""" Admin operations for CloudTiger """
from audioop import add
from copy import copy
from operator import truediv
from xml.dom.domreg import registered
import yaml
import os
import copy
import sys
import dns
from dns.resolver import Resolver
from dns.resolver import NXDOMAIN
from cloudtiger.specific.nutanix import get_vms_list_per_vlan
from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import bash_action

def gather(operation: Operation):

    """ this function collect data from all child config.yml files of a folder
    into the companion _meta folder

    :param operation: Operation, the current Operation
    """

    # we loop through the config folder
    operation.logger.info("Collecting all information from configs")
    meta_addresses = operation.addresses_info
    meta_networks = operation.network_info
    meta_metadata = operation.metadata_info
    for (root, _, files) in os.walk(os.path.join(operation.scope_config_folder, "..")):

        operation.logger.info(f"Checking folder {root}")

        # collecting data from networks & vms
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
            # collecting data from network
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

            # collecting data from vms metadata
            for network_provider, network_provider_content in subconfig_data.get('vm', {}).items():
                if not isinstance(network_provider_content, dict):
                    network_provider_content = {}
                if 'vm_metadata' not in meta_metadata.keys():
                    meta_metadata['vm_metadata'] = {}
                for network_name, network in network_provider_content.items():
                    if network_name not in meta_metadata['vm_metadata'].keys():
                        meta_metadata['vm_metadata'][network_name] = {}
                    for vm_name, vm in network.items():
                        add_vm = True
                        if operation.check_existence :
                            if vm_name not in operation.existing_vms_info.get('vm_ips', {}).get(network_name, {}).get('addresses', {}).keys():
                                add_vm = False
                        if add_vm:
                            meta_metadata['vm_metadata'][network_name][vm_name] = infer_metadata(operation, vm, vm_name)

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
            if type(subconfig_data) is dict:
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

    operation.dump_meta_info(meta_addresses, meta_networks, meta_metadata)

def monitoring(operation: Operation):

    """ this function creates all Grafana configuration files per customer
    from the all_metadata.yml file """

    # loading existing metadata
    timestamp = operation.timestamp

    if timestamp != "":
        timestamp = "_" +  timestamp

    metadata_info_file = os.path.join(operation.datacenter_meta_folder, 'all_metadata' + timestamp + '.yml')
    if not os.path.isfile(metadata_info_file):
        operation.logger.error("The metadata file %s does not exist, exiting" % metadata_info_file)
        sys.exit()

    meta_metadata = {}
    with open(metadata_info_file, "r") as f:
        meta_metadata = yaml.load(f, Loader=yaml.FullLoader)

    operation.dump_monitoring_info(meta_metadata)

def dns(operation: Operation):

    """ this function check if all VMs listed in the meta folder have a
    DNS record

    :param operation: Operation, the current Operation
    """

    if operation.meta_scope:
        scope_addresses_info = operation.addresses_info
    else:
        operation.load_ips()
        scope_addresses_info = operation.scope_config_ips

    valid_dns = copy.deepcopy(scope_addresses_info)
    invalid_address = copy.deepcopy(scope_addresses_info)
    no_address = copy.deepcopy(scope_addresses_info)

    resolver = Resolver()

    for subnet_name, subnet_vms in scope_addresses_info['vm_ips'].items():
        for vm_name, vm_ip in subnet_vms["addresses"].items():
            operation.logger.info("Checking VM DNS %s.%s" % (vm_name, operation.domain))

            try:
                addresses = resolver.query(qname=f"{vm_name}.{operation.domain}", raise_on_no_answer=False).rrset
            except NXDOMAIN as no_dns_entry:
                addresses = []

            if len(addresses) == 0:
                # the VM has no DNS record
                valid_dns['vm_ips'][subnet_name]["addresses"].pop(vm_name)
                invalid_address['vm_ips'][subnet_name]["addresses"].pop(vm_name)
            else:
                # the VM has at least one DNS record
                address = addresses[0].to_text().split(' ')[-1]
                operation.logger.info("Found address %s" % address)
                if address == vm_ip:
                    # correct address
                    invalid_address['vm_ips'][subnet_name]["addresses"].pop(vm_name)
                    no_address['vm_ips'][subnet_name]["addresses"].pop(vm_name)
                else:
                    # different address than registered
                    valid_dns['vm_ips'][subnet_name]["addresses"].pop(vm_name)
                    no_address['vm_ips'][subnet_name]["addresses"].pop(vm_name)

        if len(valid_dns['vm_ips'][subnet_name]["addresses"].keys()) == 0:
            valid_dns['vm_ips'][subnet_name].pop("addresses")
        if len(invalid_address['vm_ips'][subnet_name]["addresses"].keys()) == 0:
            invalid_address['vm_ips'][subnet_name].pop("addresses")
        if len(no_address['vm_ips'][subnet_name]["addresses"].keys()) == 0:
            no_address['vm_ips'][subnet_name].pop("addresses")
        # break

    # dumping results
    valid_dns_file = os.path.join(operation.scope_config_folder, "valid_dns.yml")
    invalid_address_file = os.path.join(operation.scope_config_folder, "invalid_address.yml")
    no_address_file = os.path.join(operation.scope_config_folder, "no_address.yml")

    with open(valid_dns_file, "w") as f:
        yaml.dump(valid_dns, f)
    with open(invalid_address_file, "w") as f:
        yaml.dump(invalid_address, f)
    with open(no_address_file, "w") as f:
        yaml.dump(no_address, f)

def vms(operation: Operation):

    """ this function list all VMs from virtualizer and compare with 
    meta folder

    :param operation: Operation, the current Operation
    """

    if operation.provider == "nutanix":
        get_vms_list_per_vlan(operation)

def infer_metadata(operation: Operation, vm: dict, vm_name: str):

    """ this function infers the metadata of a VM from its other data """

    vm_metadata = vm.get("metadata", {})
    
    # infer vm type
    vm_type = "custom"
    if "vm_type" in vm_metadata.keys():
        vm_type = vm_metadata["vm_type"]
    else:
        type_not_found = True
        for standard_type in operation.standard_config.get("list_vm_types", []):
            if ('-' + standard_type) in vm_name or (standard_type + '-') in vm_name:
                vm_type = standard_type
                type_not_found = False
                break
        
        vm_types_aliases = operation.standard_config.get("vm_types_aliases", {})
        if type_not_found:
            for standard_type_origin, standard_type_alias_list in vm_types_aliases.items():
                for standard_type_alias in standard_type_alias_list.split(','):
                    if ('-' + standard_type_alias) in vm_name or (standard_type_alias + '-') in vm_name or (standard_type_alias == vm_name):
                        vm_type = standard_type_origin
                        break

    operation.logger.info("Infered type from VM name %s : %s" % (vm_name, vm_type))

    standard_metadata = operation.standard_config.get("vm_metadata", {}).get(vm_type, {})

    # infer high availability sizing
    vm_provider = operation.provider
    if vm_provider not in operation.standard_config.get("vm_types", {}).keys():
        vm_provider = "default"
    standard_sizing = operation.standard_config.get("vm_types", {}).get(vm_provider, {}).get(vm_type, {})

    # infer services
    vm_services = [
        svc for svc, types in operation.standard_config.get("services", {}).items() if (vm_type in types.split(',') or "all" in types.split(','))
    ]

    # infer customer
    infered_customer = vm_name.split('-')[-1]
    customer = "none"
    for listed_customer in operation.standard_config.get("customers", []):
        if infered_customer == listed_customer or (infered_customer in operation.standard_config.get("customers_aliases", {}).get(listed_customer, "").split(",")):
            customer = listed_customer
            break

    # infer environment
    infered_color = vm_name.split('-')[0]
    infered_color = operation.standard_config.get("color_aliases", {}).get(infered_color, infered_color)
    color = operation.standard_config.get("color_aliases", {}).get(infered_color, "none")
    # color = "none"
    environment = "internal"
    customer_environments = operation.standard_config.get("environment_status", {}).get(customer, {})
    for env, col in customer_environments.items():
        if infered_color == col:
            color = infered_color
            environment = env

    # infer sizing
    high_sizing = {
        "cpu": standard_sizing.get("prod", {}).get("nb_vcpu_per_socket", 1) * standard_sizing.get("prod", {}).get("nb_sockets", 1),
        "memory": standard_sizing.get("prod", {}).get("memory", 1024),
        "data": standard_sizing.get("prod", {}).get("data_volume_size", 20)
    }
    medium_sizing = {
        "cpu": vm.get("size", {}).get("nb_vcpu_per_socket", 1) * vm.get("size", {}).get("nb_sockets", 1),
        "memory": vm.get("size", {}).get("memory", 1024),
        "data": vm.get("data_volume_size", 20)
    }
    low_sizing = {
        "cpu": standard_sizing.get("nonprod", {}).get("nb_vcpu_per_socket", 1) * standard_sizing.get("nonprod", {}).get("nb_sockets", 1),
        "memory": standard_sizing.get("nonprod", {}).get("memory", 1024),
        "data": standard_sizing.get("nonprod", {}).get("data_volume_size", 20)
    }

    for value in ["cpu", "memory", "data"]:
        if high_sizing[value] < medium_sizing[value]:
            high_sizing[value] = medium_sizing[value]

    if vm_type == "custom":
        high_sizing = copy.deepcopy(medium_sizing)

    # set metadata
    updated_metadata = {
        "vm_type": vm_metadata.get("vm_type", vm_type),
        "services": vm_metadata.get("services", vm_services),
        "maintenance_time_slot": vm_metadata.get("maintenance_time_slot", standard_metadata["maintenance_time_slot"]),
        "high_availability_sizing": vm_metadata.get("high_availability_sizing",
            dict({
                "high": high_sizing,
                "medium": medium_sizing,
                "low": low_sizing
            })
        ),
        "exposition": vm_metadata.get("exposition", standard_metadata["exposition"]),
        "criticity": vm_metadata.get("criticity", standard_metadata["criticity"]),
        "data": vm_metadata.get("data", standard_metadata["data"]),
        "owner": vm_metadata.get("owner", standard_metadata["owner"]),
        "customer": customer,
        "environment": environment,
        "color": color,
        "comment": vm_metadata.get("comment", "no comment"),
    }

    # if VM is not internal or prod, criticity cannot be high
    if updated_metadata["criticity"] == "high":
        if environment not in ["prod", "internal"]:
            updated_metadata["criticity"] = "medium"

    return updated_metadata