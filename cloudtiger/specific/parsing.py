import collections.abc

FORTI_PARAMS_ARRAY = {
    'firewall addrgrp': ['member'],
    'local in policy': ['srcaddr', 'dstaddr', 'service'],
    'firewall policy': ['srcaddr', 'dstaddr', 'srcintf', 'dstintf', 'service'],
    'firewall service group': ['member']
}

class FortiNetworking():
    """
    A class to extract data from a Fortinet configuration.

    Attributes
    ----------
    None

    Methods
    -------
    get_cloudtiger_format(self, resource_name, resource)
        extract data at CloudTiger format
    clean_data(key, data, array_params = [])
        reformat data if needed
    """

    def get_cloudtiger_format(self, resource_name, resource):
        resourceBTFormat = {}
        if resource_name in [
                            'firewall addrgrp',
                            'firewall address',
                            'firewall local_in_policy',
                            'firewall policy',
                            'firewall service group',
                            'firewall vip',
                            'system interface',
                            'firewall service',
                            'user group',
                            'user ldap',
                            'user local',
                            'vpn ipsec phase1',
                            'vpn ipsec phase1-interface',
                            'vpn ipsec phase2',
                            'vpn ipsec phase2-interface',
                            'vpn ssl settings'
                            ]:
            array_params = [] if resource_name not in FORTI_PARAMS_ARRAY.keys() else FORTI_PARAMS_ARRAY[resource_name]
            try:
                for resource_key, resource_property in resource.items():
                    # configuration: system interface, ...
                    if isinstance(resource_property, str) or isinstance(resource_property, collections.abc.Sequence):
                        resourceBTFormat[resource_key] = clean_data(resource_key, property)
                    else: # list of configuration: firewall policy, firewall addrgrp ...
                        resourceBTFormat[resource_key] = {
                            key: clean_data(key, property, array_params)
                            for key, property in resource_property.items() if isinstance(key, str)
                        }
            except Exception as e:
                print(e)
        return resourceBTFormat   

def clean_data(key, data, array_params = []):
    try:
        if isinstance(data, str):
            return data
        elif isinstance(data, collections.abc.Sequence):
            if key in array_params:
                return data
            else:
                return " ".join(data)
        else:
            return None
    except Exception as e:
        print('Error in clean_data')
