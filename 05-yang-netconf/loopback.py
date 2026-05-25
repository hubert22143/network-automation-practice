"""
Configure Loopback2 IPv4 address on Cisco IOS-XE via NETCONF using ncclient.

Model(s):
  - ietf-interfaces (RFC 8343)
  - ietf-ip (RFC 8344)

This performs an <edit-config> to create/update Loopback2 and set:
  11.11.11.11/32
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from ncclient import manager
from ncclient.operations.rpc import RPCError


def _env_default(*names: str) -> Optional[str]:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return None


def build_loopback_edit_config(
    name: str = "Loopback2",
    ip: str = "11.11.11.11",
    prefix_len: int = 32,
) -> str:
    """
    Build an IETF YANG payload for <edit-config>.

    Notes:
    - `enabled` is admin state (true = no shutdown).
    - Setting `ipv4/address` creates/updates the address; device may allow multiple
      addresses—this payload sets one (by IP key).
    """
    return f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{name}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip}</ip>
              <prefix-length>{prefix_len}</prefix-length>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """.strip()


def _mask_from_prefix(prefix_len: int) -> str:
    if prefix_len < 0 or prefix_len > 32:
        raise ValueError("prefix_len must be between 0 and 32")
    bits = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF if prefix_len else 0
    return ".".join(str((bits >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def build_loopback_edit_config_iosxe_native(
    name: str = "Loopback2",
    ip: str = "11.11.11.11",
    prefix_len: int = 32,
) -> str:
    """
    Build a Cisco IOS-XE native YANG payload for <edit-config>.

    YANG: Cisco-IOS-XE-native
    Path: native/interface/Loopback[name]/ip/address/primary/{address,mask}
    """
    # IOS-XE expects the Loopback interface index (e.g. "2") under <name> when using native model.
    idx = name.replace("Loopback", "")
    if not idx.isdigit():
        raise ValueError("For Cisco native model, name should look like 'Loopback2'.")

    mask = _mask_from_prefix(prefix_len)
    return f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>{idx}</name>
            <ip>
              <address>
                <primary>
                  <address>{ip}</address>
                  <mask>{mask}</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
        </interface>
      </native>
    </config>
    """.strip()


def build_loopback_get_filter(name: str = "Loopback2") -> str:
    return f"""
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" type="subtree">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{name}</name>
          <enabled/>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip/>
              <prefix-length/>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </filter>
    """.strip()


def cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Set Loopback2 to 11.11.11.11/32 via NETCONF (ncclient).")
    p.add_argument("--host", default=_env_default("NETCONF_HOST", "IOSXE_HOST"), required=False)
    p.add_argument("--port", type=int, default=int(_env_default("NETCONF_PORT") or 830))
    p.add_argument("--username", default=_env_default("NETCONF_USERNAME", "IOSXE_USERNAME"), required=False)
    p.add_argument("--password", default=_env_default("NETCONF_PASSWORD", "IOSXE_PASSWORD"), required=False)
    p.add_argument("--device-params", default="csr", help="ncclient device_params name (often 'csr' for IOS-XE).")
    p.add_argument("--target", default="running", choices=["running", "candidate"], help="edit-config target datastore.")
    p.add_argument("--commit", action="store_true", help="If using candidate, commit after edit-config.")
    p.add_argument(
        "--model",
        default="auto",
        choices=["auto", "ietf", "iosxe-native"],
        help="Which YANG model payload to use. 'auto' tries IETF then falls back to IOS-XE native.",
    )
    p.add_argument("--name", default="Loopback2", help="Interface name (default: Loopback2).")
    p.add_argument("--ip", default="11.11.11.11", help="IPv4 address (default: 11.11.11.11).")
    p.add_argument("--prefix-len", type=int, default=32, help="IPv4 prefix length (default: 32).")
    p.add_argument("--verify", action="store_true", help="Read back config after change.")
    # Compatibility with the earlier "show" script: accepted but ignored here.
    p.add_argument("--operational", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args(argv)

    missing = [k for k in ("host", "username", "password") if not getattr(args, k)]
    if missing:
        p.error(f"Missing required arguments/env: {', '.join(missing)}")

    ietf_payload = build_loopback_edit_config(name=args.name, ip=args.ip, prefix_len=args.prefix_len)
    native_payload = build_loopback_edit_config_iosxe_native(name=args.name, ip=args.ip, prefix_len=args.prefix_len)

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
        payload_used = None
        try:
            if args.model in ("ietf", "auto"):
                m.edit_config(target=args.target, config=ietf_payload)
                payload_used = "ietf"
            else:
                raise RPCError("Skipping IETF payload (model=iosxe-native).")
        except RPCError as e:
            # IOS-XE commonly throws "Runtime mapping error" when the platform doesn't map
            # ietf-ip config to native CLI. Fall back to Cisco-IOS-XE-native.
            if args.model == "ietf":
                raise
            m.edit_config(target=args.target, config=native_payload)
            payload_used = "iosxe-native"

        if args.target == "candidate" and args.commit:
            m.commit()

        if args.verify:
            flt = build_loopback_get_filter(name=args.name)
            # Config lives in running/candidate, so use get-config.
            reply = m.get_config(source="running", filter=flt)
            print(reply.xml)

    model_str = payload_used or args.model
    print(f"Configured {args.name} to {args.ip}/{args.prefix_len} (model={model_str})")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(sys.argv[1:]))
