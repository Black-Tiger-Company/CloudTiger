import yaml
from schema_validation_pydantic import Blacktiger
from pydantic import ValidationError

# CERBERUS TEST
def load_doc(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exception:
            raise exception

from cerberus import Validator
print("TEST CERBERUS")
schema = eval(open('./cloudtiger/schema_validation_cerberus.py', 'r').read())
v = Validator(schema)
doc = load_doc('/mnt/c/Users/emeric.guibert/Documents/Infrastucture/gitops/config/bnc_datacenter/bnc_2i/customers/lne/config.yml')
print(v.validate(doc, schema))
if v.errors:
    print(v.errors)

print("TEST PYDANTIC")
try:
    Blacktiger(**doc)
    print("OK")
except ValidationError as e:
    print(e)


