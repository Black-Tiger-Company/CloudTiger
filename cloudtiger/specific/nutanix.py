import base64
import json
import sys
import os
import yaml

import requests

from cloudtiger.cloudtiger import Operation


def get_vm_nutanix_uuid(operation: Operation, vm_name):

    """ this function calls the nutanix API to get the uuid of a VM """
    url = format("https://%s:9440/api/nutanix/v3/%s/list" % (operation.provider_secret.get("TF_VAR_nutanix_endpoint", "nutanix_endpoint"), "vms"))

    nutanix_auth = base64.b64encode((operation.provider_secret.get("TF_VAR_nutanix_user", "missing_user") + ':' + operation.provider_secret.get("TF_VAR_nutanix_password", "missing_password")).encode('ascii')).decode('ascii')

    headers = {
            "Authorization" : "Basic " + nutanix_auth,
            "Content-type": "application/json",
            "Accept": "application/json"
        }

    payload = format('{"kind":"vm","length":1,"offset":0,"filter":"vm_name==%s"}' % vm_name)

    operation.logger.info("API query %s with payload %s" % (url, payload))

    r = requests.post(url, headers=headers, data=payload)

    content = json.loads(r.content)

    # operation.logger.info(content)

    if len(content['entities']) == 0 :
        operation.logger.error("Warning : the VM %s has not been found on the Nutanix cluster" % vm_name)
        sys.exit()

    uuid = content["entities"][0]["metadata"]["uuid"]

    return uuid

def get_vms_list_per_vlan(operation: Operation):

    """ this function calls the nutanix API to get all the VMs inside a VLAN """
    url = format("https://%s:9440/api/nutanix/v3/%s/list" % (operation.provider_secret.get("TF_VAR_nutanix_endpoint", "nutanix_endpoint"), "vms"))

    nutanix_auth = base64.b64encode((operation.provider_secret.get("TF_VAR_nutanix_user", "missing_user") + ':' + operation.provider_secret.get("TF_VAR_nutanix_password", "missing_password")).encode('ascii')).decode('ascii')

    headers = {
            "Authorization" : "Basic " + nutanix_auth,
            "Content-type": "application/json",
            "Accept": "application/json"
        }

    pagination = 50
    offset = 0
    content = {"entities":["dummy"]}
    all_entities =  []

    while len(content["entities"]) > 0:
        payload = format('{"kind":"vm","length":%s,"offset":%s}' % (pagination, offset))

        operation.logger.info("API query %s with payload %s" % (url, payload))

        r = requests.post(url, headers=headers, data=payload)

        content = json.loads(r.content)

        all_entities += content.get("entities", [])

        offset += pagination

    all_vms_per_vlan = {}

    # we parse the VM dump to get a mapping of VLAN -> (vm_name, vm_ip)
    for vm in all_entities:
        vm_name = vm.get('spec', {}).get('name', "no_name")
        vlan_name = "NO VLAN"
        first_ip = "not_available"
        network_interface_list = vm.get('spec', {}).get('resources', {}).get('nic_list', [])
        if len(network_interface_list) > 0:
            vlan_name = network_interface_list[0].get("subnet_reference", {}).get("name", "NO VLAN")
            ip_list = network_interface_list[0].get("ip_endpoint_list", [])
            if len(ip_list) > 0:
                first_ip = ip_list[0].get("ip", "not_available")
        all_vms_of_vlan = all_vms_per_vlan.get(vlan_name, {"addresses":{}})
        all_vms_of_vlan['addresses'][vm_name] = first_ip
        all_vms_per_vlan[vlan_name] = all_vms_of_vlan

    # dumping results
    all_vms_per_vlan = {"vm_ips": all_vms_per_vlan}
    all_existing_vms = os.path.join(operation.scope_config_folder, "all_existing_vms.yml")

    with open(all_existing_vms, "w") as f:
        yaml.dump(all_vms_per_vlan, f)

    return all_entities