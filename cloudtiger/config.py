""" Config operations for CloudTiger """
from jinja2 import Environment, FileSystemLoader
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator, EmptyInputValidator, PathValidator
import os
import sys
import json
from colored import Fore, Back, Style

from cloudtiger.cloudtiger import Operation
from cloudtiger.data import common_environments, common_internal_customers, worldwide_cloud_datacenters, clusterized_hypervisors
from cloudtiger.specific.vsphere import check_folder_exists_vsphere

def generate(operation: Operation):

    """ this function prompt an interactive definition of a scope/config
    
    :param operation: Operation, the current Operation
    """

    config_content = {}

    # get config template from internal catalog
    config_template_dir = os.path.join(
        operation.libraries_path, "internal", "config")
    environment = Environment(
        loader=FileSystemLoader(config_template_dir),
        trim_blocks=True
    )
    config_template = environment.get_template("config.yml.j2")

    # choose main cloud provider
    provider = inquirer.select(
        message="Which Cloud Provider would you like to use:",
        choices=[
            Choice(value="nutanix", name="Nutanix Hyper-Converged Infrastructure",enabled=True),
            Choice(value="vsphere", name="VMware ESXi",enabled=False),
            Choice(value="proxmox", name="Proxmox VE",enabled=False),
            Choice(value="aws", name="Amazon AWS",enabled=False),
            Choice(value="azure", name="Microsoft Azure",enabled=False),
            Choice(value="gcp", name="Google Cloud Services",enabled=False),
        ],
        multiselect=False,
        default=None,
    ).execute()

    # do you have secondary cloud providers on your network ?
    have_secondary_providers = inquirer.confirm(
        message="Do you have secondary cloud providers sharing your network ?",
        default=False
    ).execute()
    secondary_providers = []

    # provide secondary cloud providers
    while have_secondary_providers:
        secondary_provider = inquirer.select(
        message="Which Secondary Cloud Provider would you like to add:",
        choices=[
            Choice(value="nutanix", name="Nutanix Hyper-Converged Infrastructure",enabled=True),
            Choice(value="vsphere", name="VMware ESXi",enabled=False),
            Choice(value="proxmox", name="Proxmox VE",enabled=False),
            Choice(value="aws", name="Amazon AWS",enabled=False),
            Choice(value="azure", name="Microsoft Azure",enabled=False),
            Choice(value="gcp", name="Google Cloud Services",enabled=False),
        ],
        multiselect=False,
        default=None,
    ).execute()

        secondary_providers.append(secondary_provider)

        have_secondary_providers = inquirer.confirm(
        message="Do you want to add an extra secondary provider ?",
        default=False
    ).execute()

    # cloud region
    region = "datacenter"
    cloud_regions = []
    if provider in worldwide_cloud_datacenters.keys():
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
    # customer_choices = ["custom"] + customer_choices
    chosen_customer = inquirer.select(
        message = "Choose a customer for your scope:",
        choices = customer_choices,
        multiselect=False,
        default = None
    ).execute()
    if chosen_customer == "custom":
        chosen_customer = inquirer.text(
            message = "Please provide the exact name of your customer"
        ).execute()

    # define environment
    environments_choices = [
        Choice(value=environment, name=environment, enabled=False) for environment in common_environments
    ]
    environments_choices.append("custom")
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

    # define scope
    default_scope = os.path.join(provider, chosen_customer, 
                                 chosen_environment)
    
    scope = inquirer.text(message="Provide the path of the scope you want to create, excluding the 'config' folder:", 
                          default=default_scope).execute()

    # do you want to add SSH keys from a repository ?
    add_ssh_keys_from_repo = inquirer.confirm(
        message="Do you want to add SSH keys from a repository ?",
        default=("artefacts_repository_admin_user_list" in operation.standard_config.keys())
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
        default=("nameservers" in operation.standard_config.keys())
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
        default=("search" in operation.standard_config.keys())
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
    default_os = "default_os"
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
            default = None
        ).execute()

    # define a default folder for VMs - for vsphere provider only
    default_folder = os.path.join(chosen_customer, chosen_environment)
    if provider == "vsphere":
        set_default_folder = inquirer.confirm(
            message="Do you want to set default vsphere folder for all the VMs of your scope ?",
            default=True
        ).execute()
        if set_default_folder:
            default_folder = inquirer.text(
                message = "Set a default vsphere folder for your scope:",
                default = default_folder
            ).execute()
            # if not check_folder_exists_vsphere(operation, default_folder):
            #     operation.logger.info("Error : the folder you have specified does not exist - create it in the vSphere UI before creating config file")
            #     sys.exit()

    # define default specific resources for VMs - for vsphere provider only
    vsphere_specific_resources = {}
    if provider == "vsphere":
        for resource in ["cluster", "datacenter", "datastore"]:
            set_default_resource = inquirer.confirm(
                message=f"Do you want to set default {resource} for all the VMs of your scope ?",
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

    # # define a default folder for VMs - for vsphere provider only
    # default_folder = "."
    # if len(operation.scope.split(os.sep)) > 2:
    #     default_folder = os.path.join(operation.scope.split(os.sep)[2:])
    # if provider == "vsphere":
    #     set_default_folder = inquirer.confirm(
    #         message="Do you want to set default vsphere folder for all the VMs of your scope ?",
    #         default=True
    #     ).execute()
    #     if set_default_folder:
    #         default_folder = inquirer.text(
    #             message = "Set a default vsphere folder for your scope:",
    #             default = default_folder
    #         ).execute()

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

    # choose subnet
    add_subnet = True
    network = { operation.provider + "_network" : {"subnets" : {}} }
    subnet_choices = [
        Choice(value=subnet_name, name=subnet_name) for subnet_name, subnet in subnet_data.items()
    ]

    while add_subnet:
        added_subnet = inquirer.select(
            message = "Choose a subnet for your scope",
            choices = subnet_choices,
            multiselect = False,
            default=None
        ).execute()

        network[operation.provider + "_network"]['subnets'][added_subnet] = subnet_data[added_subnet]

        # ask if network is Terraform-managed
        not_terraform_managed = inquirer.confirm(
            message="Is this subnet created outside of current scope ?",
            default=True
        ).execute()

        network[operation.provider + "_network"]['subnets'][added_subnet]['unmanaged'] = not_terraform_managed

        # ask if IPAM is activated on VLAN
        activated_ipam = inquirer.confirm(
            message="Has this subnet IPAM activated ?",
            default=True
        ).execute()

        network[operation.provider + "_network"]['subnets'][added_subnet]['managed_ips'] = activated_ipam

        # add VMs on subnet
        add_vm = True
        vm = { operation.provider + "_network" : {added_subnet : {}}}
        vm_type_choices = [
            Choice(value=vm_type_name, name=vm_type_name) for vm_type_name in operation.standard_config["vm_types"].get(provider, operation.standard_config["vm_types"]["default"]).keys()
        ]
        while add_vm:
            added_vm_type = inquirer.select(
                message = "Choose a VM type",
                choices = vm_type_choices,
                multiselect = False,
                default = None
            ).execute()

            vm_name = '-'.join([chosen_environment, added_vm_type, chosen_customer])
            vm_name = inquirer.text(
                message = "Please provide the name of your VM",
                default = vm_name
            ).execute()

            vm_sizing = inquirer.select(
                message="Which sizing for the VM:",
                choices=[
                    Choice(value="prod", name="default - prod",enabled=True),
                    Choice(value="nonprod", name="default - non prod",enabled=False),
                    Choice(value="custom", name="custom",enabled=False),
                ],
                multiselect=False,
                default=None,
            ).execute()

            vm_values = {}

            if vm_sizing in ["prod", "nonprod"]:
                vm_standard_values = operation.standard_config["vm_types"].get(provider, operation.standard_config["vm_types"]["default"])[added_vm_type][vm_sizing]
                nb_sockets = vm_standard_values["nb_sockets"]
                nb_vcpu_per_socket = vm_standard_values["nb_vcpu_per_socket"]
                memory = vm_standard_values["memory"]
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
                data_volume_size = inquirer.number(
                    message="Enter number of Go of data disk:",
                    min_allowed=0,
                    max_allowed=1000,
                    default=16,
                ).execute()
                root_volume_size = inquirer.number(
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
            if provider == "nutanix":
                vm_values['availability_zone'] = default_cluster

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

            # vsphere specific - set resources
            if provider == "vsphere":
                vsphere_vm_specific_resources = vsphere_specific_resources
                set_custom_resources = inquirer.confirm(
                    message=f"Do you want to set custom vSphere resources for this VM ?",
                    default=False
                ).execute()
                if set_custom_resources:
                    for resource in ["cluster", "datacenter", "datastore"]:
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

            vm[operation.provider + "_network"][added_subnet][vm_name] = vm_values

            # do you want to add an extra VM
            add_vm = inquirer.confirm(
                message="Do you want to add another VM ?",
                default=False
            ).execute()

        # do you want to add an extra subnet
        add_subnet = inquirer.confirm(
            message="Do you want to add another subnet ?",
            default=False
        ).execute()

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

    if have_secondary_providers:
        template_data["secondary_providers"] = secondary_providers

    if provider in worldwide_cloud_datacenters.keys():
        template_data["region"] = region

    if add_ssh_keys_from_repo:
        template_data["artefacts_repository_public_key_url"] = artefacts_repository_public_key_url
        template_data["artefacts_repository_admin_user_list"] = artefacts_repository_admin_user_list

    if len(nameservers_list) > 0:
        template_data['nameservers_list'] = nameservers_list.split(',')

    if len(search_domain_list) > 0:
        template_data['search_domain_list'] = search_domain_list.split(',')

    ### render config file
    content = config_template.render(template_data)

    ### create scope
    scope_folder = os.path.join(operation.project_root, "config", scope)

    os.makedirs(scope_folder, exist_ok=True)

    scope_file = os.path.join(scope_folder, "config.yml")

    if os.path.exists(scope_file):
        do_not_erase = inquirer.confirm(
            message="Do you want to overwrite existing config.yml file ?",
            default=True
        ).execute()
        if not do_not_erase:
            operation.logger.info("You have chosen to not overwrite existing scope configuration file, exiting")
            sys.exit()

    # dump config file
    config_file = os.path.join(scope_folder, "config.yml")
    with open(config_file, mode="w", encoding="utf-8") as configfile:
        configfile.write(content)
        operation.logger.info(f"Created config file for scope {scope}")

