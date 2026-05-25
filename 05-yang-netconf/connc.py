"""
Connect to Cisco IOS-XE via NETCONF and print a 'show ip int brief'-like view.

This uses standard YANG models:
  - ietf-interfaces (RFC 8343)
  - ietf-ip (RFC 8344)

IOS-XE generally supports these, but exact support varies by release/platform.
If your device doesn't return IP addresses via ietf-ip, switch to a native IOS-XE
operational model (e.g., Cisco-IOS-XE-interfaces-oper) and adjust the filter.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Iterable, Optional

import xmltodict
from ncclient import manager


@dataclass(frozen=True)
class IntBriefRow:
    name: str
    ip: str
    admin_status: str
    oper_status: str


def _env_default(*names: str) -> Optional[str]:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return None


def build_filter_interfaces_state() -> str:
    """
    NETCONF subtree filter for interfaces-state + IPv4 addresses.

    Note: `ietf-interfaces` defines `interfaces-state` (operational).
    `ietf-ip` augments interface data with `ipv4/address` in many implementations.
    """
    return """
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" type="subtree">
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name/>
          <admin-status/>
          <oper-status/>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip/>
            </address>
          </ipv4>
        </interface>
      </interfaces-state>
    </filter>
    """.strip()


def parse_interfaces_state(xml_reply: str) -> list[IntBriefRow]:
    """
    Parse ncclient <rpc-reply> XML into rows.

    Keeps it resilient to "single object vs list" shapes.
    """
    doc = xmltodict.parse(xml_reply)

    # Expected shape:
    # rpc-reply -> data -> interfaces-state -> interface -> (list)
    data = (
        doc.get("rpc-reply", {})
        .get("data", {})
        .get("interfaces-state", {})
    )
    if not data:
        return []

    interfaces = data.get("interface", [])
    if isinstance(interfaces, dict):
        interfaces = [interfaces]

    rows: list[IntBriefRow] = []
    for intf in interfaces:
        name = str(intf.get("name", "") or "")
        admin = str(intf.get("admin-status", "") or "")
        oper = str(intf.get("oper-status", "") or "")

        ip = "unassigned"
        ipv4 = intf.get("ipv4")
        if isinstance(ipv4, dict):
            addr = ipv4.get("address")
            if isinstance(addr, dict):
                ip_val = addr.get("ip")
                if ip_val:
                    ip = str(ip_val)
            elif isinstance(addr, list):
                # Take the first address if multiple exist
                for a in addr:
                    if isinstance(a, dict) and a.get("ip"):
                        ip = str(a["ip"])
                        break

        if name:
            rows.append(IntBriefRow(name=name, ip=ip, admin_status=admin, oper_status=oper))

    # Sort for stable output (GigabitEthernet..., Loopback..., etc.)
    rows.sort(key=lambda r: r.name)
    return rows


def format_table(rows: Iterable[IntBriefRow]) -> str:
    rows = list(rows)
    if not rows:
        return "No interface operational data returned."

    headers = ["Interface", "IP-Address", "Admin", "Oper"]
    data = [[r.name, r.ip, r.admin_status, r.oper_status] for r in rows]

    widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt(row: list[str]) -> str:
        return "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))

    out = [fmt(headers), fmt(["-" * w for w in widths])]
    out.extend(fmt(r) for r in data)
    return "\n".join(out)


def cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description="NETCONF 'show ip int brief'-like output from IOS-XE (ietf-interfaces/ietf-ip)."
    )
    p.add_argument("--host", default=_env_default("NETCONF_HOST", "IOSXE_HOST"), required=False)
    p.add_argument("--port", type=int, default=int(_env_default("NETCONF_PORT") or 830))
    p.add_argument("--username", default=_env_default("NETCONF_USERNAME", "IOSXE_USERNAME"), required=False)
    p.add_argument("--password", default=_env_default("NETCONF_PASSWORD", "IOSXE_PASSWORD"), required=False)
    p.add_argument(
        "--device-params",
        default="csr",
        help="ncclient device_params name (often 'csr' for IOS-XE/CSR1000v).",
    )
    p.add_argument(
        "--source",
        default="running",
        help="Datastore for <get-config>. Not used when --operational is set.",
    )
    p.add_argument(
        "--operational",
        action="store_true",
        help="Use <get> (operational/state). Recommended for interfaces-state.",
    )
    args = p.parse_args(argv)

    missing = [k for k in ("host", "username", "password") if not getattr(args, k)]
    if missing:
        p.error(f"Missing required arguments/env: {', '.join(missing)}")

    netconf_filter = build_filter_interfaces_state()

    with manager.connect(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        hostkey_verify=False,
        device_params={"name": args.device_params},
        allow_agent=False,
        look_for_keys=False,
        timeout=30,
    ) as m:
        if args.operational:
            reply = m.get(filter=netconf_filter)
        else:
            # interfaces-state is operational; some platforms may still return it via <get-config>,
            # but most will not. Keeping this for quick experimentation.
            reply = m.get_config(source=args.source, filter=netconf_filter)

    rows = parse_interfaces_state(reply.xml)
    print(format_table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(sys.argv[1:]))
