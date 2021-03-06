"""Main module."""

import copy
import json
import os
import sys
from logging import Logger

import pkg_resources
import yaml
from cloudtiger.common_tools import load_yaml, bash_source, merge_dictionaries
from cloudtiger.data import available_infra_services

LIBRARIES_PATH = pkg_resources.resource_filename('cloudtiger', 'libraries')


class Operation:
    """
    A class to store information and data about a CloudTiger operation.

    Attributes
    ----------
    logger: Logger
        a Logger object to log operation's steps
    project_root: str
        the root folder ("gitops") for executing CloudTiger
    scope: str
        the name of the current scope (including path separators)
    libraries_path: str
        the path to the folder of Ansible and Terraform libraries (by default)
        the sources of CloudTiger
    stdout_file: str
        the path of the file where standard output will be dumped
    stderr_file: str
        the path of the file where standard error will be dumped
    consolidated: bool
        set to True if we are in consolidated mode (= all VMs, no Terraform,
        Ansible only)
    default_user: bool
        set to True if we access the VM with SSH using the default OS user instead
        of a named user
    ansible_force_install: bool
        set to True if you want to apply the '--force' option to Ansible when installing
        the role requirements
    restricted_vms: str
        specify a list of the VMs when you want to target then specifically when running
        an Ansible action
    ssh_port: str
        the default SSH port for Ansible access
    tf_no_lock: bool
        set to True if you want to run Terraform action with the '-no-lock' option
    scope_config_folder: str
        the absolute path to the folder containing the current scope
    scope_config: str
        the absolute path to the config.yml file of the current scope
    scope_meta_config: str
        the absolute path to the meta_config.yml file of the current meta scope
    scope_config_dict: dict
        the dictionary of the content of config.yml
    used_services: list
        the list of infrastructure services set in config.yml (network, vm, iam, kubernetes, etc)
    provider: str
        the chosen provider
    terraform_output: str
        the absolute path to the 'terraform_output.json' file associated with the current scope
    scope_inventory_folder: str
        the absolute path to the folder '<PROJECT_ROOT>/scopes/<SCOPE>/inventory
    scope_terraform_folder: str
        the absolute path to the folder '<PROJECT_ROOT>/scopes/<SCOPE>/terraform'
    standard_config: dict
        a dictionary of standard VMs and network configurations, merged from CloudTiger
        sources and gitops folder
    vm_type_provider: str
        same value as provider, except if the provider is not listed in the 'standard_config'.
        In this case, will be 'default'
    ssh_no_check: bool
        set to True if you want to deactivate SSH fingerprint when connecting to the VMs
    terraform_vm_data: dict
        dictionary storing the content of the 'terraform_output.json' file
        if it exists
    datacenter_meta_folder: str
        absolute path to the 'meta' folder of the datacenter (used in combination with the
        'consolidated' option)
    network_info: dict
        dictionary storing the content of the 'all_networks.yml' file (used in combination
        with the 'consolidated' option)
    addresses_info: dict
        dictionary storing the content of the 'all_addresses.yml' file (used in combination
        with the 'consolidated' option)

    Methods
    -------
    scope_setup()
        set internal parameters of the Operation
    secrets_setup()
        read and set secrets for the providers and/or services
    set_ansible_options()
        set options specific to Ansible
    set_restricted_vms()
        restrict Ansible operations to specific VMs
    set_terraform_output_info()
        loads the mapping vm/address from the
        scopes/<SCOPE>/inventory/terraform_output.json file
    load_meta_info()
        loads the meta information when executing ansible
        with the --consolidated option
    load_ips()
        loads the IPs listed in config_ips.yml into
        the scope_config_dict in memory
    devops_init()
        overrides the ansible action defined in the config.yml to enforce
        the devops init role
    """

    def __init__(self,
                 logger: Logger,
                 project_root: str,
                 scope: str,
                 libraries_path: str,
                 stdout_file,
                 stderr_file
                 ):
        self.logger = logger

        # we ensure a well-defined project root folder
        if project_root == ".":
            self.project_root = os.getcwd()
        else:
            self.project_root = project_root

        # ensure robustness to whitespaces
        if "\\ " in self.project_root:
            self.project_root = "'" + self.project_root + "'"

        # if the first folder of scope is 'config', we remove it from the scope path 
        # - this behavior is meant to facilitate autocompletion on scope path"""
        scope_elts = scope.split(os.sep)
        if (scope_elts[0] == "config") & (len(scope_elts) > 1):
            self.logger.debug("Removing 'config' from scope path")
            scope = os.path.join(*(scope_elts[1:]))
            self.logger.debug("New scope path is %s" % scope)

        # set Operation values for scope
        self.scope = scope
        self.libraries_path = libraries_path
        if self.libraries_path is None:
            self.libraries_path = LIBRARIES_PATH
        self.stdout_file = stdout_file
        self.stderr_file = stderr_file

        # set default values for an Operation

        # consolidated Ansible access"""
        self.consolidated = False

        # access with default VM user using SSH
        self.default_user = False

        # force installation of Ansible dependencies
        self.ansible_force_install = False

        # Ansible actions restricted to some hosts only
        self.restricted_vms = None

        # default ssh port
        self.ssh_port = "22"

        # Terraform state lock
        self.tf_no_lock = False

    def scope_setup(self):

        """ this function set intermediate internal parameters for the current scope
        """
        self.logger.debug("Loading .env from project root folder")

        root_env = os.path.join(self.project_root, ".env")
        if os.path.exists(root_env):
            bash_source(self.logger, root_env)
        else:
            self.logger.warning("WARNING: cannot read .env file at project root folder:\
                file does not exist")

        # parameters that will be set in the terraform vars files in scopes/<SCOPE>/terraform folder
        self.scope_config_folder = os.path.join(self.project_root, 'config', self.scope)
        self.scope_config = os.path.join(self.project_root, 'config', self.scope, 'config.yml')
        self.scope_meta_config = os.path.join(
            self.project_root, 'config', self.scope, 'meta_config.yml')

        if not os.path.exists(self.scope_config):
            self.logger.warning(
                "WARNING: The %s file does not exist, testing meta_config.yml" % self.scope_config)
            self.scope_config = self.scope_meta_config
            if not os.path.exists(self.scope_meta_config):
                self.logger.warning("WARNING: The %s file does not exist either" % self.scope_config)

        # get config values
        try:
            self.scope_config_dict = load_yaml(self.logger, self.scope_config)
            # let us check if the config file is empty
            if self.scope_config_dict is None:
                self.scope_config_dict = {}
        except Exception:
            self.logger.error(
                "Failed to load the data from %s file:\
                    the file is probably badly formated" % self.scope_config)
            self.scope_config_dict = {}
        self.scope_config_dict["scope"] = self.scope

        # extract list of used services - check if they are required in the config.yml file
        self.used_services = []
        for service in available_infra_services:
            if service in self.scope_config_dict.keys():
                service_kind = self.scope_config_dict[service]
                if isinstance(service_kind, dict):
                    if ~(len(service_kind.keys()) > 0):
                        pass
                if isinstance(service_kind, list):
                    if ~(len(service_kind) > 0):
                        pass
                self.used_services.append(service)

        # set scopes values
        self.provider = self.scope_config_dict.get('provider', 'admin')
        self.logger.debug("Provider is %s" % self.provider)
        self.scope_config_dict["ssh_key_path"] = self.scope_config_dict\
            .get('ssh_key_name',
                 os.environ.get("CLOUDTIGER_PRIVATE_SSH_KEY_PATH", "missing"))
        self.logger.debug("SSH Key path is %s" % self.scope_config_dict["ssh_key_path"])

        # set recurrent intermediate variables
        self.scope_folder = os.path.join(self.project_root, "scopes", self.scope)
        self.terraform_output = os.path.join(
            self.project_root, "scopes", self.scope, "inventory", "terraform_output.json")
        self.scope_inventory_folder = os.path.join(self.scope_folder, "inventory")
        self.scope_terraform_folder = os.path.join(self.scope_folder, "terraform")
        # self.scope_data_folder = os.path.join(self.scope_folder, "data")
        # self.scope_dedicated_config_folder = os.path.join(self.scope_folder, "config")

        # set standard VM spec values
        cloudtiger_standard_file = os.path.join(
            self.libraries_path, "internal", "standard", "vm_standard.yml")
        cloudtiger_standard_config = load_yaml(self.logger, cloudtiger_standard_file)
        local_standard_file = os.path.join(self.project_root, "standard", "standard.yml")
        if os.path.exists(local_standard_file):
            local_standard_config = load_yaml(self.logger, local_standard_file)
        else:
            local_standard_config = {}
        self.standard_config = merge_dictionaries(cloudtiger_standard_config, local_standard_config)

        # set provider alias for standard configuration
        if self.provider in self.standard_config["vm_types"].keys():
            self.vm_type_provider = self.provider
        else:
            self.vm_type_provider = "default"

        # this function unpacks the map of vms
        unpacked_vms = [
            (vm_name, network_name, subnet_name, vm.get("group", "ungrouped").split(","))
            for network_name, network_subnets in self.scope_config_dict.get('vm', {}).items()
            for subnet_name, subnet_vms in network_subnets.items()
            for vm_name, vm in subnet_vms.items()
            ]

        self.scope_config_dict["unpacked_vms"] = unpacked_vms

    def secrets_setup(self):

        """ this function collects values from the secrets files
        """

        self.logger.debug("Loading secrets from various providers/services")

        # load credentials for provider
        provider_account = self.scope_config_dict.get('provider_account', "")
        provider_secret = os.path.join(
            self.project_root, "secrets", self.provider, provider_account + '.env')
        if os.path.exists(provider_secret):
            bash_source(self.logger, provider_secret)

        else:
            err = format("Cannot read %s file at project root folder: "
                         "file does not exist" % provider_secret)
            self.logger.error(err)

        # load credentials for services
        services_account = self.scope_config_dict.get("services_account", {})
        for service_name, account_name in services_account.items():
            service_secret = os.path.join(
                self.project_root, "secrets", service_name, account_name + '.env')
            if os.path.exists(service_secret):
                bash_source(self.logger, service_secret)

            else:
                err = format("Cannot read %s file at project secrets folder:\
                    file does not exist" % service_secret)
                self.logger.error(err)

    def set_ansible_options(self,
                            consolidated=False,
                            default_user=False,
                            ansible_force_install=False,
                            restricted_vms=None,
                            ssh_port="22",
                            no_check=False
                            ):

        """ this function set specific attributes for ansible connection
        """

        # consolidated Ansible access"""
        self.consolidated = consolidated

        # access with default VM user using SSH
        self.default_user = default_user

        # force installation of Ansible dependencies
        self.ansible_force_install = ansible_force_install

        # Ansible actions restricted to some hosts only
        self.restricted_vms = restricted_vms

        # default ssh port
        self.ssh_port = ssh_port

        # proceed to fingerprint check when SSHing ?
        self.ssh_no_check = no_check

    def set_restricted_vms(self):

        """ this function restrict the ansible action to a subset of VMs
        """

        # restrict Ansible operations on specific VMs
        if isinstance(self.restricted_vms, str):
            restricted_vms = self.restricted_vms.split(",")
            self.logger.info("Restricting operation to VMs %s" % self.restricted_vms)
            restricted_vms_dict = copy.deepcopy(self.scope_config_dict['vm'])
            for network_name, network_subnets in self.scope_config_dict['vm'].items():
                for subnet_name, subnet_vms in network_subnets.items():
                    for vm_name, _ in subnet_vms.items():
                        if vm_name not in restricted_vms:
                            restricted_vms_dict[network_name][subnet_name].pop(vm_name)
            self.scope_config_dict['vm'] = restricted_vms_dict
            restricted_unpacked_vms = [(vm_name, network_name, subnet_name, group)
                                       for (vm_name, network_name, subnet_name, group)
                                       in self.scope_config_dict["unpacked_vms"]
                                       if vm_name in restricted_vms
                                       ]
            self.scope_config_dict["unpacked_vms"] = restricted_unpacked_vms

    def set_terraform_output_info(self):

        """ this function loads the mapping vm/address from the
        scopes/<SCOPE>/inventory/terraform_output.json file
        """

        terraform_vm_data = {}
        if os.path.isfile(self.terraform_output):
            with open(self.terraform_output, 'r') as f:
                terraform_output_data = json.load(f)

            for vm_name, vm_data in terraform_output_data.get("vms", {}).get("value", {}).items():
                if vm_data["private_ip"] not in ["", "not_learned_yet"]:
                    terraform_vm_data[vm_name] = vm_data

        self.terraform_vm_data = terraform_vm_data

    def load_meta_info(self):

        """ this function loads the meta information when executing ansible
        with the --consolidated option
        """

        datacenter_root_folder = os.path.join(self.project_root, 'config', self.scope.split(os.sep)[0])
        datacenter_subroot_folders = os.listdir(datacenter_root_folder)
        self.datacenter_meta_folder = '_meta'
        for folder in datacenter_subroot_folders:
            if '_meta' in folder:
                self.datacenter_meta_folder = os.path.join(datacenter_root_folder, folder)
                break

        networks_info_file = os.path.join(self.datacenter_meta_folder, 'all_networks.yml')
        with open(networks_info_file, "r") as f:
            self.network_info = yaml.load(f, Loader=yaml.FullLoader)

        addresses_info_file = os.path.join(self.datacenter_meta_folder, 'all_addresses_info.yml')
        with open(addresses_info_file, "r") as f:
            self.addresses_info = yaml.load(f, Loader=yaml.FullLoader)

    def load_ips(self):

        """ this function loads the IPs listed in config_ips.yml into
        the scope_config_dict in memory
        """

        scope_ips = os.path.join(self.scope_config_folder, 'config_ips.yml')
        if os.path.exists(scope_ips):
            with open(scope_ips, 'r') as f:
                config_ip = yaml.load(f, Loader=yaml.FullLoader)
        else:
            self.logger.critical("Missing config_ips.yml file, please run cloudtiger <SCOPE> init 1")
            sys.exit()

        for network_name, network_subnets in self.scope_config_dict["vm"].items():
            for subnet_name, subnet_vms in network_subnets.items():
                for vm_name, address in subnet_vms.items():
                    address = config_ip[network_name][subnet_name]["addresses"][vm_name]
                    self.scope_config_dict["vm"][network_name][subnet_name][vm_name]["private_ip"] = address

        unpacked_ips = {
            vm_name: ip_address
            for network_name, network_subnets in config_ip.items()
            for subnet_name, subnet_vms in network_subnets.items()
            for vm_name, ip_address in subnet_vms["addresses"].items()
        }

        self.scope_unpacked_ips = unpacked_ips

    def devops_init(self):

        """ this function overrides the ansible action defined in the config.yml to enforce
        the devops init role
        """

        artefacts_repository_public_key_url = self.scope_config_dict\
            .get("artefacts_repository_public_key_url", "unset_repo_url")

        if artefacts_repository_public_key_url == "unset_repo_url":
            self.logger.critical("The artefacts repository URL has not been configured")
            sys.exit()

        self.scope_config_dict["ansible"] = [
            {
                "name": "devops init",
                "type": "role",
                "sudo_prompt": "true",
                "hosts": "all",
                "roles": [
                    {
                        "source": "devops-init",
                        "params": {
                            "become": "true",
                            "nexus_base_pkey": artefacts_repository_public_key_url
                        }
                    }
                ]
            }
        ]
