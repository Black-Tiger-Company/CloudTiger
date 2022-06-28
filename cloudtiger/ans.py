"""Ansible operations for CloudTiger."""
import os
import shutil
import getpass
import base64
from typing import Tuple

import yaml
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import bash_action, j2, load_yaml
from cloudtiger.data import (
    DEFAULT_ANSIBLE_PYTHON_INTERPRETER,
    DEFAULT_SSH_PORT,
    common_group_names,
    common_environment_tags
)


def infer_group_env(vm_name: str, subnet_name: str) -> Tuple[str, str, str]:

    """ this function tries to infer group and environment for vm according to its name
    and its subnet name

    :param vm_name: str, the name of the vm
    :param subnet_name: str, the subnet name

    :return (str, str, str), the infered group, infered environment and infered owner
    """

    elts = vm_name.split('-')

    # we remove numbers from the first element
    infered_group = elts[0]
    infered_group = "".join([i for i in infered_group if not i.isdigit()])

    group = "ungrouped"
    for common_group_name in common_group_names:
        if infered_group in common_group_name:
            group = common_group_name
            break

    env = "uncharted"
    for common_environment_tag, content in common_environment_tags.items():
        if (elts[0] in common_environment_tag) | (subnet_name in common_environment_tag):
            env = content
            break

    owner = "internal"
    if len(elts) > 1:
        owner = elts[-1]

    return group, env, owner


def extract_ssh_port(vm_address: str) -> str:

    """ this function extracts a SSH port from the VM address as provided in the
    all_addresses_info.yml file

    :param vm_address: str, the name of the vm

    :return str, the SSH port for the VM
    """

    elts = vm_address.split(':')

    if len(elts) > 1:
        if elts[-1].isdigit():
            return elts[-1]

    return DEFAULT_SSH_PORT


def load_ssh_parameters_meta(operation: Operation):

    """ this function computes the parameters for the ssh.cfg file when CloudTiger
    is called with the '--consolidated' option. In this case, information is
    extracted from the 'all_addresses_info.yml

    :param operation: Operation, the current Operation
    """

    # loading meta IP information data
    operation.load_meta_info()

    operation.scope_config_dict["vm_ssh_params"] = {}
    default_os_user = operation.scope_config_dict.get("default_os_user", "ubuntu")
    for subnet_name, subnet_vms in operation.addresses_info['vm_ips'].items():
        for vm_name, vm_ip in subnet_vms["addresses"].items():
            group, env, owner = infer_group_env(vm_name, subnet_name)
            operation.scope_config_dict["vm_ssh_params"][vm_name] = {
                "private_ip": vm_ip.split(':')[0],
                "group": group,
                "os_user": default_os_user,
                "standard_user": os.environ["CLOUDTIGER_SSH_USERNAME"],
                "ssh_port": extract_ssh_port(vm_ip),
                "env": env,
                "ansible_python_interpreter": DEFAULT_ANSIBLE_PYTHON_INTERPRETER,
                "owner": owner
            }

    # replace the unpacked VMs
    unpacked_vms = [
        (vm_name, "blank_network", subnet_name,
         [operation.scope_config_dict["vm_ssh_params"][vm_name]["group"]])
        for subnet_name, subnet_vms in operation.addresses_info['vm_ips'].items()
        for vm_name, vm_ip in subnet_vms["addresses"].items()
        ]

    operation.scope_config_dict["unpacked_vms"] = unpacked_vms

    # replace the unpacked IPs
    unpacked_ips = {
        vm_name: vm_ip
        for _, subnet_vms in operation.addresses_info['vm_ips'].items()
        for vm_name, vm_ip in subnet_vms["addresses"].items()
    }

    operation.scope_unpacked_ips = unpacked_ips


def load_ssh_parameters(operation: Operation):

    """ this function modify the operation.scope_config_dict in order
    to load it with necessary parameters to setup the ssh.cfg file

    :param operation: Operation, the current Operation

    :return: empty return
    """

    # loading IP information data
    operation.load_ips()

    # here we get the mapping VM / ssh parameters
    operation.scope_config_dict["vm_ssh_params"] = {}
    default_os_user = operation.scope_config_dict.get("default_os_user", "ubuntu")
    for network_name, network_subnets in operation.scope_config_dict['vm'].items():
        for subnet_name, subnet_vms in network_subnets.items():
            for vm_name, vm in subnet_vms.items():
                operation.scope_config_dict["vm_ssh_params"][vm_name] = {
                    "private_ip": vm.get("private_ip", "unset_ip"),
                    "group" : vm.get("group", "ungrouped")
                }
                vm_system_image = vm.get("system_image", "ubuntu_server")

                # we set the OS username (used for initial SSH connexion)
                # by order of priority, the OS username for a VM should be:
                # - vm["user"]
                # - system_images[provider]["username"]
                # - default_os_user[provider]

                operation.scope_config_dict["vm_ssh_params"][vm_name]["os_user"] = \
                    vm.get(
                        "os_user",
                        operation.standard_config["system_images"][operation.provider].get(
                            vm_system_image, {"username": default_os_user}
                        )["username"]
                    )

                # we set the SSH port for the machine
                # by order of priority, the SSH port should be :
                # - custom_ssh_parameters["ssh_ports"][vm_name]
                # - operation.scope_config_dict["vm"][vm_name]
                # ["extra_parameters"]["custom_ssh_port"]

                operation.scope_config_dict["vm_ssh_params"][vm_name]["ssh_port"] = \
                    operation.scope_config_dict.get(
                        "custom_ssh_parameters", {}).get(
                            "ssh_ports", {}).get(
                                vm_name,
                                operation.scope_config_dict\
                                    ["vm"][network_name][subnet_name][vm_name].get(
                                        "extra_parameters", {}).get(
                                            "custom_ssh_port", DEFAULT_SSH_PORT))

                # we set the standard SSH username
                # by order of priority, the standard username for a VM should be :
                # - custom_ssh_parameters["usernames"][vm_name]
                # - CLOUDTIGER_SSH_USERNAME env variable

                operation.scope_config_dict["vm_ssh_params"][vm_name]["standard_user"] =\
                    operation.scope_config_dict.get(
                        "custom_ssh_parameters", {}).get("usernames", {}).get(
                            vm_name, os.environ["CLOUDTIGER_SSH_USERNAME"])

                # we set the Ansible python interpreter
                # by order of priority, the Ansible python interpreter for a VM should be :
                # - custom_ssh_parameters["python_interpreter"]
                # - python3

                operation.scope_config_dict["vm_ssh_params"][vm_name]\
                    ["ansible_python_interpreter"] = \
                        operation.scope_config_dict["vm"][network_name][subnet_name][vm_name]\
                            .get("extra_parameters", {})\
                                .get("python_interpreter", DEFAULT_ANSIBLE_PYTHON_INTERPRETER)

                # we set the bastion public IP for a SSH proxy access mode
                if operation.scope_config_dict.get("use_proxy", False):
                    # first we get the 'escape public subnet' (= the subnet with public
                    # internet access hosting SSH bastions used by the private machines)
                    escape_public_subnet = operation.scope_config_dict["network"][network_name]\
                        .get("private_subnets_escape_public_subnet", None)
                    # then we get the VMs with a group tag 'bastion'
                    escape_bastions = {
                        vm.get("prefix", "") + vm_name + "_vm": vm
                        for vm_name, vm in operation.scope_config_dict["vm"][network_name]\
                            .get(escape_public_subnet, {}).items() \
                                if vm.get("group", "") == "bastion"
                    }
                    # we choose the first available bastion
                    escape_bastion = list(escape_bastions.keys())[0]
                    # we attribute the bastion to the SSH parameters for the current VM
                    operation.scope_config_dict["vm_ssh_params"][vm_name]["bastion_address"] \
                        = operation.terraform_vm_data[escape_bastion].get("public_ip", "unset")
                    operation.scope_config_dict["vm_ssh_params"][vm_name]["bastion_name"] \
                        = escape_bastion


def set_vm_ansible_parameters(operation: Operation, vm_name: str) -> dict:

    """ this function set the ansible parameters for the hosts file for a VM

    :param operation: Operation, the current Operation
    :param vm_name: the name of the current VM (as defined in the config.yml)

    :return vm_ssh_parameters: dict of SSH parameters to reach the VM with Ansible
    """

    ansible_ssh_host = operation.scope_unpacked_ips[vm_name].split(':')[0]

    if operation.default_user:
        ansible_user = operation.scope_config_dict["vm_ssh_params"][vm_name]["os_user"]
    else:
        ansible_user = operation.scope_config_dict["vm_ssh_params"][vm_name]["standard_user"]

    ansible_python_interpreter =\
        operation.scope_config_dict["vm_ssh_params"][vm_name]["ansible_python_interpreter"]

    ansible_ssh_port = operation.scope_config_dict["vm_ssh_params"][vm_name]["ssh_port"]

    vm_ssh_parameters = {
        "ansible_ssh_host": ansible_ssh_host
    }

    if ansible_ssh_port != "22":
        vm_ssh_parameters["ansible_ssh_port"] = ansible_ssh_port

    if ansible_user != os.environ["CLOUDTIGER_SSH_USERNAME"]:
        vm_ssh_parameters["ansible_user"] = ansible_user
        # if the SSH user is the OS user, we have to set the password for sudo actions
        if operation.default_user:
            vm_ssh_parameters["ansible_become_pass"] = ansible_user
            vm_ssh_parameters["ansible_ssh_pass"] = ansible_user

    if ansible_python_interpreter != DEFAULT_ANSIBLE_PYTHON_INTERPRETER:
        vm_ssh_parameters["ansible_python_interpreter"] = ansible_python_interpreter

    return vm_ssh_parameters


def group_hosts(operation: Operation) -> dict:

    """ this function takes the operation.scope_config_dict["vm"] dictionary
    and return a dictionary ready for dump as an ansible hosts file 

    :param operation: Operation, the current Operation

    :return host_file: dict the content of the hosts.yml file for Ansible
    """

    scope_groups = [
        item
        for _, _, _, group_list in operation.scope_config_dict["unpacked_vms"]
        for item in group_list
    ]
    scope_groups = list(set(scope_groups))

    scope_subnets = list(set([
        subnet
        for _, _, subnet, _ in operation.scope_config_dict["unpacked_vms"]
        ]))

    group_children = {
        scope_group: {
            "hosts": {
                vm_name: set_vm_ansible_parameters(operation, vm_name)
                for vm_name, _, _, vm_groups
                in operation.scope_config_dict["unpacked_vms"] if scope_group in vm_groups
            }
        } for scope_group in scope_groups
    }

    subnet_children = {
        subnet: {
            "hosts": {
                vm_name: set_vm_ansible_parameters(operation, vm_name)
                for vm_name, _, subnet_name, _
                in operation.scope_config_dict["unpacked_vms"] if subnet_name == subnet
            }
        } for subnet in scope_subnets
    }

    host_file = {
        "all": {
            "vars": operation.scope_config_dict\
                .get("custom_ssh_parameters", {}).get("all", {}).get("vars", {}),
            "children": {** group_children, **subnet_children}
        }
    }

    if operation.consolidated:
        # if we are in consolidated mode, we also group VMs by environment and
        # by owner
        all_environments = list(set(
            {vm["env"] for vm in operation.scope_config_dict["vm_ssh_params"].values()}))

        environment_children = {
            environment: {
                "hosts": {
                    vm_name: set_vm_ansible_parameters(operation, vm_name)
                    for vm_name, content in operation.scope_config_dict["vm_ssh_params"].items()
                    if content["env"] == environment
                }
            } for environment in all_environments
        }

        all_owners = list(set(
            {vm["owner"] for vm in operation.scope_config_dict["vm_ssh_params"].values()}))

        owner_children = {
            owner: {
                "hosts": {
                    vm_name: set_vm_ansible_parameters(operation, vm_name)
                    for vm_name, content in operation.scope_config_dict["vm_ssh_params"].items()
                    if content["owner"] == owner
                }
            } for owner in all_owners
        }

        host_file["all"]["children"].update(environment_children)
        host_file["all"]["children"].update(owner_children)

    return host_file


def create_inventory(operation: Operation):

    """ this function is the entry function for the 'create_inventory' CloudTiger command.
    It creates the ssh.cfg, the ansible.cfg and the hosts.yml file dedicated for the current scope

    :param operation: Operation, the current Operation

    :return: empty return
    """

    operation.logger.debug("Creating inventory folder")

    os.makedirs(os.path.join(operation.scope_folder, "inventory"), exist_ok=True)

    # set ssh.cfg
    # first, we choose a ssh.cfg template according to the kind of SSH access we want
    use_proxy = ""
    os_user = ""
    if operation.scope_config_dict.get("use_proxy", False):
        use_proxy = "_with_proxy"
    if operation.default_user:
        os_user = "_os_user"
    ssh_cfg_template = format("ssh%s%s.cfg.j2" % (use_proxy, os_user))

    ssh_cfg_template = os.path.join(
        operation.libraries_path, "internal", "inventory", ssh_cfg_template
    )

    # then, we define the location of the target ssh.cfg
    ssh_cfg_output = os.path.join(operation.scope_folder, 'inventory', "ssh.cfg")

    # we create the ssh.cfg file
    j2(operation.logger, ssh_cfg_template, operation.scope_config_dict, ssh_cfg_output)

    # set hosts.yml

    # we load the dictionary for the hosts.yml file
    host_file_content = group_hosts(operation)

    # then, we define the location of the target hosts.yml
    host_file_output = os.path.join(operation.scope_folder, "inventory", "hosts.yml")

    with open(host_file_output, "w") as f:
        yaml.dump(host_file_content, f)

    # set ansible.cfg
    # if we are using the default OS user, we disable host fingerprint checking
    if operation.default_user or operation.ssh_no_check:
        ansible_cfg = os.path.join(
            operation.libraries_path, "internal", "inventory", "ansible_nocheck.cfg"
        )
    else:
        ansible_cfg = os.path.join(operation.libraries_path, "internal", "inventory", "ansible.cfg")
    shutil.copy(ansible_cfg, os.path.join(operation.scope_folder, "inventory", "ansible.cfg"))


def install_ansible_dependencies(operation: Operation):

    """ This function creates an <GITOPS_FOLDER>/ansible/requirements.yml file
    by merging the default one from CloudTiger sources and the one in
    <GITOPS_FOLDER>/standard/ansible_requirements.yml

    :param operation: Operation, the current Operation

    :return: empty return
    """

    # install Ansible dependencies
    operation.logger.info("Installation of Ansible dependencies")

    # we merge the Ansible requirement lists from libraries/ansible/requirements.yml
    # and from <GITOPS_FOLDER>/standard/ansible_requirements.yml
    ansible_folder = os.path.join(operation.project_root, "ansible")
    ansible_generic_requirement = os.path.join(
        operation.libraries_path, "ansible", "requirements.yml"
    )
    ansible_local_requirement = os.path.join(
        operation.project_root, "standard", "ansible_requirements.yml"
    )
    ansible_dest_requirement = os.path.join(
        operation.project_root, "ansible", "requirements.yml"
    )
    os.makedirs(ansible_folder, exist_ok=True)

    ansible_requirement_content = load_yaml(operation.logger, ansible_generic_requirement)
    if os.path.exists(ansible_local_requirement):
        ansible_local_requirement_content = load_yaml(operation.logger, ansible_local_requirement)
        ansible_requirement_content['roles'] =\
            ansible_requirement_content['roles'] + ansible_local_requirement_content['roles']

    with open(ansible_dest_requirement, "w") as f:
        yaml.dump(ansible_requirement_content, f)

    command = "ansible-galaxy install -r ansible/requirements.yml"

    if operation.ansible_force_install:
        command += " --force"

    bash_action(operation.logger, command, operation.project_root,
                os.environ, operation.stdout_file)


def install_ansible_playbooks(operation: Operation):

    """ this function copy the needed ansible playbooks into the project root

    :param operation: Operation, the current Operation

    :return: empty return
    """

    ansible_playbooks = os.path.join(operation.libraries_path, "ansible", "playbooks")
    target_folder = os.path.join(operation.project_root, "ansible", "playbooks")
    operation.logger.info("Creating Ansible folder from libraries folder : %s" % target_folder)
    os.makedirs(target_folder, exist_ok=True)
    shutil.copytree(ansible_playbooks, target_folder, dirs_exist_ok=True)


def prepare_ansible(operation: Operation):

    """ this function creates the Ansible meta playbook 'execute_ansible.yml' using inputs
    from the 'ansible' key in config.yml

    :param operation: Operation, the current Operation

    :return: empty return
    """

    # prepare Ansible meta playbook

    execute_ansible_template = os.path.join(
        operation.libraries_path, "internal", "inventory", "execute_ansible.yml.j2"
    )
    execute_ansible_output = os.path.join(
        operation.scope_folder, 'inventory', "execute_ansible.yml"
    )

    # if we have an 'ansible_params' key in the config.yml,
    # it means we need to interprete some variables
    # in the 'ansible' dict that are in jinja format
    if "ansible_params" in operation.scope_config_dict.keys():
        buffer_config_file = os.path.join(operation.scope_folder, "inventory", "buffer_config.yml")
        j2(operation.logger, operation.scope_config,
           operation.scope_config_dict, buffer_config_file)
        ansible_config_dict = {
            **operation.scope_config_dict,
            **load_yaml(operation.logger, buffer_config_file)
        }

    else:
        ansible_config_dict = operation.scope_config_dict

    j2(operation.logger, execute_ansible_template, ansible_config_dict, execute_ansible_output)


def execute_ansible(operation: Operation):

    """ this function executes Ansible on the Ansible meta playbook 'execute_ansible.yml'
    in the scopes/<SCOPE>/inventory folder

    :param operation: Operation, the current Operation

    :return: empty return
    """

    # execute Ansible meta playbook

    ansible_cfg_file = os.path.join(operation.scope_inventory_folder, 'ansible.cfg')
    ansible_environ = dict(
        os.environ,
        **{'ANSIBLE_CONFIG': ansible_cfg_file, 'ANSIBLE_TIMEOUT': "120"}
    )

    command = 'ansible-playbook -i ./hosts.yml execute_ansible.yml\
        --extra-vars "exec_folder=$(pwd)"'

    if not operation.default_user:
        if "CLOUDTIGER_SSH_PASSWORD" not in ansible_environ.keys():
            query_string = format(
                "Enter SSH password for %s :" % ansible_environ.get("CLOUDTIGER_SSH_USERNAME"))
            cloudtiger_ssh_password = getpass.getpass(query_string)
            ansible_environ["CLOUDTIGER_SSH_PASSWORD"] = base64.b64encode(
                bytes(cloudtiger_ssh_password, 'utf-8'))
        command += ' --extra-vars "ansible_become_pass=$(echo $CLOUDTIGER_SSH_PASSWORD | base64 --decode)"'

    bash_action(operation.logger, command, operation.scope_inventory_folder,
                ansible_environ, operation.stdout_file, operation.stderr_file)


def setup_ssh_connection(operation: Operation):

    """ this function tries a first ssh connect in order to make ansible connection doable,
    and clean the existing SSH fingerprint of the target hosts if necessary

    :param operation: Operation, the current Operation

    :return: empty return
    """

    operation.logger.info("Collecting list of all VMs")

    data_loader = DataLoader()
    inventory_file = os.path.join(operation.scope_inventory_folder, "hosts.yml")
    if not os.path.exists(inventory_file):
        err = format("Error : missing hosts.yml file in folder %s"
                     % operation.scope_inventory_folder)
        operation.logger.error(err)
        raise Exception(err)

    inventory = InventoryManager(loader=data_loader, sources=[inventory_file])

    all_vms_ip = inventory.get_groups_dict()["all"]

    for vm in all_vms_ip:
        operation.logger.debug("Removing vm %s from known hosts" % vm)
        command = format("ssh-keygen -f \"/home/%s/.ssh/known_hosts\" -R \"%s\""
                         % (os.environ["USER"], operation.scope_unpacked_ips[vm]))
        bash_action(operation.logger, command, operation.scope_inventory_folder, os.environ)


def meta_aggregate(operation: Operation):

    """ this function aggregates all config files in current
    folder and subfolders into a meta_config.yml

    :param operation: Operation, the current Operation
    """

    # we check if the meta_config already exists
    meta_config = {'ansible':dict()}
    meta_config_path = os.path.join(operation.scope_config_folder, "meta_config.yml")
    if os.path.isfile(meta_config_path):
        with open(meta_config_path, "r") as f:
            try:
                meta_config = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as e:
                operation.logger.error(format(
                    "Failed to open meta_config file %s with error %s" % (meta_config_path, e)))

    # we loop through the config folder
    for (root, dirs, files) in os.walk(operation.scope_config_folder):
        if 'config.yml' in files:
            subconfig_path = os.path.join(root, 'config.yml')
            subconfig_scope = os.path.join(
                *(subconfig_path.split(os.sep)
                  [len(operation.scope_config_folder.split(os.sep)):-1])
            )
            with open(subconfig_path, 'r') as f:
                try:
                    subconfig_data = yaml.load(f, Loader=yaml.FullLoader)
                except Exception as e:
                    operation.logger.error(format(
                        "Failed to open file %s with error %s" % (subconfig_path, e)))
            meta_config['ansible'][subconfig_scope] = subconfig_data.get('ansible')

    # we write the meta_config.yml
    meta_config_path = os.path.join(operation.scope_config_folder, "meta_config.yml")
    with open(meta_config_path, "w") as f:
        yaml.dump(meta_config, f)


def meta_distribute(operation: Operation):

    """ this function distributes the ansible data from the
    meta_config.yml to all scopes defined inside

    :param operation: Operation, the current Operation

    :return: empty return
    """

    # we load the meta_config data
    meta_config_path = os.path.join(operation.scope_config_folder, "meta_config.yml")
    with open(meta_config_path, "r") as f:
        meta_config = yaml.load(f, Loader=yaml.FullLoader)

    # ensure the ansible entry is well defined
    meta_config['ansible'] = meta_config.get('ansible', {})

    meta_defined_scopes = meta_config.get('ansible', {}).keys()

    # set empty ansible entries for scopes in the folder tree but without meta_config data
    for (root, _, files) in os.walk(operation.scope_config_folder):
        if 'config.yml' in files:
            subconfig_path = os.path.join(root, 'config.yml')
            subconfig_scope = subconfig_path.split(os.sep)[
                len(operation.scope_config_folder.split(os.sep)):-1
            ]
            if len(subconfig_scope) > 0:
                subconfig_scope = os.path.join(*subconfig_scope)
            else:
                subconfig_scope = "."
            if subconfig_scope not in meta_defined_scopes:
                meta_config['ansible'][subconfig_scope] = {}

    for scope, scope_content in meta_config['ansible'].items():
        subconfig_path = os.path.join(operation.scope_config_folder, scope, 'config.yml')
        if os.path.isfile(subconfig_path):
            operation.logger.debug("Updating ansible config for scope %s" % scope)
            subconfig_data = {}
            # loading pre-existing config
            with open(subconfig_path, 'r') as f:
                try:
                    subconfig_data = yaml.load(f, Loader=yaml.FullLoader)
                except Exception as e:
                    operation.logger.error("Failed to open file %s with error %s"
                                          % (subconfig_path, e))
            # updating config with ansible data for considered scope
            subconfig_data['ansible'] = scope_content.get('tasks', {})

            # adding ansible_params if necessary
            if "params" in scope_content.keys():
                subconfig_data['ansible_params'] = scope_content["params"]
            with open(subconfig_path, 'w') as f:
                try:
                    yaml.dump(subconfig_data, f)
                except Exception as e:
                    operation.logger.error("Failed to open file %s with error %s"
                                          % (subconfig_path, e))
        else:
            operation.logger.error("Scope %s is not defined" % scope)
