""" Initial operations needed for CloudTiger """
import json
import os
import shutil
import subprocess
import sys
import base64
import ipaddress

import netaddr
import yaml
import requests

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
# from InquirerPy.base.control import Choice
# from InquirerPy.separator import Separator
# from InquirerPy.validator import NumberValidator, EmptyInputValidator, PathValidator
# from colored import Fore, Back, Style

import re

from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import load_yaml, j2, create_ssh_keys, merge_dictionaries, read_user_choice, get_credentials
from cloudtiger.data import available_infra_services, terraform_vm_resource_name, provider_secrets_helper, environment_name_mapping, custom_ssh_port_per_vm_type
from cloudtiger.specific.nutanix import get_vms_list_per_vlan_nutanix
from cloudtiger.specific.vsphere import get_vms_list_per_vlan_vsphere
from cloudtiger.specific.dns import *

def config_gitops(operation: Operation):

    """ this function executes the initial configuration of a CloudTiger project folder

    :param operation: Operation, the current Operation
    """

    # root .env file

    root_dotenv = {}

    dotenv_configuration_prompt = """
Let us configure some parameters for your CloudTiger project folder."""
    print(dotenv_configuration_prompt)

    get_credentials(
        operation.logger,
        operation.libraries_path,
        operation.project_root,
        provider_secrets_helper["root"],
        operation.scope
    )


    # .env file per cloud provider

    provider_dotenv_configuration_prompt = """
Now, let us configure credentials for your chosen cloud provider."""
    print(provider_dotenv_configuration_prompt)

    chosen_providers = inquirer.checkbox(
        message = "Select cloud providers",
        choices = terraform_vm_resource_name.keys(),
        default = None
    ).execute()

    for chosen_provider in chosen_providers:
        provider_secret_path = os.path.join(operation.project_root, "secrets", chosen_provider)
        get_credentials(
            operation.logger,
            operation.libraries_path,
            provider_secret_path,
            provider_secrets_helper[chosen_provider],
            os.path.join(operation.scope, "secrets", chosen_provider)
        )

    # check if the user wants to use a Terraform backend
    use_tf_backend = inquirer.confirm(
        message = "Do you wish to use a remote Terraform backend ? If yes, you will need to provide them beforehand",
        default = False
    ).execute()

    if use_tf_backend:
        get_credentials(operation.logger,
                        operation.libraries_path,
                        operation.project_root,
                        provider_secrets_helper["tf_backend"],
                        os.path.join(operation.scope, "secrets", chosen_provider),
                        append=True)

def folder(operation: Operation):

    """ this function creates a bootstrap project root folder ('gitops')
    for CloudTiger

    :param operation: Operation, the current Operation
    """

    os.makedirs(operation.scope, exist_ok=True)
    gitops_template = os.path.join(operation.libraries_path, "internal", "gitops")
    shutil.copytree(gitops_template, operation.scope, dirs_exist_ok=True)


def set_ssh_keys(operation: Operation):

    """ this function creates a dedicated pair of SSH keys for the scope if needed
    by the config.yml

    :param operation: Operation, the current Operation
    """

    private_ssh_folder = ""
    public_ssh_folder = ""
    ssh_key_name = ""

    # first option, dedicated ssh keys pair wanted
    if operation.scope_config_dict.get("dedicated_ssh_keys", False):
        private_ssh_folder = os.path.join(operation.project_root, "secrets", "ssh",
                                          operation.scope, "private")
        public_ssh_folder = os.path.join(operation.project_root, "secrets", "ssh",
                                         operation.scope, "public")
        ssh_key_name = operation.scope_config_dict.get("ssh_key_name", 
                                                       operation.scope.replace(os.sep, "_"))

        create_ssh_keys(operation.logger, private_ssh_folder, public_ssh_folder,
                        ssh_key_name=ssh_key_name)

    else:
        # second option, we use the CLOUDTIGER_SSH_KEY_PATH only
        if "CLOUDTIGER_PRIVATE_SSH_KEY_PATH" not in os.environ.keys():
            sys.exit("The environment variable CLOUDTIGER_PRIVATE_SSH_KEY_PATH is not set, exiting")
        private_ssh_key_path = os.environ.get("CLOUDTIGER_PRIVATE_SSH_KEY_PATH")
        private_ssh_key_path = os.path.expanduser(private_ssh_key_path)
        private_ssh_key_path = private_ssh_key_path.replace(" ", "\ ")

        if not os.path.exists(private_ssh_key_path):
            sys.exit("The provided private SSH key does not exist in this path, exiting")

        # private key already exists, we return
        operation.logger.info("The private SSH key %s does exist, going forward"
                              % private_ssh_key_path)

    return


def configure_ip(operation: Operation):

    """ this function generates the config_ips.yml file associated with the scope

    :param operation: Operation, the current Operation
    """

    # we load the IPs already set for the current scope
    operation.set_terraform_output_info()

    # listing all the subnets that need to be crawled for available IPs
    all_vms_per_vlan = {}

    # we collect IPs from existing VMs on private cloud providers
    if (operation.provider == "nutanix") or ('TF_VAR_nutanix_endpoint' in os.environ.keys()):
        all_vms_per_vlan_nutanix = get_vms_list_per_vlan_nutanix(operation)
        merge_dictionaries(all_vms_per_vlan_nutanix, all_vms_per_vlan)

    if (operation.provider == "vsphere") or ('TF_VAR_vsphere_url' in os.environ.keys()):
        all_vms_per_vlan_vsphere = get_vms_list_per_vlan_vsphere(operation)
        merge_dictionaries(all_vms_per_vlan_vsphere, all_vms_per_vlan)

    operation.logger.debug("All considered VMs per VLAN :")
    operation.logger.debug(yaml.dump(all_vms_per_vlan))

    subnets_to_crawl = {}
    for network_name, network_subnets in operation.scope_config_dict.get('vm', {}).items():
        subnets_to_crawl[network_name] = []
        for subnet_name, subnet_vms in network_subnets.items():
            for vm_name, vm in subnet_vms.items():
                has_subnet_managed_ips = operation.scope_config_dict["network"][network_name]\
                    ["subnets"][subnet_name].get("managed_ips", False)
                if has_subnet_managed_ips & ("private_ip" not in vm.keys()):
                    subnets_to_crawl[network_name].append(subnet_name)
                    break

    operation.logger.debug(f"Subnets to inspect to find available IPs {subnets_to_crawl}")

    # we 'fping' the subnets to find available IPs
    available_ips = {}
    all_available_ips = []
    for network_name, network_subnets in subnets_to_crawl.items():
        available_ips[network_name] = {}
        for subnet_name in network_subnets:
            if operation.provider in ["nutanix", "vsphere"]:
                network = ipaddress.IPv4Network(operation.scope_config_dict["network"][network_name]\
                ["subnets"][subnet_name]["cidr_block"], strict=False)
                vlan_all_ip_addresses = [str(ip) for ip in network.hosts()]
                vlan_all_ip_set_addresses = [
                    ip for vm, address in all_vms_per_vlan["vm_ips"].get(subnet_name, {}).get("addresses", {}).items() for ip in address.split(',')
                ]
                unsorted_all_available_ips = [
                    address for address in vlan_all_ip_addresses if address not in vlan_all_ip_set_addresses
                ]
                all_available_ips = sorted(unsorted_all_available_ips, key=lambda x: ipaddress.IPv4Address(x))

            else:
                command = format("fping -ugq %s" % (operation.scope_config_dict["network"][network_name]\
                    ["subnets"][subnet_name]["cidr_block"]))
                operation.logger.info("Executing command %s" % command)
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True)
                # out, err = process.communicate()
                process.wait()
                out = process.stdout.read()
                all_available_ips = out.split('\n')

            # dump available IPs for debug
            operation.logger.debug(f"Subnets to inspect to find available IPs {subnets_to_crawl}")

            # in order to avoid broadcast IPs
            all_available_ips.reverse()

            # in order to avoid gateway IP and other technical IPs
            if len(all_available_ips) > 3:
                all_available_ips.pop()
                all_available_ips.pop()
                all_available_ips.pop()
            else:
                operation.logger.info("Error : the VLAN you chose does not contain enough remaining available IPs")
                sys.exit()

            # we get the list of forbidden IPs
            forbidden_range_start = operation.scope_config_dict["network"][network_name]\
                ["subnets"][subnet_name].get("forbidden_range_start", None)
            forbidden_range_stop = operation.scope_config_dict["network"][network_name]\
                ["subnets"][subnet_name].get("forbidden_range_stop", None)
            if (forbidden_range_start is not None) & (forbidden_range_stop is not None):
                forbidden_cidr_block = netaddr.iter_iprange(forbidden_range_start,
                                                            forbidden_range_stop)
                forbiddend_addresses_pool = [str(addr) for addr in forbidden_cidr_block]
            else:
                forbiddend_addresses_pool = []
       
            available_ips[network_name][subnet_name] = [
                ip for ip in all_available_ips if ip not in forbiddend_addresses_pool
                ]

    operation.logger.debug("The list of available addresses:\n%s" % all_available_ips)

    # we update the config_ips using the available IPs for the VMs missing an attributed IP
    updated_config_ip = {
        network_name: {
            subnet_name: {
                "addresses": {
                    vm_name: vm.get("private_ip", 
                                    operation.terraform_vm_data\
                                        .get(
                                            vm_name,
                                            {"private_ip":"not_learned_yet"})["private_ip"])
                    for vm_name, vm in subnet_vms.items()
                }
            }
            for subnet_name, subnet_vms in network_subnets.items()
        }
        for network_name, network_subnets in operation.scope_config_dict.get("vm", {}).items()
    }

    for network_name, network_subnets in updated_config_ip.items():
        for subnet_name, subnet_vms in network_subnets.items():
            for vm_name, address in subnet_vms["addresses"].items():
                if address == "not_learned_yet":
                    has_subnet_managed_ips = operation.scope_config_dict["network"][network_name]\
                        ["subnets"][subnet_name].get("managed_ips", False)
                    if has_subnet_managed_ips:
                        updated_config_ip[network_name][subnet_name]["addresses"][vm_name] = \
                            available_ips[network_name][subnet_name].pop()
                    else:
                        updated_config_ip[network_name][subnet_name]["addresses"][vm_name] = \
                            "not_learned_yet"

    scope_ips = os.path.join(operation.scope_config_folder, 'config_ips.yml')
    with open(scope_ips, 'w') as f:
        yaml.dump(updated_config_ip, f)


def prepare_scope_folder(operation: Operation):

    """ this function creates the <GITOPS>/scopes/<SCOPE> folder associated
    with your scope

    :param operation: Operation, the current Operation
    """

    # create scope folder
    operation.logger.info("Creating scope folder %s" % operation.scope_folder)
    os.makedirs(operation.scope_terraform_folder, exist_ok=True)

    # copying standard terraform folder
    template_folder = os.path.join(operation.libraries_path, "internal", "terraform_providers")
    operation.logger.debug("Creating scope from terraform template folder : %s" % template_folder)
    shutil.copytree(template_folder, operation.scope_terraform_folder, dirs_exist_ok=True)

    # copying needed provider's modules into project root
    operation.logger.debug("Creating Terraform modules folder from libraries folder : %s"
                          % operation.libraries_path)
    tf_modules = os.path.join(
        operation.libraries_path, "terraform", "providers", operation.provider)
    target_modules = os.path.join(
        operation.project_root, "terraform", "providers", operation.provider)
    os.makedirs(target_modules, exist_ok=True)
    shutil.copytree(tf_modules, target_modules, dirs_exist_ok=True)

    # loading attributed IPs from config_ips.yml
    operation.load_ips()

    # setting terraform files from jinja templates
    operation.logger.debug("setting services parameters for scope %s" % operation.scope)

    for service in available_infra_services:
        if service in operation.used_services:
            j2(operation.logger, os.path.join(operation.scope_folder,
                                              "terraform", "services", service + ".tfvars.j2"),
               operation.scope_config_dict,
               os.path.join(operation.scope_folder, "terraform", "services", service + ".tfvars"))
        os.remove(os.path.join(operation.scope_folder, "terraform", "services",
                               service + ".tfvars.j2"))

    for tf_file in ["outputs.tf", "modules.tf", "provider.tf", "terraform.tfvars"]:
        tf_template_path = os.path.join(operation.scope_folder, "terraform", tf_file + ".j2")
        tf_file_path = os.path.join(operation.project_root, "scopes",
                                    operation.scope, "terraform", tf_file)
        j2(operation.logger, tf_template_path, operation.scope_config_dict, tf_file_path)
        os.remove(tf_template_path)

    for yaml_file in ["firewall_standard", "vm_standard", "disk_standard"]:
        yaml_file_path = os.path.join(operation.libraries_path, "internal", "standard",
                                      yaml_file + ".yml")
        tf_file_dest = os.path.join(operation.project_root, "scopes", operation.scope,
                                    "terraform", yaml_file + ".auto.tfvars.json")
        yaml_file_content = load_yaml(operation.logger, yaml_file_path)
        # we supercharge the vm_standard file with extra entries from
        # <GITOPS_FOLDER>/standard/standard.yml
        if yaml_file == "vm_standard":
            yaml_file_content = operation.standard_config
        with open(tf_file_dest, "w") as f:
            json.dump(yaml_file_content, f, indent=4)

    operation.logger.info("Successfully created and set scope folder")

def set_mode(operation: Operation, tag):
    # Display new tag
    print('new tag: ', tag)
    file = open(operation.scope_config,'r')
    content = ''.join(file.readlines())
    content = re.sub("(?<=tag:\n         mode:)(.*)", " {tag}".format(tag=tag), content )
    with open(operation.scope_config, "w") as scope:
        scope.write(content)
    operation.scope_config_dict = load_yaml(operation.logger, operation.scope_config)
    prepare_scope_folder(operation)

def set_vm_name(vm, subfolder_values, platform_parent_folder):

    scope_name = os.path.basename(platform_parent_folder)
    if scope_name in environment_name_mapping.keys():
        scope_name = environment_name_mapping[scope_name]

    if scope_name != "" :
        scope_name = scope_name + "-"

    if "name" in vm.keys():
        vm_name = vm.get("vm_prefix", subfolder_values["vm_prefix"]) + scope_name + vm["name"] + vm.get("suffix", "") + str(vm.get("indice", "")) + "-" + subfolder_values["client_name"]
        return vm_name

    vm_name = vm.get("vm_prefix", subfolder_values["vm_prefix"]) + scope_name + vm["type"] + vm.get("suffix", "") + str(vm.get("indice", "")) + "-" + subfolder_values["client_name"]

    return vm_name

def get_nb_cpu_per_socket(operation, vm, subfolder_values):

    if "cpu" in vm.keys():
        nb_cpu = int(vm["cpu"])%4
        if nb_cpu == 0 :
            nb_cpu = 4
        return nb_cpu
    else:
        return int(operation.standard_config["vm_types"][operation.vm_type_provider][vm["type"]][subfolder_values["vm_class"]]["nb_vcpu_per_socket"])

def get_nb_sockets(operation, vm, subfolder_values):

    if "cpu" in vm.keys():
        nb_socket = int(float(vm["cpu"])/4)
        if nb_socket == 0:
            nb_socket = 1
        return nb_socket
    else:
        return int(operation.standard_config["vm_types"][operation.vm_type_provider][vm["type"]][subfolder_values["vm_class"]]["nb_sockets"])

def set_custom_ssh_port(extra_parameters, vm_type):

    if "custom_ssh_port" in extra_parameters.keys():
        return extra_parameters

    if vm_type in custom_ssh_port_per_vm_type.keys():
        extra_parameters["custom_ssh_port"] = custom_ssh_port_per_vm_type[vm_type]
        return extra_parameters

def set_vm(operation, vm, subfolder_subnet, subfolder_values, config_ip, subfolder_network_name, subfolder_subnet_name, platform_common_values, platform_parent_folder):

    private_ip = "0.0.0.0"
    if subfolder_network_name in config_ip.keys():
        if subfolder_subnet_name in config_ip[subfolder_network_name].keys():
            vm_name = set_vm_name(vm, subfolder_values, platform_parent_folder)
            if vm_name in config_ip[subfolder_network_name][subfolder_subnet_name]["addresses"]:
                private_ip = config_ip[subfolder_network_name][subfolder_subnet_name]["addresses"][vm_name]
                # if private_ip in platform_common_values["addresses_pool"]:
                #     platform_common_values["addresses_pool"].remove(private_ip)

    if private_ip == "0.0.0.0" :
        private_ip = subfolder_values["addresses_pool"][0]
        subfolder_values["addresses_pool"] = subfolder_values["addresses_pool"][1:]

    config_vm = {
        "availability_zone": vm.get("availability_zone",
                                    subfolder_subnet["availability_zone"]),
        "data_volume_size": vm.get("data_volume_size", 
                                    operation.standard_config["vm_types"]\
                                        [operation.vm_type_provider]\
                                            [vm["type"]]\
                                                [subfolder_values["vm_class"]]\
                                                    ["data_volume_size"]),
        "group": vm["type"],
        "private_ip": private_ip,
        "root_volume_size": subfolder_values["root_volume_size"]\
            .get(subfolder_values["provider"], 32),
        "system_image": vm.get("system_image",
                                operation.standard_config["vm_types"]\
            [operation.vm_type_provider][vm["type"]][subfolder_values["vm_class"]]\
                .get("system_image", subfolder_values["default_os_images"]\
                    [operation.vm_type_provider])),
        "size": {
            "memory": vm.get("memory", operation.standard_config["vm_types"]\
                [operation.vm_type_provider][vm["type"]]\
                    [subfolder_values["vm_class"]]["memory"]),
            "nb_sockets": get_nb_sockets(operation, vm, subfolder_values),
            "nb_vcpu_per_socket": get_nb_cpu_per_socket(operation, vm, subfolder_values)
        },
        "extra_parameters" : set_custom_ssh_port(vm.get("extra_parameters", {}), vm["type"])
    }

    if config_vm["extra_parameters"] is None:
        config_vm.pop("extra_parameters")

    return config_vm

def prepare_platform_action(
        operation: Operation,
        platform: dict,
        platform_parent_folder: str,
        platform_common_values: dict,
        all_config_ips: dict
        ):

    """ this function executes the action needed by a level of a platform description

    :param operation: Operation, the current Operation
    :param platform: dict, the dictionary of parameters for the current scope and subscopes
    :param platform_parent_folder: str, the parent folder of the current scope
    :param platform_common_values: dict, the dictionary of parameters shared by all subscopes
    (below the offset = used IPs)
    """

    # the meta_config defines a IP addresses pool, from which we draw IP addresses for VMs
    # in successive scopes. It means we have to keep track of an offset of already attributed
    # addresses from the pool

    os.makedirs(platform_parent_folder, exist_ok=True)

    # we prepare a config.yaml from jinja template
    subfolder_values = dict(platform_common_values, **platform)
    subfolder_values = dict(subfolder_values, **(operation.standard_config))
    subfolder_values["vm_class"] = "nonprod"
    if os.sep + 'prod' in platform_parent_folder:
        subfolder_values["vm_class"] = "prod"

    environment = platform_common_values.get("environment", "")
    if environment != "":
        environment += "_"

    operation.logger.info("Creating subscope %s" % platform_parent_folder)
    operation.logger.debug("Choosing %s VMs in IP pool : %s" % (len(subfolder_values.get("vms", [])), subfolder_values["addresses_pool"]))

    subfolder_network_name = list(subfolder_values["network"].keys())[0]
    subfolder_network = subfolder_values["network"][subfolder_network_name]

    subfolder_subnet_name = list(subfolder_network["subnets"].keys())[0]
    subfolder_subnet = subfolder_network["subnets"][subfolder_subnet_name]

    subconfig = {
        "network": subfolder_values.get("network", {}),
        "kubernetes": subfolder_values.get("kubernetes", {}),
        "policies": subfolder_values.get("policies", {}),
        "provider": subfolder_values.get("provider", {}),
        "artefacts_repository_public_key_url": subfolder_values.get("artefacts_repository_public_key_url", "unset_repo_url"),
        "vm": {
            subfolder_network_name: {
                subfolder_subnet_name: {
                    set_vm_name(vm, subfolder_values, platform_parent_folder) : set_vm(operation, vm, subfolder_subnet, subfolder_values, all_config_ips, subfolder_network_name, subfolder_subnet_name, platform_common_values, platform_parent_folder) for vm in subfolder_values.get("vms", [])
                }
            }
        }
    }


    if platform_common_values.get("use_tf_backend", False):
        subconfig["use_tf_backend"] = True

    with open(os.path.join(platform_parent_folder, "config.yml"), "w") as f:
        yaml.dump(subconfig, f)

    # we update the offset in the addresses pool
    nb_vms_in_subfolder = len(subfolder_values.get("vms", []))

    # we do the same for subscopes
    for key, val in platform.items():
        if key not in ['kubernetes', "spark_cluster", "environments", "vms"]:
            if isinstance(val, dict):
                new_platform_folder = os.path.join(platform_parent_folder, key)
                if key in ["preprod", "pprod", "prod", "production"]:
                    platform_common_values["environment"] = key
                prepare_platform_action(
                    operation,
                    val,
                    new_platform_folder,
                    platform_common_values,
                    all_config_ips
                    )

    return

def collect_set_ips(platform, platform_parent_folder, all_config_ips):

    """ this function collect all data from all subscopes config_ips.yml """

    for key, val in platform.items():
        if key not in ['kubernetes', "spark_cluster", "environments", "vms"]:
            if isinstance(val, dict):
                new_platform_folder = os.path.join(platform_parent_folder, key)
                config_ip = {}
                # if subscope already exists and IP are already sets, we must edit the IP pool
                config_ip_files = os.path.join(new_platform_folder, "config_ips.yml")
                if os.path.isfile(config_ip_files):
                    with open(config_ip_files, "r") as f:
                        config_ip = yaml.load(f, Loader=yaml.FullLoader)
                all_config_ips = merge_dictionaries(all_config_ips, config_ip)
                collect_set_ips(
                    val,
                    new_platform_folder,
                    all_config_ips
                    )

    return all_config_ips


def init_meta_distribute(operation: Operation):

    """ this function generates the folders and configuration tree for a full platform
    for a dedicated customer

    :param operation: Operation, the current Operation
    """

    # we check if the meta_config already exists
    meta_config = {'infra':dict()}
    meta_config_path = os.path.join(operation.scope_config_folder, "meta_config.yml")
    if os.path.isfile(meta_config_path):
        with open(meta_config_path, "r") as f:
            try:
                meta_config = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as e:
                operation.logger.error("Failed to open meta_config file %s with error %s" % (meta_config_path, e))

    # we set the addresses pool
    # cidr_block = ipaddress.summarize_address_range(
    # ipaddress.IPv4Address(meta_config["addresses_pool_start"]),
    # ipaddress.IPv4Address(meta_config["addresses_pool_end"]))
    # addresses_pool = [str(addr) for addr in cidr_block]
    addresses_pool = []
    if "addresses_pool" in meta_config.keys():
        if isinstance(meta_config["addresses_pool"], list):
            addresses_pool = meta_config["addresses_pool"]
    else:
        if ("addresses_pool_start" in meta_config.keys()) &\
        ("addresses_pool_end" in meta_config.keys()):
            operation.logger.debug("Addresses range : from %s to %s" % (meta_config["addresses_pool_start"], meta_config["addresses_pool_end"]))
            cidr_block = netaddr.iter_iprange(meta_config["addresses_pool_start"],
                                              meta_config["addresses_pool_end"])
            addresses_pool = list(str(addr) for addr in cidr_block)
        else:
            operation.logger.error("Addresses pool not provided or badly formatted, exiting")
            sys.exit()

    operation.logger.debug("Working with addresses pool : %s" % addresses_pool)
    meta_config["addresses_pool"] = addresses_pool

    all_config_ips = collect_set_ips(meta_config['infra'], operation.scope_config_folder, {})
    for network, network_content in all_config_ips.items():
        for subnetwork, subnetwork_content in network_content.items():
            for vm, address in subnetwork_content.get("addresses", {}).items():
                if address in meta_config["addresses_pool"]:
                    meta_config["addresses_pool"].remove(address)

    # we loop through the folders requested by the meta_config to create subscopes
    prepare_platform_action(operation, meta_config['infra'], operation.scope_config_folder,
                            meta_config, all_config_ips)


def init_meta_aggregate(operation: Operation):

    """ this function aggregates all config files in current folder and subfolders
    into a meta_config.yml

    :param operation: Operation, the current Operation
    """

    # we loop through the config folder
    meta_config = {'ansible':dict()}
    for (root, _, files) in os.walk(operation.scope_config_folder):
        if 'config.yml' in files:
            subconfig_path = os.path.join(root, 'config.yml')
            subconfig_scope = os.path.join(*(subconfig_path.split(os.sep)\
                [len(operation.scope_config_folder.split(os.sep)):-1]))
            # print(subconfig_scope)
            with open(subconfig_path, 'r') as f:
                try:
                    subconfig_data = yaml.load(f, Loader=yaml.FullLoader)
                except Exception as e:
                    operation.logger.error(
                        "Failed to open file % with error %s".format(subconfig_path, e))
            meta_config['infra'][subconfig_scope] = subconfig_data.get('vm')

    # we write the meta_config.yml
    meta_config_path = os.path.join(operation.scope_config_folder, "meta_config.yml")
    with open(meta_config_path, "w") as f:
        yaml.dump(meta_config, f)

def set_admin(operation: Operation):

    """ this function download the list of default admin users for the newly created
    VMs, and their associated SSH public keys """

    # we download the list of admin users
    admin_list = []
    try:
        # Construct the full URL to the YAML file in the Nexus repository
        full_url = f"{operation.scope_config_dict['artefacts_repository_admin_user_list']}"

        # Send a GET request to download the YAML file
        response = requests.get(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Load the YAML content as a Python dictionary
            admin_list = yaml.safe_load(response.text)
        else:
            print(f"Failed to download YAML file. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    admin_public_keys = []

    for admin in admin_list:
        try:
            # Construct the full URL to the YAML file in the Nexus repository
            full_url = f"{operation.scope_config_dict['artefacts_repository_public_key_url']}/{ admin['name'] }_authorized_key/latest/{ admin['name'] }_authorized_key-latest.txt"

            # Send a GET request to download the YAML file
            response = requests.get(full_url)

            # parse list of keys
            keys = [key for key in response.text.split('\n') if key != ""]

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Load the YAML content as a Python dictionary
                admin_public_keys.append({
                    'name' : admin['name'],
                    'public_key' : keys
                })
            else:
                print(f"Failed to download key file. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    admin_public_keys_tfvars_file = os.path.join(operation.scope_terraform_folder, "admin.auto.tfvars.json")
    print(admin_public_keys_tfvars_file)
    with open(admin_public_keys_tfvars_file, "w") as f:
        json.dump({"users_list": admin_public_keys}, f, indent=4)


    return None

def set_dns(operation: Operation):

    """ this function will call the operate_dsn function with the 'set' operation """

    operate_dns(operation, "set")

def delete_dns(operation: Operation):

    """ this function will call the operate_dsn function with the 'delete' operation """

    operate_dns(operation, "delete")

def operate_dns(operation: Operation, operator):

    """ this function creates or deletes the DNS records (A and PTR) associated with the 
    config_ips.yml file """

    # loading attributed IPs from config_ips.yml
    operation.load_ips()

    dns_server_type = operation.standard_config.get("default_dns_server_type", "bind")

    # check if DNS server credentials are defined
    dns_credentials = {}
    for dns_credential in ["address", "login", "password"]:
        dns_credential_var = "CLOUDTIGER_DNS_" + dns_credential.upper()
        if dns_credential_var not in os.environ.keys():
            operation.logger.error(f"Error : there is no {dns_credential_var} value defined in your base .env file")
            sys.exit()
        dns_credentials[dns_credential] = os.environ[dns_credential_var]
        if dns_credential == "password":
            dns_credentials[dns_credential] = base64.b64decode(dns_credentials[dns_credential]).decode('ascii').rstrip('\n')

    # check if a domain is defined for editing your VMs DNS
    if "search" not in operation.standard_config.keys():
        operation.logger.error(f"Error : the domain is not defined in your standard.yml file, please define a 'search' value")
        sys.exit()

    domain = operation.standard_config['search']

    # for Windows server DNS
    if dns_server_type == "windows":
        ms_connection = dns_login(
            operation,
            dns_credentials["address"],
            dns_credentials["login"],
            dns_credentials["password"]
        )

        if operator == "set":
            for vm_name, ip_address in operation.scope_unpacked_ips.items():
                operation.logger.info(f"Adding VM DNS {vm_name} to domain {domain}")
                dns_add_a_record(operation, vm_name, ip_address, domain, ms_connection)
                if operation.ptr:
                    dns_add_ptr_record(operation, vm_name, ip_address, domain, ms_connection)

        if operator == "delete":
            for vm_name, ip_address in operation.scope_unpacked_ips.items():
                operation.logger.info(f"Deleted VM DNS {vm_name} from domain {domain}")
                dns_delete_a_record(operation, vm_name, ip_address, domain, ms_connection)
                dns_delete_ptr_record(operation, vm_name, ip_address, domain, ms_connection)

    return