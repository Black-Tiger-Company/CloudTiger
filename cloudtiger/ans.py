"""Ansible operations for CloudTiger."""
import os
import string
import sys
import copy
import shutil
import getpass
import base64
from typing import Tuple
import ruamel.yaml
import re

import yaml
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import bash_action, j2, load_yaml
from cloudtiger.data import (
    DEFAULT_ANSIBLE_PYTHON_INTERPRETER,
    DEFAULT_SSH_PORT,
    common_group_names,
    common_environment_tags,
    custom_ssh_port_per_vm_type
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

    elts2 = vm_name.split(".")[-1].split("-")[-1]
    owner = "internal"
    if elts2 != "":
        owner = elts2

    return group, env, owner


def extract_ssh_port(vm_address: str, vm_name: str, keep_default_ssh: bool) -> str:

    """ this function extracts a SSH port from the VM address as provided in the
    all_addresses_info.yml file

    :param vm_address: str, the name of the vm

    :return str, the SSH port for the VM
    """

    if not keep_default_ssh:
        # we check if a custom SSH port is provided
        elts = vm_address.split(':')

        if len(elts) > 1:
            # a custom SSH port has been provided using semicolon
            if elts[-1].isdigit():
                return elts[-1]
        else:
            # let us check the name of the vm
            for vm_type, custom_port in custom_ssh_port_per_vm_type.items():
                if vm_type in vm_name:
                    return custom_port

    return DEFAULT_SSH_PORT


def load_ssh_parameters_meta(operation: Operation, keep_default_ssh=False):

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
                "ssh_port": extract_ssh_port(vm_ip, vm_name, keep_default_ssh),
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

def set_ssh_port(operation, vm_name, network_name, subnet_name, keep_default_ssh):

    if keep_default_ssh:
        return "22"

    ssh_port = operation.scope_config_dict.get("custom_ssh_parameters", {})\
        .get("ssh_ports", {})\
            .get(vm_name, operation.scope_config_dict["vm"][network_name][subnet_name][vm_name]\
                .get("extra_parameters", {}).get("custom_ssh_port", DEFAULT_SSH_PORT))

    return ssh_port

def load_ssh_parameters(operation: Operation, keep_default_ssh=False):

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
                    "group" : vm.get("group", "ungrouped"),
                    "metadata": vm.get("metadata", {})
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

                operation.scope_config_dict["vm_ssh_params"][vm_name]["ssh_port"] = set_ssh_port(operation, vm_name, network_name, subnet_name, keep_default_ssh)

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
                        vm_name: vm
                        for vm_name, vm in operation.scope_config_dict["vm"][network_name]\
                            .get(escape_public_subnet, {}).items() \
                                if vm.get("group", "") == "bastion"
                    }

                    # we choose the first available bastion
                    escape_bastion = list(escape_bastions.keys())[0]

                    bastion_data = operation.terraform_vm_data.get(escape_bastion, {})
                    if not bastion_data:
                        # raise warning if no TF data available for bastion
                        operation.logger.warning(
                            "Warning : no Terraform data available for bastion")

                    # we attribute the bastion to the SSH parameters for the current VM
                    operation.scope_config_dict["vm_ssh_params"][vm_name]["bastion_address"] \
                        = bastion_data.get("public_ip", "unset")
                    operation.scope_config_dict["vm_ssh_params"][vm_name]["bastion_name"] \
                        = escape_bastion


def set_vm_ansible_parameters(operation: Operation, vm_name: str) -> dict:

    """ this function set the ansible parameters for the hosts file for a VM

    :param operation: Operation, the current Operation
    :param vm_name: the name of the current VM (as defined in the config.yml)

    :return vm_ssh_parameters: dict of SSH parameters to reach the VM with Ansible
    """

    ansible_private_ip = operation.scope_unpacked_ips[vm_name].split(':')[0]

    if operation.default_user:
        ansible_user = operation.scope_config_dict["vm_ssh_params"][vm_name]["os_user"]
    else:
        ansible_user = operation.scope_config_dict["vm_ssh_params"][vm_name]["standard_user"]

    ansible_python_interpreter =\
        operation.scope_config_dict["vm_ssh_params"][vm_name]["ansible_python_interpreter"]

    ansible_ssh_port = operation.scope_config_dict["vm_ssh_params"][vm_name]["ssh_port"]

    provider_name = next(iter(operation.scope_config_dict['vm']))
    print(provider_name)
    vlan_name = next(iter(operation.scope_config_dict['vm'][provider_name]))
    print(vlan_name)
    root_volume_size=operation.scope_config_dict['vm'][provider_name][vlan_name][vm_name]['root_volume_size']

    vm_ssh_parameters = {
        "ansible_ssh_host": vm_name,
        "ansible_user": ansible_user,
        "private_ip": ansible_private_ip,
        "root_disk_size": root_volume_size
    }

    # add metadata if they exist
    if "metadata" in operation.scope_config_dict["vm_ssh_params"][vm_name].keys():
        if isinstance(operation.scope_config_dict["vm_ssh_params"][vm_name]["metadata"], dict):
            if len(operation.scope_config_dict["vm_ssh_params"][vm_name]["metadata"]) > 0:
                for k, v in operation.scope_config_dict["vm_ssh_params"][vm_name]["metadata"].items():
                    # you cannot overloads reserved ansible parameter names
                    if k not in operation.scope_config_dict["vm_ssh_params"][vm_name].keys():
                        operation.scope_config_dict["vm_ssh_params"][vm_name][k] = v
                        vm_ssh_parameters[k] = v

    if ansible_ssh_port != "22":
        vm_ssh_parameters["ansible_ssh_port"] = ansible_ssh_port

    if ansible_user != os.environ["CLOUDTIGER_SSH_USERNAME"]:
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
        scope_group.replace(' ','-'): {
            "hosts": {
                vm_name: set_vm_ansible_parameters(operation, vm_name)
                for vm_name, _, _, vm_groups
                in operation.scope_config_dict["unpacked_vms"] if scope_group in vm_groups
            }
        } for scope_group in scope_groups
    }

    subnet_children = {
        subnet.replace(' ','-'): {
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
    if operation.obsolete_ssh:
        ansible_cfg = os.path.join(
            operation.libraries_path, "internal", "inventory", "ansible_nocheck.cfg"
        )
    elif operation.default_user or operation.ssh_no_check:
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
    ansible_role_list = os.path.join(
        operation.project_root, "ansible", "roles.txt"
    )
    os.makedirs(ansible_folder, exist_ok=True)

    ansible_requirement_content = load_yaml(operation.logger, ansible_generic_requirement)
    if os.path.exists(ansible_local_requirement):
        ansible_local_requirement_content = load_yaml(operation.logger, ansible_local_requirement)
        ansible_requirement_content['roles'] =\
            ansible_requirement_content['roles'] + ansible_local_requirement_content['roles']

    # add repository credentials if needed
    ansible_requirement_content_backup = copy.deepcopy(ansible_requirement_content)
    if ("CLOUDTIGER_ANSIBLE_REPO_USER" in os.environ.keys()) & \
    ("CLOUDTIGER_ANSIBLE_REPO_PASSWORD" in os.environ.keys()):
        ansible_requirement_content['roles'] = [
            {
                'name': role['name'],
                'version': role['version'],
                'src': role['src'].replace('https://', 'https://' + 
                                           os.environ["CLOUDTIGER_ANSIBLE_REPO_USER"] +
                                           ":" +
                                           os.environ["CLOUDTIGER_ANSIBLE_REPO_PASSWORD"] +
                                           "@")
            }
            for role in ansible_requirement_content['roles'] if type(role) is dict
        ] + [
            role for role in ansible_requirement_content['roles'] if type(role) is string
        ]

    with open(ansible_dest_requirement, "w") as f:
        yaml.dump(ansible_requirement_content, f)

    # dump the list of ansible roles with their version
    command = "ansible-galaxy role list"
    if os.path.exists(ansible_role_list):
        os.remove(ansible_role_list)
    bash_action(operation.logger, command, operation.project_root,
                os.environ, ansible_role_list)

    installed_ansible_roles = dict()

    try :
        with open(ansible_role_list, "r") as f:
            ansible_roles = f.read().split('\n')
            ansible_roles = [x for x in ansible_roles if len(x) > 1 ]
            ansible_roles = [x[2:].split(',') for x in ansible_roles if x[:2] == "- "]
            ansible_roles = [(x[0], x[1].strip()) for x in ansible_roles]
            installed_ansible_roles = dict(ansible_roles)
    except Exception as exc:
        operation.logger.error(F"Error raised when trying to read the list of Ansible roles : {exc}")
        sys.exit()

    role_update_list = []
    for required_role in ansible_requirement_content['roles']:
        if isinstance(required_role, dict):
            if 'name' not in required_role.keys():
                raise Exception("Role name not specified in Ansible requirements file")
            required_role_name = required_role['name']
            if required_role.get('version', 'latest') != installed_ansible_roles.get(required_role_name, "unknown"):
                role_update_list.append(required_role_name)

    role_update_commands = [f"ansible-galaxy install -r ansible/requirements.yml {role_name} --force --ignore-errors" for role_name in role_update_list]

    for role_update_command in role_update_commands:
        bash_action(operation.logger, role_update_command, operation.project_root,
                os.environ, operation.stdout_file)

    # # remove repository credentials if needed
    # if ("CLOUDTIGER_ANSIBLE_REPO_USER" in os.environ.keys()) & \
    # ("CLOUDTIGER_ANSIBLE_REPO_PASSWORD" in os.environ.keys()):
    #     with open(ansible_dest_requirement, "w") as f:
    #         yaml.dump(ansible_requirement_content, f)


def install_ansible_playbooks(operation: Operation):

    """ this function copy the needed ansible playbooks into the project root

    :param operation: Operation, the current Operation

    :return: empty return
    """

    ansible_playbooks = os.path.join(operation.libraries_path, "ansible", "playbooks")
    local_ansible_playbooks = os.path.join(operation.project_root, "standard", "playbooks")
    target_folder = os.path.join(operation.project_root, "ansible", "playbooks")
    operation.logger.info("Creating Ansible folder from libraries folder : %s" % target_folder)
    os.makedirs(target_folder, exist_ok=True)
    shutil.copytree(ansible_playbooks, target_folder, dirs_exist_ok=True)

    if os.path.isdir(local_ansible_playbooks):
        local_files = os.listdir(local_ansible_playbooks)
        for file in local_files:
            src_playbook = os.path.join(local_ansible_playbooks, file)
            if os.path.isfile(src_playbook):
                if file.split('.')[-1] in ["yaml", "yml"]:
                    dest_playbook = os.path.join(target_folder, file)
                    shutil.copyfile(src_playbook, dest_playbook)


def prepare_ansible(operation: Operation, securize=False):

    """ this function creates the Ansible meta playbook 'execute_ansible.yml' using inputs
    from the 'ansible' key in config.yml

    :param operation: Operation, the current Operation
    :param securize: bool, set to True if we are using the 'cloudtiger ... init Z' command

    :return: empty return
    """

    # prepare Ansible meta playbook
    if operation.default_user | (not operation.ssh_with_password) :
        execute_ansible_template = os.path.join(
            operation.libraries_path, "internal", "inventory", "execute_ansible_no_sudo_pass.yml.j2"
        )
    else:
        execute_ansible_template = os.path.join(
            operation.libraries_path, "internal", "inventory", "execute_ansible.yml.j2"
        )
    execute_ansible_output = os.path.join(
        operation.scope_folder, 'inventory', "execute_ansible.yml"
    )

    # if the ansible key is not 'ansible', we need to reinject the ansible key content into
    # operation.scope_config_dict['ansible']
    if operation.ansible_key != 'ansible':
        operation.scope_config_dict["ansible"] = operation.scope_config_dict.get(operation.ansible_key, [])

    # if we have an 'ansible_params' key in the config.yml,
    # it means we need to interprete some variables
    # in the 'ansible' dict that are in jinja format
    if (not securize) & ("ansible_params" in operation.scope_config_dict.keys()):
        operation.logger.debug("Interpretating ansible parameters")
        buffer_config_file = os.path.join(operation.scope_folder, "inventory", "buffer_config.yml")
        j2(operation.logger, operation.scope_config,
           operation.scope_config_dict["ansible_params"], buffer_config_file)
        ansible_config_dict = {
            **operation.scope_config_dict,
            **load_yaml(operation.logger, buffer_config_file)
        }

    else:
        ansible_config_dict = operation.scope_config_dict

    j2(operation.logger, execute_ansible_template, ansible_config_dict, execute_ansible_output)

    # set secret keys in the execute_ansible.yml file
    cloudtiger_secret_pattern = re.escape("__CT_SECRET_START__") + "(.*?)" + re.escape("__CT_SECRET_STOP__")

    execute_ansible_content = ""
    with open(execute_ansible_output, "r") as file:
        execute_ansible_content = file.read()

    cloudtiger_ansible_secrets = re.findall(cloudtiger_secret_pattern, execute_ansible_content)
    # get unique secret patterns
    cloudtiger_ansible_secrets = list(set(cloudtiger_ansible_secrets))

    for ct_ansible_secret in cloudtiger_ansible_secrets:
        secret_path = ct_ansible_secret.split('_')
        if len(secret_path) < 2:
            operation.logger.error(f"Error : the ansible secret pattern {ct_ansible_secret} is badly formatted")
            sys.exit()
        else:
            secret_folder = secret_path[0].lower()
            secret_key = "_".join(secret_path[1:])
            # check if secret_folder exists, and contains .env
            secret_file = os.path.join(operation.project_root, 'secrets', secret_folder, '.env')
            if not os.path.exists(secret_file):
                operation.logger.error(f"Error : the file {secret_file} referenced by secret {ct_ansible_secret} does not exist")
                sys.exit()
            secrets = []
            with open(secret_file, "r") as file:
                secrets = file.read().split('\n')
                # remove lines without '='
            secrets = [
                key for key in secrets if '=' in key
            ]
            secrets = {
                line.replace('export ', '').split('=')[0] : line.replace('export ', '').split('=')[1] for line in secrets
            }
            if secret_key not in secrets.keys():
                operation.logger.error(f"Error : the key {secret_key} referenced by secret {ct_ansible_secret} does not exist in secret file {secret_file}")
                sys.exit()
            secret = secrets[secret_key]
            execute_ansible_content = execute_ansible_content.replace("__CT_SECRET_START__" + ct_ansible_secret + "__CT_SECRET_STOP__", secret)
            with open(execute_ansible_output, "w") as file:
                file.write(execute_ansible_content)


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

    if operation.ssh_with_password:
        if "CLOUDTIGER_SSH_PASSWORD" not in ansible_environ.keys():
            query_string = format(
                "Enter SSH password for %s :" % ansible_environ.get("CLOUDTIGER_SSH_USERNAME"))
            cloudtiger_ssh_password = getpass.getpass(query_string)
            ansible_environ["CLOUDTIGER_SSH_PASSWORD"] = base64.b64encode(
                bytes(cloudtiger_ssh_password, 'utf-8'))
        command += ' --extra-vars "b64_ansible_ssh_pass=$(echo $CLOUDTIGER_SSH_PASSWORD)"'

    if operation.encrypted_file is not None:
        ansible_vault_password_file = os.path.join(operation.project_root, 'secrets', 'ansible-vault', 'ansible-vault-secret.txt')
        ansible_vault_encrypted_file = os.path.join(operation.project_root, 'secrets', 'ansible-vault', operation.encrypted_file)
        if not os.path.isfile(ansible_vault_password_file):
            operation.logger.error("The file %s. Terminating" % ansible_vault_password_file)
            sys.exit()
        if not os.path.isfile(ansible_vault_encrypted_file):
            operation.logger.error("The file %s is not set. Terminating" % ansible_vault_encrypted_file)
            sys.exit()
        command += f" --vault-password-file {ansible_vault_password_file} {ansible_vault_encrypted_file}"

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
        operation.logger.debug("Removing vm IP %s from known hosts" % vm)
        command = format("ssh-keygen -f ~/.ssh/known_hosts -R \"%s\""
                         % (operation.scope_unpacked_ips[vm]))
        bash_action(operation.logger, command, operation.scope_inventory_folder, os.environ)
        operation.logger.debug("Removing vm hostname %s from known hosts" % vm)
        command = format("ssh-keygen -f ~/.ssh/known_hosts -R \"%s\""
                         % (vm))
        bash_action(operation.logger, command, operation.scope_inventory_folder, os.environ)

        # when using a proxy SSH connection, a first direct connection with plain SSH
        # is necessary in order to have Ansible able to connect afterwards
        if operation.scope_config_dict.get("use_proxy", False):
            operation.logger.debug(
                "Initializing first SSH connection to allow proxy connection")
            if operation.default_user:
                ansible_user = operation.scope_config_dict["vm_ssh_params"][vm]["os_user"]
            else:
                ansible_user = operation.scope_config_dict["vm_ssh_params"][vm]["standard_user"]
            command = format(
                "ssh -o \"StrictHostKeyChecking no\" -F ssh.cfg %s@%s bash -c 'echo \"done\"'" %
                (ansible_user, vm))
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

def my_represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

def meta_distribute(operation: Operation):

    """ this function distributes the ansible data from the
    meta_config.yml to all scopes defined inside

    :param operation: Operation, the current Operation

    :return: empty return
    """

    # create a ruamel yaml reader/writer to preserve comment in yaml files
    ru_yaml = ruamel.yaml.YAML()
    ru_yaml.preserve_quotes = True
    # ru_yaml.default_flow_style = False
    ru_yaml.representer.add_representer(type(None), my_represent_none)

    # we load the meta_config data
    meta_config_path = os.path.join(operation.scope_config_folder, "meta_config.yml")
    with open(meta_config_path, "r") as f:
        meta_config = ru_yaml.load(f)
        # meta_config = yaml.load(f, Loader=yaml.FullLoader)

    # ensure the ansible entry is well defined
    meta_config_ansible = meta_config.get('ansible', {})

    meta_defined_scopes = list(meta_config.get('infra', {}).keys())

    operation.logger.info(f"Adding Ansible entries to list of scopes : {meta_defined_scopes}")

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

    # add common Ansible tasks to all subscopes
    common_content = meta_config_ansible.get("common", {})
    common_params = common_content.get("params", {})
    meta_config_ansible.pop("common", None)

    for scope in meta_defined_scopes:
        scope_content = meta_config_ansible.get(scope, {})
        subconfig_path = os.path.join(operation.scope_config_folder, scope, 'config.yml')
        if os.path.isfile(subconfig_path):
            operation.logger.info("Updating ansible config for scope %s" % scope)
            subconfig_data = {}
            # loading pre-existing config
            with open(subconfig_path, 'r') as f:
                try:
                    # subconfig_data = yaml.load(f, Loader=yaml.FullLoader)
                    subconfig_data = ru_yaml.load(f)
                except Exception as e:
                    operation.logger.error("Failed to open file %s with error %s"
                                          % (subconfig_path, e))
            # updating config with ansible data for considered scope
            subconfig_data['ansible'] = common_content.get('tasks', [])
            subconfig_data['ansible'] += scope_content.get('tasks', [])

            # adding ansible_params if necessary
            environment = os.path.basename(scope)
            subconfig_data['ansible_params'] = {'environment': environment}
            subconfig_data['ansible_params'].update(common_params)
            if "params" in scope_content.keys():
                subconfig_data['ansible_params'].update(scope_content["params"])
            with open(subconfig_path, 'w') as f:
                try:
                    # yaml.dump(subconfig_data, f)
                    ru_yaml.dump(subconfig_data, f)
                except Exception as e:
                    operation.logger.error("Failed to open file %s with error %s"
                                          % (subconfig_path, e))
        else:
            operation.logger.error("Scope %s is not defined" % scope)
