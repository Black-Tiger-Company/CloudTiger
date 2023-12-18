import base64
import json
import sys
import os
import yaml

import requests
from requests.exceptions import ConnectionError

from cloudtiger.cloudtiger import Operation

def get_vms_list_per_vlan_vsphere(operation: Operation):

    """ this function calls the nutanix API to get all the VMs inside a VLAN """

    # small manipulation to have vsphere credentials indepently of the main provider
    vsphere_secret = {
        "endpoint" : operation.provider_secret.get("TF_VAR_vsphere_url", os.environ.get("TF_VAR_vsphere_url", "vsphere_url")),
        "username" : operation.provider_secret.get("TF_VAR_vsphere_user", os.environ.get("TF_VAR_vsphere_user", "vsphere_user")),
        "password" : operation.provider_secret.get("TF_VAR_vsphere_password", os.environ.get("TF_VAR_vsphere_password", "vsphere_password")),
    }

    url = format("https://%s/api/session" % (vsphere_secret["endpoint"]))

    vsphere_auth = base64.b64encode((vsphere_secret["username"] + ':' + vsphere_secret["password"]).encode('ascii')).decode('ascii')

    headers = {
            "Authorization" : "Basic " + vsphere_auth,
        }

    response = requests.post(url, headers=headers, verify=False)

    session_token = "session_token"
    if response.status_code in [200, 201]:
        # Authentication successful, get the session token
        session_token = response.json()
        operation.logger.debug(f"Session Token: {session_token}")
    else:
        operation.logger.error(f"Authentication failed. Status Code: {response.status_code}")
        sys.exit()

    # Add the session token to the headers
    headers = {
        'vmware-api-session-id': session_token
    }

    vm_list_url = format("https://%s/api/vcenter/vm" % (vsphere_secret["endpoint"]))
    response = requests.get(vm_list_url, headers=headers, verify=False)

    # print(response.json())
    vms_data = response.json()

    vm_names = [{"name":vm['name'], "id":vm['vm']} for vm in vms_data]

    operation.logger.info("List of VMs :")
    operation.logger.info(yaml.dump(vm_names))

    all_vms_per_vlan = {}

    # list subnets to inspect
    requested_subnets = operation.scope_config_dict.get("vm", {}).get("vsphere_network").keys()

    for vm in vm_names:
        # we filter vSphere Cluster Service VM
        if "vCLS" not in vm["name"]:
            operation.logger.debug("Examining data from VM %s" % (vm["name"]))
            vm_detail_url = format("https://%s/api/vcenter/vm/%s" % (vsphere_secret["endpoint"], vm['id']))
            vm_network_url = format("https://%s/api/vcenter/vm/%s/guest/networking/interfaces" % (vsphere_secret["endpoint"], vm['id']))
            headers = {
                'vmware-api-session-id': session_token
            }
            vm_data = {}
            # Define the maximum number of retry attempts
            max_retry_attempts = 20

            # Initialize a counter for retries
            retry_count = 0
            while retry_count < max_retry_attempts:
                try:
                    response = requests.get(vm_detail_url, headers=headers, verify=False)
                    vm_data = response.json()

                    break

                except ConnectionError as e:
                    operation.logger.debug(f"Connection error: {e}")
                    retry_count += 1
                    if retry_count < max_retry_attempts:
                        operation.logger.debug(f"Retrying (attempt {retry_count}/{max_retry_attempts})...")
                    else:
                        operation.logger.debug(f"Max retry attempts ({max_retry_attempts}) reached. Request failed.")
                except requests.exceptions.RequestException as e:
                    operation.logger.debug(f"Request error: {e}")
                    break  # Other request exceptions are not retried
            # print(yaml.dump(vm_data))
            # if the considered VM is not connected to the subnets we are inspecting, skip
            consider_vm = False
            for _, network_interface in vm_data.get("nics", {}).items():
                if network_interface.get("backing", {}).get("network_name", "") in requested_subnets:
                    consider_vm = True
                    break
            if consider_vm:

                # Define the maximum number of retry attempts
                max_retry_attempts = 20

                # Initialize a counter for retries
                retry_count = 0
                while retry_count < max_retry_attempts:
                    try:
                        operation.logger.info("Querying VM network interfaces")
                        response = requests.get(vm_network_url, headers=headers, verify=False)
                        vm_network_data = response.json()
                        for network_interface in vm_network_data:
                            if isinstance(network_interface, dict):
                                vlan_name = vm_data.get("nics", {}).get(network_interface.get('nic', ''), {}).get("backing", {}).get('network_name', 'no_network_identified')
                                ip_addresses = []
                                for address in network_interface.get("ip", {}).get("ip_addresses", []):
                                    ip_address = str(address.get("ip_address", "unknown_address"))
                                    if len(ip_address.split('.')) == 4:
                                        ip_addresses.append(ip_address)

                                vm_name = vm["name"]

                                all_vms_of_vlan = all_vms_per_vlan.get(vlan_name, {"addresses":{}})
                                all_vms_of_vlan['addresses'][vm_name] = ",".join(ip_addresses)
                                all_vms_per_vlan[vlan_name] = all_vms_of_vlan

                        break

                    except ConnectionError as e:
                        operation.logger.debug(f"Connection error: {e}")
                        retry_count += 1
                        if retry_count < max_retry_attempts:
                            operation.logger.debug(f"Retrying (attempt {retry_count}/{max_retry_attempts})...")
                        else:
                            operation.logger.debug(f"Max retry attempts ({max_retry_attempts}) reached. Request failed.")
                    except requests.exceptions.RequestException as e:
                        operation.logger.debug(f"Request error: {e}")
                        break  # Other request exceptions are not retried

    all_vms_per_vlan = {"vm_ips": all_vms_per_vlan}

    operation.logger.info(yaml.dump(all_vms_per_vlan))

    return all_vms_per_vlan
