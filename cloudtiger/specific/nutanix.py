import base64
import json
import sys

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
