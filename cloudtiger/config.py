""" Config operations for CloudTiger """
from jinja2 import Environment, FileSystemLoader
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator, EmptyInputValidator, PathValidator
import os
import sys
import json
import yaml
import copy
from colored import Fore, Back, Style

from cloudtiger.cloudtiger import Operation
from cloudtiger.data import common_environments, common_internal_customers, worldwide_cloud_datacenters, clusterized_hypervisors, supported_providers, worldwide_cloud_default_network, pvs_suffix
from cloudtiger.specific.vsphere import check_folder_exists_vsphere

def int_to_two_char_string(number):
    if 0 <= number <= 99:
        return f"{number:02d}"
    else:
        return "Invalid number"

def generate(operation: Operation):

    """ this function prompt an interactive definition of a scope/config
    
    :param operation: Operation, the current Operation
    """

    # choose main cloud provider
    all_supported_providers = [
            Choice(value=prov['name'], name=prov['common_name'], enabled=False) for prov in supported_providers["private"] + supported_providers["public"]
        ]
    provider = "admin"
    if operation.provider == "admin":
        provider = inquirer.select(
            message="Which Cloud Provider would you like to use:",
            choices=all_supported_providers,
            multiselect=False,
            default=None,
        ).execute()
    else:
        provider = operation.provider

    # is it a public cloud provider ?
    public_cloud_provider = (provider in worldwide_cloud_datacenters.keys())

    # is it an internal or external deployment ?
    default_deployment_mode = "internal"
    if public_cloud_provider:
        default_deployment_mode = "external"
    deployment_mode = inquirer.select(
            message="Select the deployment mode (internal or external):",
            choices=[
                Choice(value="internal", name="internal"),
                Choice(value="external", name="external")
            ],
            multiselect=False,
            default=default_deployment_mode,
        ).execute()

    # prepare deployment manifest
    manifest_data = {}
    if operation.manifest:
        manifest_data = manifest(operation, deployment_mode)

    config_content = {}

    # get config template from internal catalog
    config_template_dir = os.path.join(
        operation.libraries_path, "internal", "config")
    environment = Environment(
        loader=FileSystemLoader(config_template_dir),
        trim_blocks=True
    )
    config_template = environment.get_template("config.yml.j2")

    # if you have a platform manifest, set associated ansible config
    public_exposition_layer = False
    using_platform_manifest = False
    if len(manifest_data) > 0:
        using_platform_manifest = True

    if using_platform_manifest:

        # choose if a public exposition proxy has to be set
        public_exposition_layer = inquirer.confirm(
            message="Do you want to include a public exposition proxy ?",
            default=public_cloud_provider
        ).execute()

    # do you have secondary cloud providers on your network ?
    secondary_providers = operation.standard_config.get(provider, {}).get("secondary_providers", [])
    have_secondary_providers = inquirer.confirm(
        message="Do you have secondary cloud providers sharing your network ?",
        default=(len(secondary_providers) > 0)
    ).execute()

    default_secondary_provider = None
    if len(secondary_providers) > 0:
        default_secondary_provider = secondary_providers[0]
    secondary_providers = []

    # provide secondary cloud providers
    while have_secondary_providers:
        secondary_provider = inquirer.select(
            message="Which Secondary Cloud Provider would you like to add:",
            choices=all_supported_providers,
            multiselect=False,
            default=default_secondary_provider,
        ).execute()

        secondary_providers.append(secondary_provider)

        have_secondary_providers = inquirer.confirm(
            message="Do you want to add an extra secondary provider ?",
            default=False
        ).execute()

    # cloud region
    region = "datacenter"
    cloud_regions = []
    if public_cloud_provider:
        cloud_regions = [
            Choice(value=region, name=region, enabled=(region == worldwide_cloud_datacenters[provider]['default_datacenter']))
            for region in worldwide_cloud_datacenters[provider]['datacenters']
        ]
        region = inquirer.select(
            message="Select the datacenter/region you want for your cloud provider",
            choices=cloud_regions,
            multiselect=False,
            default=worldwide_cloud_datacenters[provider]['default_datacenter'],
        ).execute()

    # if nutanix, define subcluster
    default_cluster = "default_cluster"
    if provider in clusterized_hypervisors:
        if provider == "nutanix":
            available_clusters = [
                cluster['spec']['name'] for cluster in operation.existing_clusters_info['nutanix_clusters']
            ]
            available_clusters = [
                Choice(value=cluster, name=cluster) for cluster in available_clusters
            ]
            default_cluster = operation.standard_config.get("nutanix").get("default_cluster", available_clusters[0])
            default_cluster = inquirer.select(
                message="Select the default cluster for the VMs you want to create",
                choices=available_clusters,
                multiselect=False,
                default=default_cluster,
            ).execute()

    # define customer
    customer_list = operation.standard_config.get("customers", common_internal_customers)
    customer_choices = [
        Choice(value=customer, name=customer, enabled=False) for customer in customer_list
    ]
    customer_choices = [Choice(value="custom", name="custom")] + customer_choices
    chosen_customer = inquirer.select(
        message = "Choose a customer for your scope (custom customer's scope starts at 'gitops/config', standard customer's scope starts at 'gitops/customers/<CUSTOMER>'):",
        choices = customer_choices,
        multiselect=False,
        default = None
    ).execute()
    if chosen_customer == "custom":
        chosen_customer = inquirer.text(
            message = "Please provide the exact name of your customer"
        ).execute()

    # define environment
    common_env = operation.standard_config.get("common_environments", common_environments)
    environments_choices = [
        Choice(value=environment, name=environment, enabled=False) for environment in common_env
    ]
    environments_choices.append(Choice(value="custom", name="custom"))
    chosen_environment = inquirer.select(
        message = "Choose an environment for your scope:",
        choices = environments_choices,
        multiselect=False,
        default = None
    ).execute()
    if chosen_environment == "custom":
        chosen_environment = inquirer.text(
            message = "Please provide the exact name of your environment"
        ).execute()

    # if you have a platform manifest, get VM type counts according to environment
    if using_platform_manifest:
        sizing_data = manifest_data["manifest"].get("infrastructure", {}).get("sizing", {})
        manifest_data['vm_type_count'] = {'public':{}, 'private':{}}
        for module in (manifest_data['activated_modules'] + ['requirements']):
            for vm_type, vm_count in sizing_data.get(chosen_environment, sizing_data["nonprod"]).get(module, {}).items():
                # check if VM should be on private or public subnet
                vm_kind = "private"
                if vm_count.get("public", False):
                    vm_kind = "public"
                # check if VM is needed as belonging to an extral public layer
                if (not vm_count.get("exposition_layer", False)) or public_exposition_layer:
                    if vm_type in manifest_data['vm_type_count'].keys():
                        manifest_data['vm_type_count'][vm_kind][vm_type] += vm_count["count"]
                    else:
                        manifest_data['vm_type_count'][vm_kind][vm_type] = vm_count["count"]

        for kind in ['public', 'private']:
            manifest_data['vm_type_count'][kind] = [
                {
                    "vm_type" : k,
                    "count": v
                } for k, v in manifest_data['vm_type_count'][kind].items()
            ]

    # define scope
    # by default, the scope format is <PROVIDER>/<CUSTOMER>/<ENVIRONMENT>
    default_scope = os.path.join(provider, chosen_customer, chosen_environment)
    if using_platform_manifest:
        # if we are deploying a platform, the default scope format is <PROVIDER>/customers/<CUSTOMER>/<ENVIRONMENT>
        default_scope = os.path.join(provider, "customers", chosen_customer, chosen_environment)

    scope = inquirer.text(message="Provide the path of the scope you want to create, excluding the 'config' folder:", 
                          default=default_scope).execute()

    # do you want to add SSH keys from a repository ?
    add_ssh_keys_from_repo = inquirer.confirm(
        message="Do you want to add SSH keys from a repository ?",
        default=operation.standard_config.get("add_ssh_keys_from_repo", False)
    ).execute()

    if add_ssh_keys_from_repo:
        # provide path to public SSH keys repository
        artefacts_repository_admin_user_list = operation.standard_config.get("artefacts_repository_admin_user_list", "")
        artefacts_repository_public_key_url = operation.standard_config.get("artefacts_repository_public_key_url", "")
        artefacts_repository_admin_user_list = inquirer.text(
                message="Provide the URL for the admin users list on an artefacts repository:",
                default=artefacts_repository_admin_user_list
            ).execute()
        
        artefacts_repository_public_key_url = inquirer.text(
                message="Provide the URL for the admin users public SSH keys on an artefacts repository:",
                default=artefacts_repository_public_key_url
            ).execute()

    # do you want to provide nameservers to the VMs ?
    add_nameservers = inquirer.confirm(
        message="Do you want to add nameservers ?",
        default=((not public_cloud_provider) and ("nameservers" in operation.standard_config.keys()))
    ).execute()

    nameservers_list = []
    if add_nameservers:
        # provide list of nameservers
        nameservers_list = operation.standard_config.get("nameservers", "")
        nameservers_list = inquirer.text(
                message="Provide a comma-separated list of addresses for your nameservers",
                default=nameservers_list
            ).execute()

    # do you want to provide a default search domain for the VMs ?
    add_search_domain = inquirer.confirm(
        message="Do you want to add a default search domain for the VMs ?",
        default=((not public_cloud_provider) and ("search" in operation.standard_config.keys()))
    ).execute()

    search_domain_list = []
    if add_search_domain:
        # provide list of nameservers
        search_domain_list = operation.standard_config.get("search", "")
        search_domain_list = inquirer.text(
                message="Provide a comma-separated list of search domains for your nameservers",
                default=search_domain_list
            ).execute()

    # define a default OS for VMs
    default_os = operation.standard_config.get(provider, {}).get("default_os_template", None)
    os_choices = operation.standard_config['system_images'].get(provider, {}).keys()
    set_default_os = inquirer.confirm(
        message="Do you want to set default OS for all the VMs of your scope ?",
        default=True
    ).execute()
    if set_default_os:
        default_os = inquirer.select(
            message = "Choose a default OS for your scope:",
            choices = os_choices,
            multiselect=False,
            default = default_os
        ).execute()

    # define a default folder for VMs - for vsphere provider only
    default_folder = os.path.join(chosen_customer, chosen_environment)
    if provider == "vsphere":
        default_base_folder = operation.standard_config[provider].get("default_base_folder", "")
        default_folder = os.path.join(default_base_folder, default_folder)
        set_default_folder = inquirer.confirm(
            message="Do you want to set default vsphere folder for all the VMs of your scope ?",
            default=True
        ).execute()
        if set_default_folder:
            default_folder = inquirer.text(
                message = "Set a default vsphere folder for your scope:",
                default = default_folder
            ).execute()

    # define default specific resources for VMs - for vsphere provider only
    vsphere_specific_resources = {}
    if provider == "vsphere":
        operation.logger.info('*** VSPHERE SPECIFIC ***')
        for resource in ["cluster", "datacenter", "datastore", "host"]:
            set_default_resource = inquirer.confirm(
                message=f"Vsphere infrastructure - Do you want to set default {resource} for all the VMs of your scope ?",
                default=True
            ).execute()
            if set_default_resource:
                available_resources = operation.existing_clusters_info.get("vsphere_cluster_resources", {}).get(resource, [])
                available_resources = [
                    available_resource.get("name", "no_name") for available_resource in available_resources
                ]
                if len(available_resources) == 0:
                    operation.logger.info(f"There is no resource of type {resource} in your vsphere cluster")
                    sys.exit()
                default_resource = operation.standard_config.get("vsphere", {}).get("default_" + resource, "")
                if default_resource == "":
                    default_resource = available_resources[0]
                default_resource = inquirer.select(
                    message = f"Choose a default vsphere {resource} for your scope:",
                    choices = available_resources,
                    multiselect=False,
                    default = default_resource
                ).execute()
                vsphere_specific_resources[resource] = default_resource
        vsphere_specific_resources['folder'] = default_folder

    # get network data
    network = {}
    network_name = operation.provider + "_network"
    if public_cloud_provider:
        network_name = inquirer.text(
            message = "Choose the name of your network",
            default = "main_network"
        ).execute()
        network_cidr = inquirer.text(
            message = "Choose the CIDR range of your network",
            default = worldwide_cloud_default_network["default_cidr_per_env"].get(chosen_environment, worldwide_cloud_default_network["default_cidr"]) + "0.0/16"
        ).execute()
        network = {
            network_name : {
                "network_cidr": network_cidr,
                "prefix": chosen_environment + "_",
                "subnets" : {}
            }
        }
    else:
        network = { network_name : {"subnets" : {}} }

    # get subnets data
    subnet_data = {}
    if operation.provider in ["nutanix", "vsphere"]:
        subnet_data = {
            subnet.get("spec", {}).get("name", "missing_vlan_name"):
            {
                "name": subnet.get("spec", {}).get("name", "missing_vlan_name"),
                "cidr_block": subnet.get("spec", {}).get("resources").get("ip_config", {}).get("subnet_ip", "192.168.0.0") + "/" + str(subnet.get("spec", {}).get("resources").get("ip_config", {}).get("prefix_length", "32")),
                "vlan_id" : subnet.get("spec", {}).get("resources").get("vlan_id", 0),
                "gateway_ip_address": subnet.get("spec", {}).get("resources").get("ip_config", {}).get("default_gateway_ip", "192.168.0.1")
            } for subnet in operation.all_network_info.get("nutanix_network", {}).get("subnets", [])
        }
    if operation.provider == "vsphere":
        for subnet in operation.all_network_info.get("vsphere", {}).get("subnets", []):
            subnet_data[subnet['name']]['name'] = subnet['name']

        network[network_name]['datacenter'] = vsphere_specific_resources['datacenter']

    # choose subnet
    add_subnet = True
    default_subnet = operation.standard_config.get(provider, {}).get("default_vlan", "default")
    subnet_choices = [
        Choice(value=subnet_name, name=subnet_name, enabled=(subnet_name == default_subnet)) for subnet_name, subnet in subnet_data.items()
    ]

    subnet_iterator = 0
    a_public_subnet_exists = False
    while add_subnet:

        vm_subnet_count = 0
        
        # do we create a new subnet, or add VMs on an existing one ?
        create_subnet = inquirer.confirm(
                message="Create new subnet ?",
                default=(public_cloud_provider)
        ).execute()

        # by default the subnet is not managed by Terraform
        not_terraform_managed = True

        if create_subnet:

            not_terraform_managed = False

            network_name = list(network.keys())[0]
            default_subnet = worldwide_cloud_default_network["subnets"][subnet_iterator]

            subnet_name = inquirer.text(
                message = "Please provide subnet name",
                default = default_subnet["name"]
            ).execute()

            cidr_block = inquirer.text(
                message = "Please provide subnet CIDR",
                default = worldwide_cloud_default_network["default_cidr_per_env"].get(chosen_environment, worldwide_cloud_default_network["default_cidr"]) + default_subnet["cidr_block_suffix"]
            ).execute()

            az_suffix = inquirer.select(
                message = "Please provide availability zone",
                choices = [
                        Choice(value = "a", name = "a"),
                        Choice(value = "b", name = "b"),
                        Choice(value = "c", name = "c"),
                    ],
                multiselect=False,
                default = default_subnet["availability_zone"],
            ).execute()

            # get suffix of availability zone
            az_suffix_len = len(region.split("-"))
            if az_suffix_len < 2:
                az_suffix = "-" + az_suffix

            added_subnet = {
                "name" : subnet_name,
                "cidr_block" : cidr_block,
                "availability_zone" : region + az_suffix
            }

            default_public = inquirer.confirm(
                message="Is subnet public ?",
                default=(default_subnet.get("public", False))
            ).execute()

            if default_public:
                a_public_subnet_exists = True
                added_subnet["public"] = "true"
                network[network_name]["private_subnets_escape_public_subnet"] = default_subnet["name"]
            network[network_name]['subnets'][subnet_name] =  added_subnet

            added_subnet = subnet_name

        else:
            added_subnet = inquirer.select(
                message = "Choose an existing subnet for your scope",
                choices = subnet_choices,
                multiselect = False,
                default = default_subnet
            ).execute()

            network[network_name]['subnets'][added_subnet] = subnet_data[added_subnet]



            # ask if IPAM is activated on VLAN
            no_dhcp_ip_attribution = inquirer.confirm(
                message="Are you setting IP addresses without DHCP ?",
                default=True
            ).execute()

            network[network_name]['subnets'][added_subnet]['managed_ips'] = no_dhcp_ip_attribution
        
        # we define if the subnet should be managed by Terraform in the current scope
        network[network_name]['subnets'][added_subnet]['unmanaged'] = not_terraform_managed

        # get subnet kind
        subnet_is_public = network[network_name]['subnets'][added_subnet].get("public", False)
        subnet_kind = "private"
        if subnet_is_public:
            subnet_kind = "public"

        # add VMs on subnet
        add_vm = True
        vm = { network_name : {added_subnet : {}}}
        vm_type_choices = [
            Choice(value=vm_type_name, name=vm_type_name) for vm_type_name in operation.standard_config["vm_types"].get(provider, operation.standard_config["vm_types"]["default"]).keys()
        ]

        vm_type_manifest_iterator = 0
        vm_count = 0

        # choose IP addresses for the VM ?
        choose_ip_addresses = inquirer.confirm(
            message="Do you want to manually set IP addresses for this VLAN ?",
            default=public_cloud_provider
        ).execute()

        while add_vm:

            default_vm_sizing = "nonprod"
            if chosen_environment == "prod":
                default_vm_sizing = "prod"

            # check if we are using a platform manifest
            if "sizing" in manifest_data.get("manifest", {}).get("infrastructure", {}).keys():
                # if platform manifest, the number of VMs of each type is pre-set
                nb_vms = manifest_data['vm_type_count'][subnet_kind][vm_type_manifest_iterator]['count']
                vm_set = (nb_vms > 1)
                added_vm_type = manifest_data['vm_type_count'][subnet_kind][vm_type_manifest_iterator]['vm_type']
                
                # customize_sizing = inquirer.confirm(
                #     message=f"Do you want to customize {added_vm_type} nodes ?",
                #     default=False
                # ).execute()
                # if customize_sizing:
                #     vm_sizing = "custom"

            else:
                # do you want a set of identical VMs ?
                nb_vms = 1
                vm_set = inquirer.confirm(
                    message="Do you want a set of identical VMs ?",
                    default=False
                ).execute()

                if vm_set:
                    nb_vms = inquirer.number(
                        message="Enter number of VMs:",
                        min_allowed=1,
                        max_allowed=99,
                        default=1,
                    ).execute()

                added_vm_type = inquirer.select(
                    message = "Choose a VM type",
                    choices = vm_type_choices,
                    multiselect = False,
                    default = None
                ).execute()

            vm_sizing = inquirer.select(
                message="Which sizing for the VM:",
                choices=[
                    Choice(value="prod", name="default - prod",enabled=True),
                    Choice(value="nonprod", name="default - non prod",enabled=False),
                    Choice(value="custom", name="custom",enabled=False),
                ],
                multiselect=False,
                default=default_vm_sizing,
            ).execute()

            vm_values = {}

            if vm_sizing in ["prod", "nonprod"]:
                vm_standard_values = operation.standard_config["vm_types"].get(provider, operation.standard_config["vm_types"]["default"])[added_vm_type][vm_sizing]
                nb_sockets = vm_standard_values["nb_sockets"]
                nb_vcpu_per_socket = vm_standard_values["nb_vcpu_per_socket"]
                memory = vm_standard_values["memory"]
                if provider in ["nutanix", "vsphere"]:
                    root_volume_size = vm_standard_values.get("root_volume_size", operation.standard_config.get("default_root_volume_size", "16"))
                    data_volume_size = 0
                else:
                    data_volume_size = vm_standard_values["data_volume_size"]
                    root_volume_size = operation.standard_config.get("default_root_volume_size", "16")
                vm_group = added_vm_type
            else:
                nb_sockets = inquirer.number(
                    message="Enter number of sockets:",
                    min_allowed=1,
                    max_allowed=16,
                    default=1,
                ).execute()
                nb_vcpu_per_socket = inquirer.number(
                    message="Enter number of vCPUs per socket:",
                    min_allowed=1,
                    max_allowed=16,
                    default=1,
                ).execute()
                memory = inquirer.number(
                    message="Enter number of Mo of RAM:",
                    min_allowed=1024,
                    max_allowed=65536,
                    default=1024,
                ).execute()
                root_volume_size = inquirer.number(
                    message="Enter number of Go of root disk:",
                    min_allowed=0,
                    max_allowed=1000,
                    default=16,
                ).execute()
                data_volume_size = inquirer.number(
                    message="Enter number of Go of data disk:",
                    min_allowed=0,
                    max_allowed=1000,
                    default=16,
                ).execute()
                vm_group = inquirer.text(
                    message="Set vm group:",
                    default = added_vm_type
                ).execute()
            vm_values = {
                "size": {
                    "nb_sockets": nb_sockets,
                    "nb_vcpu_per_socket": nb_vcpu_per_socket,
                    "memory": memory,
                },
                "data_volume_size": data_volume_size,
                "root_volume_size": root_volume_size,
                "group": vm_group
            }

            # set VM's OS
            vm_os = default_os
            set_vm_specific_os = inquirer.confirm(
                message=f"Do you want to set a specific OS for this VM ?",
                default=False
            ).execute()
            if set_vm_specific_os:
                vm_os = inquirer.select(
                    message = "Choose an OS for your VM:",
                    choices = os_choices,
                    multiselect=False,
                    default = default_os
                ).execute()

            if provider == "nutanix":
                vm_values['availability_zone'] = default_cluster

                # set VM template UUID from standard config
                available_clone_uuid = operation.standard_config.get("system_images", {}).get("nutanix", {}).get(vm_os, {}).get("uuid", "unset_template_vm_uuid")
                vm_values['extra_parameters'] = vm_values.get("extra_parameters", {})
                vm_values['extra_parameters']["source_image_uuid"] = available_clone_uuid

                vm_values['system_image'] =  vm_os

            # vsphere specific - set resources
            if provider == "vsphere":
                operation.logger.info('*** VSPHERE SPECIFIC ***')
                vsphere_vm_specific_resources = vsphere_specific_resources
                set_custom_resources = inquirer.confirm(
                    message=f"Do you want to set custom vSphere resources for this VM ?",
                    default=False
                ).execute()
                if set_custom_resources:
                    for resource in ["cluster", "datacenter", "datastore", "host"]:
                        available_resources = operation.all_existing_clusters.get("vsphere_cluster_resources", {}).get(resource, [])
                        available_resources = [
                            available_resource.get("name", "no_name") for available_resource in available_resources
                        ]
                        if len(available_resources) == 0:
                            operation.logger.info(f"There is no resource of type {resource} in your vsphere cluster")
                            sys.exit()
                        vm_resource = inquirer.select(
                            message = f"Choose a default vsphere {resource} for your scope:",
                            choices = available_resources,
                            multiselect=False,
                            default = vsphere_specific_resources[resource]
                        ).execute() 
                        vsphere_vm_specific_resources[resource] = vm_resource
                vm_values['system_image'] =  vm_os

                vm_values['folder'] =  vsphere_vm_specific_resources['folder']
                vm_values['extra_parameters'] = vm_values.get('extra_parameters', {})
                vm_values['extra_parameters']['datastore'] = "/" + "/".join([vsphere_vm_specific_resources['datacenter'], "datastore", vsphere_vm_specific_resources['datastore']])
                vm_values['extra_parameters']['resource_pool'] = "/" + "/".join([vsphere_vm_specific_resources['datacenter'], "host", vsphere_vm_specific_resources['cluster']])
                vm_values['datacenter'] = vsphere_vm_specific_resources['datacenter']
                vm_values['availability_zone'] = vsphere_vm_specific_resources['host']

            # prepare VM default name
            normalized_naming = operation.standard_config.get("normalized_naming", {})
            normalized_environment = normalized_naming.get("environment", {}).get(chosen_environment, chosen_environment)
            normalized_vm_type = normalized_naming.get("type", {}).get(added_vm_type, added_vm_type)
            normalized_customer = normalized_naming.get("customer", {}).get(chosen_customer, chosen_customer)

            if vm_set:

                for i in range(0, int(nb_vms)):
                    vm_name = ''.join([normalized_environment, normalized_vm_type, int_to_two_char_string(i+1), normalized_customer])
                    vm_name = inquirer.text(
                        message = "Please provide the name of your VM",
                        default = vm_name
                    ).execute()
                    if choose_ip_addresses:
                        cidr_prefix = network[network_name]['subnets'][added_subnet].get("cidr_block", "10.0.0.0/16")
                        cidr_prefix = '.'.join(cidr_prefix.split('.')[:3])
                        private_ip = inquirer.text(
                            message = "Please provide the private IP address of your VM",
                            default = cidr_prefix + "." + int_to_two_char_string(i+10)
                        ).execute()
                        vm_values['private_ip'] = private_ip
                    vm[network_name][added_subnet][vm_name] = copy.deepcopy(vm_values)

            else:
                vm_name = ''.join([normalized_environment, normalized_vm_type, normalized_customer])
                vm_name = inquirer.text(
                    message = "Please provide the name of your VM",
                    default = vm_name
                ).execute()
                if choose_ip_addresses:
                    cidr_prefix = network[network_name]['subnets'][added_subnet].get("cidr_block", "10.0.0.0/16")
                    cidr_prefix = '.'.join(cidr_prefix.split('.')[:3])
                    private_ip = inquirer.text(
                        message = "Please provide the private IP address of your VM",
                        default = cidr_prefix + "." + int_to_two_char_string(vm_subnet_count+10)
                    ).execute()
                    vm_values['private_ip'] = private_ip
                vm[network_name][added_subnet][vm_name] = vm_values

            # check if we are using a platform manifest
            if "sizing" in manifest_data.get("manifest", {}).get("infrastructure", {}).keys():
                vm_type_manifest_iterator += 1
                # if platform manifest, we continue to the next VM type of the manifest
                if vm_type_manifest_iterator >= len(manifest_data['vm_type_count'][subnet_kind]):
                    add_vm = False
            else:
                # do you want to add an extra VM
                add_vm = inquirer.confirm(
                    message="Do you want to add another VM ?",
                    default=False
                ).execute()

            # increase vm count for subnet
            if vm_set:
                vm_count += nb_vms
            else:
                vm_count += 1

        # do you want to add an extra subnet
        add_subnets = False
        # if we are using a manifest with a public exposition layer, we need 2 subnets
        if using_platform_manifest:
            if public_exposition_layer:
                if subnet_iterator == 0:
                    add_subnets = True
        add_subnet = inquirer.confirm(
            message="Do you want to add another subnet ?",
            default=add_subnets
        ).execute()

        subnet_iterator += 1

    # do you plan to use a Terraform backend
    use_tf_backend = inquirer.confirm(
        message="Do you want to use a remote Terraform backend ?",
        default=("CLOUDTIGER_BACKEND_ADDRESS" in operation.provider_secret.keys())
    ).execute()

    template_data = {
        "provider" : provider,
        "chosen_environment" : chosen_environment,
        "chosen_customer" : chosen_customer,
        "add_ssh_keys_from_repo" : add_ssh_keys_from_repo,
        "network" : network,
        "vm" : vm,
        "use_tf_backend" : use_tf_backend
    }

    if len(secondary_providers) > 0:
        template_data["secondary_providers"] = secondary_providers

    if public_cloud_provider:
        template_data["region"] = region

    if add_ssh_keys_from_repo:
        template_data["artefacts_repository_public_key_url"] = artefacts_repository_public_key_url
        template_data["artefacts_repository_admin_user_list"] = artefacts_repository_admin_user_list

    if len(nameservers_list) > 0:
        template_data['nameservers_list'] = nameservers_list.split(',')

    if len(search_domain_list) > 0:
        template_data['search_domain_list'] = search_domain_list.split(',')

    # if you have a platform manifest, set associated ansible config
    if using_platform_manifest:

        # set the folder to browse for a platform manifest ansible template
        default_ansible_folder = "./manifests"
        ansible_folder = inquirer.text(
            message = "Please provide the platform ansible template folder to browse, relative to your current project root folder",
            default = default_ansible_folder,
            validate = PathValidator(is_dir=True, message="Input is not a folder")
        ).execute()

        if public_exposition_layer:
            manifest_data['public_dns'] = inquirer.text(
                message="Choose a public DNS for the exposition of your platform",
                default=provider + "." + operation.standard_config.get("default_external_domain", "myplatform.com")
            ).execute()

        ansible_template_file = inquirer.select(
            message="Select the ansible template to use:",
            choices=[
                Choice(value="internal", name="internal"),
                Choice(value="external", name="external")
            ],
            multiselect=False,
            default=deployment_mode,
        ).execute()
        ansible_template_file = ansible_template_file + ".ansible.yml.j2"

        if not os.path.exists(os.path.join(ansible_folder, ansible_template_file)):
            operation.logger.info(f"The ansible template {ansible_template_file} does not exist, please provide one before generating a config file for a platform")
            sys.exit()

        # get ansible template
        environment = Environment(
            loader=FileSystemLoader(ansible_folder),
            trim_blocks=True
        )
        ansible_template = environment.get_template(ansible_template_file)

        ### render ansible template file
        manifest_data['config'] = template_data
        manifest_data['public_exposition_layer'] = public_exposition_layer
        operation.logger.debug("Values for generating manifest :")
        operation.logger.debug(yaml.dump(manifest_data))

    ### create scope
    scope_folder = os.path.join(operation.project_root, "config", scope)

    os.makedirs(scope_folder, exist_ok=True)

    scope_file = os.path.join(scope_folder, "config.yml")

    if using_platform_manifest:

        # dump deploy file
        deploy_file = os.path.join(scope_folder, "deploy.yml")
 
        with open(deploy_file, mode="w", encoding="utf-8") as deployfile:
            yaml.dump(manifest_data, deployfile)

        operation.logger.info(f"Created deploy file for scope {scope}")

    else:

        if os.path.exists(scope_file):
            do_not_erase = inquirer.confirm(
                message="Do you want to overwrite existing config.yml file ?",
                default=True
            ).execute()
            if not do_not_erase:
                operation.logger.info("You have chosen to not overwrite existing scope configuration file, exiting")
                sys.exit()

        ### render config file
        content = config_template.render(template_data)

        # dump config file
        config_file = os.path.join(scope_folder, "config.yml")
        with open(config_file, mode="w", encoding="utf-8") as configfile:
            configfile.write(content)
            operation.logger.info(f"Created config file for scope {scope}")

def manifest(operation: Operation, deployment_mode):

    """ this function prompt an interactive definition of a platform manifest
    
    :param operation: Operation, the current Operation
    """

    # set the folder to browse for a platform manifest
    default_manifest_folder = "./manifests"
    manifest_folder = inquirer.text(
        message = "Please provide the manifest folder to browse, relative to your current project root folder",
        default = default_manifest_folder,
        validate = PathValidator(is_dir=True, message="Input is not a folder")
    ).execute()

    # browse manifest folder for a platform manifest
    platformManifestChoices = []
    for file in os.listdir(manifest_folder):
        if (file.endswith(".yml")) :
            platformManifestChoices.append(Choice(value=file, name=file,enabled=False))

    platform_manifest_file = inquirer.select(
        message="Select the platform manifest to start from:",
        choices=platformManifestChoices,
        multiselect=False,
        default=None,
    ).execute()
    platform_manifest_file = os.path.join(manifest_folder, platform_manifest_file)

    platform_manifest = {}
    with open(platform_manifest_file, "r") as file:
        platform_manifest = yaml.load(file, Loader=yaml.FullLoader)

    if "vm_types" in platform_manifest.get("infrastructure", {}).keys():
        operation.standard_config["vm_types"] = platform_manifest["infrastructure"]["vm_types"]

    # activate/deactivate modules for the platform
    module_choices = platform_manifest.get("modules", [])
    module_choices = [
        Choice(value = module['id'], name = module['name'], enabled = True) for module in module_choices
    ]
    activated_modules = inquirer.select(
        message="Which modules would you like to include in the platform :",
        choices=module_choices,
        multiselect=True,
        default=None,
    ).execute()
    activated_modules.append("dependencies")

    # activate/deactivate components for the platform
    component_list = platform_manifest.get("components", [])
    activated_components = []
    for module in activated_modules:
        component_choices = [
            Choice(value = component['id'], name = component['name'] + " " + component["version"], enabled = True) for component in component_list if component.get("module", "") == module
        ]
        module_text = f"module {module}"
        if module == "dependencies":
            module_text = "platform dependencies"
        if len(component_choices)>0 :
            activated_components_per_module = inquirer.select(
                message=f"Which component would you like to include for {module_text} :",
                choices=component_choices,
                multiselect=True,
                default=None,
            ).execute()
            activated_components += activated_components_per_module

    # customize platform
    customization = {}
    for module, module_content in platform_manifest.get("customization", {}).items():
        if module in activated_modules:
            customization[module] = {}
            for parameter in module_content:
                if (parameter.get("deployment_mode", deployment_mode) == deployment_mode):
                    if parameter.get("type", "text") == "boolean":
                        customization[module][parameter["name"]] = inquirer.confirm(
                                message=parameter["prompt"],
                                default=False
                        ).execute()
                    if parameter.get("type", "text") == "text":
                        customization[module][parameter["name"]] = inquirer.text(
                            message = parameter["prompt"],
                            default = parameter["default_value"]
                        ).execute()
                    if parameter.get("type", "text") == "secret":
                        customization[module][parameter["name"]] = inquirer.secret(
                            message = parameter["prompt"]
                        ).execute()

    # load custom credentials
    custom_credentials = {}
    for custom_credential_name, custom_credential in operation.standard_config.get("custom_credentials", {}).items():
        custom_credentials[custom_credential_name] = custom_credential

    deploy_manifest = {
        "manifest" : platform_manifest,
        "activated_modules" : activated_modules,
        "activated_components" : activated_components,
        "customization" : customization,
        "custom_credentials" : custom_credentials,
        "pvs_suffix" : pvs_suffix,
        "deployment_mode": deployment_mode
    }

    return deploy_manifest

def deploy(operation: Operation):

    # INFRASTRUCTURE PART
    scope_folder = os.path.join(operation.project_root, "config", operation.scope)

    deploy_file = os.path.join(scope_folder, "deploy.yml")
    if not os.path.exists(deploy_file):
        operation.logger.error(f"ERROR : the file {deploy_file} does not exist !")
        sys.exit()

    content = {}
    with open(deploy_file, "r") as deployfile:
        manifest_data = yaml.load(deployfile, Loader=yaml.FullLoader)

    # template_data = content.get("infrastructure", {})
    # manifest_data = content.get("configuration_management", {})
    template_data = manifest_data['config']

    deployment_mode = manifest_data.get("deployment_mode", "internal")

    # get config template from internal catalog
    config_template_dir = os.path.join(
        operation.libraries_path, "internal", "config")
    environment = Environment(
        loader=FileSystemLoader(config_template_dir),
        trim_blocks=True
    )
    config_template = environment.get_template("config.yml.j2")

    # CONFIGURATION MANAGEMENT PART
    # set the folder to browse for a platform manifest ansible template
    default_ansible_folder = "./manifests"
    ansible_folder = inquirer.text(
        message = "Please provide the platform ansible template folder to browse, relative to your current project root folder",
        default = default_ansible_folder,
        validate = PathValidator(is_dir=True, message="Input is not a folder")
    ).execute()

    ansible_template_file = inquirer.select(
        message="Select the ansible template to use:",
        choices=[
            Choice(value="internal", name="internal"),
            Choice(value="external", name="external")
        ],
        multiselect=False,
        default=deployment_mode,
    ).execute()
    ansible_template_file = ansible_template_file + ".ansible.yml.j2"

    if not os.path.exists(os.path.join(ansible_folder, ansible_template_file)):
        operation.logger.info(f"The ansible template {ansible_template_file} does not exist, please provide one before generating a config file for a platform")
        sys.exit()

    # get ansible template
    environment = Environment(
        loader=FileSystemLoader(ansible_folder),
        trim_blocks=True
    )
    ansible_template = environment.get_template(ansible_template_file)

    # RENDERING
    ansible_template_file = deployment_mode + ".ansible.yml.j2"
    ansible_template = environment.get_template(ansible_template_file)

    # render config template
    content = config_template.render(template_data)
    ansible_content = ansible_template.render(manifest_data)

    # dump config file
    config_file = os.path.join(scope_folder, "config.yml")
    with open(config_file, mode="w", encoding="utf-8") as configfile:
        configfile.write(content)
        configfile.write(ansible_content)
        operation.logger.info(f"Created config file for scope {operation.scope}")