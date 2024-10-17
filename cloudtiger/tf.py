"""CloudTiger functions for running Terraform actions."""
import json
import os
import random
import string

from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import bash_action
from cloudtiger.data import terraform_vm_resource_name, supported_providers
from cloudtiger.specific.nutanix import get_vm_nutanix_uuid
from cloudtiger.init import *

DEFAULT_PASSWORD_LENGTH = 64

def tf_generic(operation: Operation, tf_action):
    """ This function executes the wrapped Terraform command for the chosen provider

    :param operation: Operation, the current Operation
    :param tf_action: str, the Terraform action called (init, apply, plan, destroy, etc)
    """

    operation.logger.info("Executing Terraform command %s", tf_action)

    # create a custom environment for the ansible bash command
    tf_env = os.environ

    # add a random default password
    characters = string.ascii_letters + string.digits  # Uppercase letters, lowercase letters, and digits
    tf_env['TF_VAR_default_password'] = ''.join(random.choice(characters) for _ in range(DEFAULT_PASSWORD_LENGTH))

    # add current scope path as default folder
    if operation.provider == "vsphere":
        splitted_scope = operation.scope.split(os.sep)
        # by default we remove the first folder of the scope (usually used to define the cluster name)
        if len(splitted_scope) > 1:
            splitted_scope = splitted_scope[1:]
        tf_env['TF_VAR_scope_folder'] = "/".join(splitted_scope)

    # if tf action is not output, import or rm, we need to provide the tfvars files
    # as extra parameters
    # to the terraform command
    if tf_action not in ["output", "import", "rm"]:

        command = format("terraform %s %s" % (tf_action, " ".join(
            ["--var-file=services/" + service + ".tfvars" for service in operation.used_services]
        )))

        # if tf action is init, we need to set the environment variables for reaching the backend if
        # backend is used
        if (tf_action == "init") & (operation.scope_config_dict.get("use_tf_backend", False)):
            command += format(' -backend-config="conn_str=postgres://%s:%s@%s/%s?sslmode=disable"' %
                              (
                                  os.environ['CLOUDTIGER_BACKEND_USERNAME'],
                                  os.environ['CLOUDTIGER_BACKEND_PASSWORD'],
                                  os.environ['CLOUDTIGER_BACKEND_ADDRESS'],
                                  os.environ['CLOUDTIGER_BACKEND_DB']
                              ))
            command += format(' -backend-config="schema_name=%s"' % operation.scope)

        # if we are running a 'plan', we dump the output inside a dedicated json file
        if tf_action == "plan":
            command += " -json"
            test_tf_plan_file = os.path.join(operation.scope_terraform_folder, "tf_plan.json")
            if os.path.exists(test_tf_plan_file):
                os.remove(test_tf_plan_file)
            bash_action(operation.logger, command, operation.scope_terraform_folder,
                        tf_env, test_tf_plan_file)
            with open(test_tf_plan_file, "r") as f:
                test_tf_plan = f.read().split("\n")
            test_tf_plan = {
                "line_" + str(i): json.loads(test_tf_plan[i])
                for i in range(len(test_tf_plan)) if test_tf_plan[i] != ""
            }
            # test_tf_plan = load_json(operation.logger, test_tf_plan_file)
            nice_test_tf_plan_file = os.path.join(
                operation.scope_terraform_folder, "tf_nice_plan.json")
            with open(nice_test_tf_plan_file, "w") as f:
                json.dump(test_tf_plan, f, indent=4)
        else:
            if operation.tf_no_lock:
                command += " -lock=false"

            if tf_action == "init" :
                if operation.tf_reconfigure :
                    command += " -reconfigure"

            bash_action(operation.logger, command, operation.scope_terraform_folder,
                        tf_env, operation.stdout_file)

            # if the action is 'tf apply' and we have VMs we dump the default password we used
            private_supported_providers = [prov['name'] for prov in supported_providers["private"]]
            if (tf_action == "apply") and (operation.provider in private_supported_providers):
                if ("vm" in operation.used_services) or ("vm_template" in operation.used_services):
                    default_password_file = os.path.join(operation.scope_terraform_folder, ".env")
                    with open(default_password_file, "w") as f:
                        f.write(f"export TF_VAR_default_password={tf_env['TF_VAR_default_password']}")

    # 'import' is a non-terraform CLI, custom command, that remove all VMs of the
    # config.yml from the state if they are in the state, then reimport them.
    # It is useful for importing VMs created independently into Cloudtiger
    if tf_action == "import":

        # listing existing vm in state
        temp_vm_list_file = os.path.join(operation.scope_terraform_folder, "temp_vm_list_file.txt")
        command = "terraform state list"
        bash_action(operation.logger, command, operation.scope_terraform_folder,
                    tf_env, output=temp_vm_list_file)

        # purging state from vms
        with open(temp_vm_list_file, "r") as f:
            res_list = f.read().split('\n')
            for res in res_list:
                mother_module = res.split('[')[0]
                if (mother_module == "module.vm") & (len(res) > len(mother_module)):
                    res = res.replace('"', '\\"')
                    command = "terraform state rm " + res  # + ' -lock=false'
                    operation.logger.info('Purging VM %s from tfstate' % res)
                    bash_action(operation.logger, command, operation.scope_terraform_folder,
                                tf_env, output=operation.stdout_file)

        if os.path.exists(temp_vm_list_file):
            os.remove(temp_vm_list_file)

        # importing vms into state
        vms = [(vm_name, vm) for network_name, network_content
               in operation.scope_config_dict["vm"].items()
               for subnet_name, subnet_content in network_content.items()
               for vm_name, vm in subnet_content.items()]

        # get the detailed name of the vms for the import, according to the provider
        vms_import_name = vms
        if operation.provider == "nutanix":
            vms_import_name = [(vm_name, get_vm_nutanix_uuid(operation, vm_name))
                               for (vm_name, vm) in vms]
        if operation.provider == "vsphere":
            vms_import_name = [
                (vm_name, "/".join(["", vm["datacenter"],
                                    "vm",
                                    vm["extra_parameters"]["folder"].replace(" ", "\ "),
                                    vm.get("vm_name", vm_name)]))
                for (vm_name, vm) in vms]
        if operation.provider not in ["nutanix", "vsphere"]:
            vms_import_name = [(vm_name, vm_name) for (vm_name, _) in vms]

        # creating the list of import commands for all vms
        commands = [
            format("terraform import %s module.vm[\\\"%s\\\"].%s.virtual_machine %s" %
                   (" ".join(["--var-file=services/" + service + ".tfvars"
                              for service in operation.used_services]),
                    vm_name,
                    terraform_vm_resource_name[operation.provider],
                    vm_import_name)
                   )
            for (vm_name, vm_import_name) in vms_import_name
        ]

        # importing vms
        for command in commands:
            bash_action(operation.logger, command, operation.scope_terraform_folder,
                        tf_env, operation.stdout_file)

    if tf_action == "rm":
        commands = [
            format("terraform state rm module.vm[\\\"%s\\\"].%s.virtual_machine" %
                   (vm_name, terraform_vm_resource_name[operation.provider]))
            for (vm_name, vm_import_name) in vms_import_name
        ]

        for command in commands:
            bash_action(operation.logger, command, operation.scope_terraform_folder,
                        tf_env, operation.stdout_file)

    # at the end of a terraform apply/refresh/output command, we execute a 'terraform output'
    if tf_action in ["apply", "refresh", "output"]:
        os.makedirs(operation.scope_inventory_folder, exist_ok=True)
        command = "terraform output -json"
        bash_action(operation.logger, command, operation.scope_terraform_folder, tf_env,
                    operation.terraform_output, single_output=True)

    if tf_action == "destroy":
        delete_dns(operation)
        if operation.provider == "vsphere":
            # release the IPs
            scope_ips = os.path.join(operation.project_root, "config", operation.scope,
                                     "config_ips.yml")
            if os.path.exists(scope_ips):
                os.remove(scope_ips)
