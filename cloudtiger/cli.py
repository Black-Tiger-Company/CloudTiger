"""Console script for cloudtiger."""
import os
import sys

import click

from cloudtiger.init import (
    folder,
    config,
    set_ssh_keys,
    configure_ip,
    prepare_scope_folder,
    init_meta_aggregate,
    init_meta_distribute
)
from cloudtiger.ans import (
    install_ansible_playbooks,
    install_ansible_dependencies,
    load_ssh_parameters,
    load_ssh_parameters_meta,
    create_inventory,
    setup_ssh_connection,
    prepare_ansible,
    execute_ansible,
    meta_distribute,
    meta_aggregate
)
from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import create_logger
from cloudtiger.data import allowed_actions, available_api_services
from cloudtiger.service import tf_service_generic, prepare
from cloudtiger.tf import tf_generic


@click.group()
@click.version_option()
@click.option('--project-root', '-p', default='.', help="set the gitops project root")
@click.option('--libraries-path', '-l', default=None,
              help="set a custom folder of libraries for Terraform modules and Ansible playbooks")
@click.option('--output-file', '-o', default=None,
              help="define a file path for dumping outputs of CloudTiger")
@click.option('--error-file', '-e', default=None,
              help="define a file path for dumping erros of CloudTiger")
@click.option('--recursive', '-r', is_flag=True, default=False,
              help="this option will apply your command recursively on all scope folders inside"
              "current folder")
@click.option('--verbose', '-v', is_flag=True, default=False,
              help="set logger to verbose mode")
@click.argument('scope')
@click.pass_context
def main(context, scope, project_root, libraries_path, output_file, error_file, recursive, verbose):
    """ Cloud Tiger is a CLI tool for creating, configuring and managing infrastructures.
    """

    # create a logger for the command
    logger = create_logger(verbose=verbose)

    logger.info("Starting Cloud Tiger")

    # check consistency of arguments
    project_root = os.path.expanduser(project_root)
    if not os.path.isdir(project_root):
        logger.error("The folder %s for project root does not exist" % project_root)
        sys.exit("Impossible to go on")

    # let us define the scope or list of scopes, and the list of operations
    scopes = []
    operations = []

    # if the scope is not the 'root' folder and the last element of the scope
    # is a path separator, we remove it
    if len(scope) > 1:
        if scope[-1] == os.sep:
            scope = scope[:-1]

    scope_elts = scope.split(os.sep)
    # if the first folder of scope is NOT 'config', we add it to the scope path
    # - this behavior is meant to facilitate autocompletion on scope path
    if scope_elts[0] != "config":
        logger.debug("Adding 'config' to scope(s) path")
        scope = os.path.join("config", scope)
        logger.debug("New scope path is %s" % scope)

    # if 'recursive' option is set, we detect all scopes contained in subfolders
    # of current working directory

    if recursive:
        for root, _, files in os.walk(os.path.join(project_root, scope)):
            for file in files:
                if file == "config.yml":
                    subscope = root.lstrip('./').rstrip('/')
                    logger.info(
                        "Will execute Cloud Tiger action on subscope %s" % subscope)
                    scopes.append(subscope)

        # otherwise, we consider the current working directory as a simple scope
    else:
        logger.info("Starting Cloud Tiger action on simple scope %s", scope)
        scopes = [scope]

    for scope_elt in scopes:
        operation = Operation(logger, project_root, scope_elt, libraries_path, output_file,
                              error_file)
        # let us check if the provided scope is a well-configured scope in a well-configured
        # project folder
        # if not the case, we should assume that we are using a `init folder` or `init config`
        # command
        root_dotenv = os.path.join(project_root, ".env")
        config_file = os.path.join(project_root, scope, "config.yml")
        meta_config_file = os.path.join(project_root, scope, "meta_config.yml")
        if os.path.exists(root_dotenv) & (os.path.exists(config_file)|os.path.exists(meta_config_file)):
            operation.scope_setup()
            operation.secrets_setup()
            operation.logger.debug("Operations setup")

        operations.append(operation)

    # necessary to pass main CLI context to sub actions
    context.obj = {
        "operations": operations,
        "logger": logger
    }

    return


@click.command('init', short_help='init actions')
@click.argument('action')
@click.pass_context
def init(context, action):
    """ Initial actions for preparing a new scope :
\n- folder (F)            : create a boostrap gitops folder
\n- ssh_keys (0)          : create a dedicated pair of SSH keys
for the current scope in secrets/ssh/<PROVIDER>/private|public
\n- get_ip (1)            : collect available IPs from fping
\n- scope_folder (2)      : prepare scope folder
\n- meta_aggregate (M1)   : aggregate config.yml files from children scopes
\n- meta_distribute (M2)  : distribute the meta_config.yml to children scopes
    """

    logger = context.obj['logger']

    for operation_context in context.obj['operations']:
        operation: Operation = operation_context

        operation.logger.info("init action")

        # check if action is allowed
        if action in allowed_actions["init"].keys():

            operation.logger.debug("%s command" %
                                   allowed_actions["init"][action])
            globals()[allowed_actions["init"][action]](operation)

        else:
            # unallowed action
            operation.logger.error("Unallowed action %s" % action)
            sys.exit()

    logger.info("Finished init action sucessfully")


@click.command('tf', short_help='Terraform actions')
@click.argument('action')
@click.option('--nolock', '-nl', is_flag=True, default=False,
              help="use Terraform with the '-lock=false' flag")
@click.pass_context
def tf(context, action, nolock):
    """ Terraform actions
\n- init (1)             : run Terraform init
\n- apply (2)            : run Terraform apply & output
\n- output (O)           : run Terraform output
\n- import (I)           : custom command for cleaning current tfstate
from declared resources and reimporting them
\n- refresh (R)          : run Terraform refresh & output
\n- destroy (D)          : run Terraform destroy
    """

    for operation_context in context.obj['operations']:
        operation: Operation = operation_context

        operation.logger.debug("tf action")

        # do we apply no-lock flag ?
        if nolock:
            operation.tf_no_lock = True

        # check if action is allowed
        if action in allowed_actions["tf"].keys():

            operation.logger.debug("%s command" % allowed_actions["tf"][action])
            tf_generic(operation, allowed_actions["tf"][action])

        else:
            # unallowed action
            operation.logger.error("Unallowed action %s" % action)
            sys.exit()

    operation.logger.info("Finished tf action sucessfully")


@click.command('ans', short_help='Ansible actions')
@click.argument('action')
@click.option('--consolidated', '-c',
              is_flag=True,
              default=False,
              help="running the ansible command in the 'meta' folder")
@click.option('--default-user', '-d',
              is_flag=True,
              default=False,
              help="will execute ssh connexion using the default user of the VM")
@click.option('--restricted-vms', '-r',
              default=None,
              help="restrict ansible command to hosts listed")
@click.option('--ansible-force-install', '-F',
              is_flag=True,
              default=False)
@click.option('--port', '-P',
              default='22',
              help="set a different port for SSH connexion than the default one (22)")
@click.option('--no-check', '-n',
              is_flag=True,
              default=False,
              help="disable fingerprint check at SSH connection")
@click.pass_context
def ans(context, action, consolidated, default_user, restricted_vms,
        ansible_force_install, port, no_check):
    """ Ansible actions
\n- securize (Z)         : set defined users, deactivate default user
\n- playbooks (P)        : install Ansible playbooks catalog
\n- dependencies (D)     : install Ansible dependencies (roles)
\n- inventory (1)        : prepare Ansible inventory
\n- prep_ansible (2)     : prepare Ansible meta-playbook
\n- setup_ssh (H)        : initialize SSH connections
\n- run_ansible (3)      : run Ansible meta-playbook
"""

    for operation_context in context.obj['operations']:
        operation: Operation = operation_context

        operation.set_ansible_options(
            consolidated,
            default_user,
            ansible_force_install,
            restricted_vms,
            port,
            no_check
        )

        operation.logger.info("ansible action")

        if operation.restricted_vms:
            operation.set_restricted_vms()

        if action in allowed_actions["ans"].keys():
            operation.logger.debug("%s command" %
                                   allowed_actions["ans"][action])

            # we load the SSH config parameters
            if allowed_actions["ans"][action] != "meta_distribute":
                operation.set_terraform_output_info()
                if not operation.consolidated:
                    load_ssh_parameters(operation)
                else:
                    load_ssh_parameters_meta(operation)

            # if the action chosen is 'securize', it means we roll
            # 'devops init' role after ans 1 --d, ans 2 --d
            if allowed_actions["ans"][action] == "securize":
                operation.default_user = True
                operation.devops_init()
                create_inventory(operation)
                setup_ssh_connection(operation)
                prepare_ansible(operation)
                execute_ansible(operation)
                return

            globals()[allowed_actions["ans"][action]](operation)

        else:
            operation.logger.error("Unallowed action %s" % action)
            sys.exit()

    operation.logger.info("Finished ansible action sucessfully")


@click.command('service', short_help='service configuration')
@click.argument('name')
@click.argument('step')
@click.pass_context
def service(context, name, step):
    """ Service configuration through Terraform
service names:
\n- gitlab                : configure Gitlab
\n- nexus                 : configure Nexus
steps :
\n- prepare (0)           : prepare associated Terraform folder and module
\n- init (1)              : run Terraform init
\n- apply (2)             : run Terraform apply & output
\n- refresh (R)           : run Terraform refresh & output
\n- destroy (D)           : run Terraform destroy
    """

    for operation_context in context.obj['operations']:
        operation: Operation = operation_context

        operation.logger.info("service action")

        # check if service exists and is well defined
        if name not in operation.scope_config_dict.keys():
            operation.logger.error("Warning : the requested service is "
                                   "not defined in the config.yml file. Exiting")
            sys.exit()

        if name not in available_api_services:
            operation.logger.error("Warning : the requested service is "
                                   "not available in CloudTiger. Exiting")
            sys.exit()

        if step in allowed_actions["service"].keys():

            operation.logger.debug("%s command" %
                                   allowed_actions["service"][step])

            if allowed_actions["service"][step] == "prepare":
                prepare(operation, name)
            else:
                tf_service_generic(operation, allowed_actions["service"][step], name)

        else:
            operation.logger.error("Unallowed service %s" % name)
            sys.exit()

    operation.logger.info("Finished service action sucessfully")


main.add_command(init)
main.add_command(tf)
main.add_command(ans)
main.add_command(service)

if __name__ == "__main__":
    main()
