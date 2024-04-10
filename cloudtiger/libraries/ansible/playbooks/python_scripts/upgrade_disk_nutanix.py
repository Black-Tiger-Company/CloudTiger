import sys
import requests
import os
import json
import base64

nutanix_user = os.environ.get('TF_VAR_nutanix_user')
nutanix_password = os.environ.get('TF_VAR_nutanix_password')
nutanix_endpoint = os.environ.get('TF_VAR_nutanix_endpoint')
nutanix_port = os.environ.get('TF_VAR_nutanix_port')
nutanix_insecure = os.environ.get('TF_VAR_nutanix_insecure')

def upgrade_vm_disk(vm_name, new_disk_size_gb):
    # Nutanix Prism Central API endpoint
    protocol = "https"
    if nutanix_insecure.lower() == "true":
        protocol = "http"
    api_url = f"{protocol}://{nutanix_endpoint}:{nutanix_port}/api/nutanix/v3/vms"

    token = base64.b64encode(f"{nutanix_user}:{nutanix_password}".encode('utf-8')).decode('utf-8')

    # Get VM UUID by name
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {token}"
    }

    request_body = {
        "kind": "vm",
        "length": 5,  # Adjust as needed
        "filter": f"vm_name=={vm_name}"
    }

    response = requests.post(api_url + "/list", json=request_body, headers=headers, verify=False)
    vm_uuid = None
    if response.status_code == 200:
        vm_list = response.json()['entities']
        if len(vm_list) == 1:  # Ensure only one VM is found with the specified name
            vm_uuid = vm_list[0]['metadata']['uuid']
        else:
            print(f"Found multiple VMs with name '{vm_name}'. Please provide a unique VM name.")
            return
    else:
        print("Failed to retrieve VM list. Status code:", response.status_code)
        print("Response:", response.text)
        exit(1)
    
    # retrieve vm conf
    vm_info = requests.get(api_url + f"/{vm_uuid}", headers=headers, verify=False)
    if vm_info.status_code == 200:
        resp = vm_info.json()
        del resp['status']
        resp['spec']['resources']['disk_list'][0]['disk_size_mib'] = int(new_disk_size_gb)*1024
    else:
        print("Get request failed", vm_info.content)
        exit(1)

    print(" Start update vm")
    vm_updated = requests.put(api_url + f"/{vm_uuid}", json=resp, headers=headers, verify=False)
    if vm_updated.status_code == 202:
        resp = vm_updated.json()
        print("Root partition extended to: {} GB".format(resp['spec']['resources']['disk_list'][0]['disk_size_mib']/1024))
    else:
        print("Put request failed", vm_updated)
        exit(1)

if __name__ == "__main__":
    vm_name = sys.argv[1]  # Get VM name from command line argument
    new_disk_size_gb = int(sys.argv[2])  # Get new disk size from command line argument
    upgrade_vm_disk(vm_name, new_disk_size_gb)
