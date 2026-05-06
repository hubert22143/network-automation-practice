#pyyaml lib

import yaml

with open('r1.yaml') as file:
    data = yaml.safe_load(file)

print(data)