""" Admin operations for CloudTiger """
import yaml
import os

from cloudtiger.cloudtiger import Operation

def gather(operation: Operation):

    """ this function collect data from all child config.yml files of a folder
    into the companion _meta folder

    :param operation: Operation, the current Operation
    """

    operation.logger.info("Loading current meta information")
    operation.load_meta_info()

    # we loop through the config folder
    operation.logger.info("Collecting all information from configs")
    meta_addresses = operation.addresses_info
    meta_networks = operation.network_info
    for (root, _, files) in os.walk(operation.scope_config_folder):
        
        operation.logger.info(f"Checking folder {root}")

        # collecting data from networks
        if 'config.yml' in files:
            subconfig_path = os.path.join(root, 'config.yml')
            subconfig_scope = (subconfig_path.split(os.sep)\
                [len(operation.scope_config_folder.split(os.sep)):-1])
            if subconfig_scope == []:
                subconfig_scope = ""
            else :
                subconfig_scope = os.path.join(*(subconfig_scope))
            operation.logger.info(f"Collecting config {subconfig_scope}")
            with open(subconfig_path, 'r') as f:
                try:
                    subconfig_data = yaml.load(f, Loader=yaml.FullLoader)
                except Exception as e:
                    operation.logger.error(
                        "Failed to open file % with error %s".format(subconfig_path, e))
            for network_provider, network_provider_content in subconfig_data.get('network', {}).items():
                if not isinstance(meta_networks, dict):
                    meta_networks = {}
                if network_provider not in meta_networks.keys():
                    meta_networks[network_provider] = {"subnets": {}}
                if 'subnets' not in meta_networks[network_provider].keys():
                    meta_networks[network_provider]['subnets'] = {}
                for network_name, network in network_provider_content.get('subnets', {}).items():
                    # we manage collisions
                    if network_name in meta_networks.get(network_provider, {}).get("subnets", {}).keys():
                        if network != meta_networks[network_provider]['subnets'][network_name]:
                            meta_networks[network_provider]['subnets'][network_name + "_previous"] = meta_networks[network_provider]['subnets'].pop(network_name)
                            meta_networks[network_provider]['subnets'][network_name + "_" + subconfig_scope] = network
                    else:
                        meta_networks[network_provider]['subnets'][network_name] = network

        if 'config_ips.yml' in files:

            # collecting data from addresses
            subconfig_path = os.path.join(root, 'config_ips.yml')
            subconfig_scope = (subconfig_path.split(os.sep)\
                [len(operation.scope_config_folder.split(os.sep)):-1])
            if subconfig_scope == []:
                subconfig_scope = ""
            else :
                subconfig_scope = os.path.join(*(subconfig_scope))
            operation.logger.info(f"Collecting config addresses {subconfig_scope}")
            with open(subconfig_path, 'r') as f:
                try:
                    subconfig_data = yaml.load(f, Loader=yaml.FullLoader)
                except Exception as e:
                    operation.logger.error(
                        "Failed to open file % with error %s".format(subconfig_path, e))
            for network_provider, network_provider_content in subconfig_data.items():
                if not isinstance(network_provider_content, dict):
                    network_provider_content = {}
                if 'vm_ips' not in meta_addresses.keys():
                    meta_addresses['vm_ips'] = {}
                # if network_name not in meta_addresses[network_provider].keys():
                #     meta_addresses[network_provider][network_name] = {"addresses": {}}
                for network_name, network in network_provider_content.items():
                    if network_name not in meta_addresses['vm_ips'].keys():
                        meta_addresses['vm_ips'][network_name] = {'addresses': {}}
                    for vm_name, vm_full_address in network.get('addresses', {}).items():
                        # we manage collisions
                        if vm_name in meta_addresses.get('vm_ips', {}).get(network_name, {}).get("addresses", {}).keys():
                            # we remove any potential SSH port at the end of the IP address
                            previous_full_address = meta_addresses['vm_ips'][network_name]['addresses'][vm_name]
                            previous_ip = previous_full_address.split(':')[0]
                            vm_ip = vm_full_address.split(':')[0]

                            # if we have different IPs AND none of the two different IPs are 
                            # "0.0.0.0" or '' (meaning very probably a shutdown machine),
                            # then we provide two different entries, a 'before' and an 'after'
                            if previous_ip not in ["", "0.0.0.0"] and vm_ip not in ["", "0.0.0.0"]:
                                if vm_ip != previous_ip:
                                    meta_addresses['vm_ips'][network_name]['addresses'][vm_name + "_previous"] = previous_full_address
                                    meta_addresses['vm_ips'][network_name]['addresses'].pop(vm_name)
                                    meta_addresses['vm_ips'][network_name]['addresses'][vm_name + "_" + subconfig_scope] = vm_full_address
                        else :
                            meta_addresses['vm_ips'][network_name]['addresses'][vm_name] = vm_full_address
                            
    operation.dump_meta_info(meta_addresses, meta_networks)