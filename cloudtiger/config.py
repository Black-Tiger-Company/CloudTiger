""" Config operations for CloudTiger """
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator, EmptyInputValidator, PathValidator
import os
import json
from colored import Fore, Back, Style

from cloudtiger.cloudtiger import Operation
from cloudtiger.data import common_environments, common_internal_customers

def generate(operation: Operation):

    """ this function prompt an interactive definition of a scope/config
    
    :param operation: Operation, the current Operation
    """

    config_content = {}

    # choose main cloud provider
    provider = inquirer.select(
        message="Which Cloud Provider would you like to use:",
        choices=[
            Choice(value="nutanix", name="Nutanix Hyper-Converged Infrastructure",enabled=True),
            Choice(value="vmware", name="VMware ESXi",enabled=False),
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
            Choice(value="vmware", name="VMware ESXi",enabled=False),
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

    # define environment
    environments_choices = [
        Choice(value=environment, name=environment, enabled=False) for environment in common_environments
    ]
    environments_choices.append("custom")
    chosen_environment = inquirer.select(
        message = "Choose an environment for your scope:",
        choices = chosen_environment,
        multiselect=False,
        default = None
    ).execute()
    if chosen_environment == "custom":
        chosen_environment = inquirer.text(
            message = "Please provide the exact name of your environment"
        ).execute()

    # define customer
    customer_list = operation.standard_config.get("customers", common_internal_customers)
    customer_choices = [
        Choice(value=customer, name=customer, enabled=False) for customer in customer_list
    ]
    customer_choices.append("custom")
    chosen_customer = inquirer.select(
        message = "Choose a customer for your scope:",
        choices = chosen_customer,
        multiselect=False,
        default = None
    ).execute()
    if chosen_customer == "custom":
        chosen_customer = inquirer.text(
            message = "Please provide the exact name of your customer"
        ).execute()

    # do you want to add SSH keys from a repository ?
    add_ssh_keys_from_repo = inquirer.confirm(
        message="Do you want to add SSH keys from a repository ?",
        default=False
    ).execute()

    if add_ssh_keys_from_repo:
        # provide path to public SSH keys repository
        artefacts_repository_admin_user_list = os.environ.get("CLOUDTIGER_ARTEFACTS_REPOSITORY_ADMIN_USER_LIST", "")
        artefacts_repository_public_key_url = os.environ.get("CLOUDTIGER_ARTEFACTS_REPOSITORY_PUBLIC_KEY_URL", "")
        artefacts_repository_admin_user_list = inquirer.text(
                message="Provide the URL for the admin users list on an artefacts repository:",
                default=artefacts_repository_admin_user_list
            ).execute()
        
        artefacts_repository_public_key_url = inquirer.text(
                message="Provide the URL for the admin users public SSH keys on an artefacts repository:",
                default=artefacts_repository_public_key_url
            ).execute()

    # get subnets data
    subnet_data = {}
    if operation.provider == "nutanix":
        subnet_data = {
            subnet.get("spec", {}).get("name", "missing_vlan_name"):
            {
                "name": subnet.get("spec", {}).get("name", "missing_vlan_name"),
                "cidr_block": subnet.get("spec", {}).get("resources").get("ip_config", {}).get("subnet_ip", "192.168.0.0") + "/" + subnet.get("spec", {}).get("resources").get("ip_config", {}).get("prefix_length", "32"),
                "id" : subnet.get("spec", {}).get("resources").get("vlan_id", 0),
                "default_gateway_ip": subnet.get("spec", {}).get("resources").get("ip_config", {}).get("default_gateway_ip", "192.168.0.1")
            } for subnet in operation.all_network_info.get("nutanix_network", {}).get("subnets", [])
        }

    # choose subnet
    add_subnet = True
    network = { operation.provider + "_network" : {"subnets" : {}} }
    subnet_choices = [
        Choice(value=subnet, name=subnet_name) for subnet, subnet_name in subnet_data.items()
    ]

    while add_subnet:
        added_subnet = inquirer.select(
            message = "Choose a subnet for your scope",
            choices = subnet_choices,
            multiselect = False,
            default=None
        ).execute()

        network[operation.provider + "_network"]['subnets'][added_subnet['name']] = added_subnet.pop('name')

        # ask for nameservers
        add_dns_servers = inquirer.confirm(
            message="Do you want to add DNS servers for VMs on this subnet ?",
            default=False
        ).execute()

        if add_dns_servers:
            list_of_nameserver = os.environ.get("CLOUDTIGER_NAMESERVERS", [])
            list_of_nameserver = inquirer.text(
                message = "Provide a list of comma-separated IP addresses for your DNS servers",
                default = ",".join(list_of_nameserver)
            ).execute()

            network[operation.provider + "_network"]['subnets'][added_subnet['name']]['nameservers'] = list_of_nameserver

        # ask for search domains
        add_search_domains = inquirer.confirm(
            message="Do you want to add search domains for VMs on this subnet ?",
            default=False
        ).execute()

        if add_search_domains:
            list_of_search_domains = os.environ.get("CLOUDTIGER_SEARCH_DOMAINS", [])
            list_of_search_domains = inquirer.text(
                message = "Provide a list of comma-separated IP addresses for your DNS servers",
                default = ",".join(list_of_search_domains)
            ).execute()

            network[operation.provider + "_network"]['subnets'][added_subnet['name']]['search'] = list_of_search_domains

        # ask if network is Terraform-managed
        not_terraform_managed = inquirer.confirm(
            message="Is this subnet created outside of current scope ?",
            default=True
        ).execute()

        network[operation.provider + "_network"]['subnets'][added_subnet['name']]['unmanaged'] = not_terraform_managed

        # ask if IPAM is activated on VLAN
        activated_ipam = inquirer.confirm(
            message="Has this subnet IPAM activated ?",
            default=True
        ).execute()

        network[operation.provider + "_network"]['subnets'][added_subnet['name']]['managed_ips'] = activated_ipam

        # add VMs on subnet
        add_vm = True
        vm = { operation.provider + "_network" : {added_subnet['name'] : {}}}
        vm_type_choices = [
            Choice(value={"name":vm_type_name,"type":vm_type}, name=vm_type_name) for vm_type_name, vm_type in operation.standard_config["vm"].items()
        ]
        while add_vm:
            added_vm_type = inquirer.select(
                message = "Choose a VM type",
                choices = vm_type_choices,
                multiselect = False,
                default = None
            ).execute()

            vm_name = '-'.join([chosen_environment, added_vm_type["name"], chosen_customer])
            vm_name = inquirer.text(
                message = "Please provide the name of your VM",
                default = vm_name
            ).execute()

            vm[operation.provider + "_network"][added_subnet['name']][vm_name] = added_vm_type["type"]

        # do you want to add an extra subnet
        add_subnet = inquirer.confirm(
            message="Do you want to add another subnet ?",
            default=False
        ).execute()

    # do you plan to use a Terraform backend
    use_tf_backend = inquirer.confirm(
        message="Do you want to use a remote Terraform backend ?",
        default=False
    ).execute()

