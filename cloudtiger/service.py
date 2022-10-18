""" CloudTiger functions for using Terraform with non-infrastructure services."""
import json
import os
import shutil
import yaml

from cloudtiger.cloudtiger import Operation
from cloudtiger.common_tools import bash_action, j2
from cloudtiger.data import services_resources_mapping
from cloudtiger.specific.forti import ConfigParser
from cloudtiger.specific.parsing import FortiNetworking



def prepare(operation: Operation, service):
    """ This function prepare the terraform folder in <GITOPS>/scopes/<SCOPE>/<SERVICE>
    for the chosen service

    :param operation: Operation, the current Operation
    :param service: str, the service invoked
    """

    # prepare service Terraform files
    service_folder = os.path.join(operation.scope_folder, service)
    os.makedirs(service_folder, exist_ok=True)

    template_folder = os.path.join(operation.libraries_path, "internal",
                                   "terraform_services", service)
    operation.logger.debug("Creating service folder from template : %s" % template_folder)
    shutil.copytree(template_folder, service_folder, dirs_exist_ok=True)

    # copying needed provider's modules into project root
    operation.logger.debug(
        "Creating Terraform modules folder from libraries folder : %s" % operation.libraries_path)
    tf_modules = os.path.join(operation.libraries_path, "terraform", "services",
                              service)
    target_modules = os.path.join(operation.project_root, "terraform", "services", service)
    os.makedirs(target_modules, exist_ok=True)
    shutil.copytree(tf_modules, target_modules, dirs_exist_ok=True)

    # copying input for the service from the config.yml file in the
    # scopes/<SCOPE>/<SERVICE>/service_config.yml file
    service_config_file = os.path.join(operation.scope_folder, service,
                                       "service_config.auto.tfvars.json")
    with open(service_config_file, "w") as f:
        json.dump({service + "_config": operation.scope_config_dict[service]}, f, indent=4)

    # setting the main.tf for the service called
    template_file = os.path.join(service_folder, "main.tf.j2")
    j2(operation.logger, template_file, operation.scope_config_dict,
       os.path.join(service_folder, "main.tf"))

    if os.path.exists(template_file):
        os.remove(template_file)


def tf_service_generic(operation, tf_action, service):
    """ This function executes the wrapped Terraform command for the chosen provider

    :param operation: Operation, the current Operation
    :param tf_action: str, the Terraform action called (init, apply, plan, destroy, etc)
    :param service: str, the service invoked
    """

    operation.logger.info("Executing Terraform command %s", tf_action)

    service_folder = os.path.join(operation.scope_folder, service)
    terraform_service_output = os.path.join(operation.scope_folder, service,
                                            "terraform_" + service + "_output.json")

    if os.path.exists(terraform_service_output):
        os.remove(terraform_service_output)

    if tf_action not in ["output", "list", "import"]:
        command = format("terraform %s" % tf_action)

        # if tf action is init, we need to set the environment variables for reaching the backend if
        # backend is used
        if (tf_action == "init") & (operation.scope_config_dict.get("use_tf_backend_for_service", False)):
            command += format(' -backend-config="conn_str=postgres://%s:%s@%s/%s"' %
                              (
                                  os.environ['CLOUDTIGER_BACKEND_USERNAME'],
                                  os.environ['CLOUDTIGER_BACKEND_PASSWORD'],
                                  os.environ['CLOUDTIGER_BACKEND_ADDRESS'],
                                  os.environ['CLOUDTIGER_BACKEND_DB']
                              ))
            command += format(' -backend-config="schema_name=%s/%s"' % (operation.scope, service))

        bash_action(operation.logger, command, service_folder, os.environ, operation.stdout_file)

    if tf_action in ["apply", "refresh", "output", "plan"]:
        os.makedirs(os.path.join(operation.scope_folder, service), exist_ok=True)
        command = "terraform output -json"
        bash_action(operation.logger, command, service_folder, os.environ, terraform_service_output)

    if tf_action == "import":
        # creating the list of import commands for all resources
        list_import_data = [(service, resource_elt, tf_prefix, terraform_resource) for resource_type, resource_elts in operation.scope_config_dict[service].items() for (tf_prefix, terraform_resource) in services_resources_mapping[service][resource_type] for resource_elt in resource_elts.keys()]
        list_import_command = [f"terraform import module.{service}.{terraform_resource}[\\\"{resource_name}\\\"] {tf_prefix}{resource_name}" for service, resource_name, tf_prefix, terraform_resource in list_import_data]
        
        operation.logger.info(f"List of imports : {list_import_command}")

        # importing vms
        for command in list_import_command:
            bash_action(operation.logger, command, service_folder, os.environ, operation.stdout_file)

def convert(operation, service, src):
    config_parser = ConfigParser()
    data_json = config_parser.parse_file(os.path.join(src))
    fortigate_parser = FortiNetworking()
    result = {}
    domains = {}
    data_json = getFortigateDomain(domains, data_json)
    for vdom_name, vdom in data_json.items():
        result[vdom_name] = {}
        # firewall policy
        for resource_name, resource in  vdom.items():
            result[vdom_name][resource_name] = fortigate_parser.get_BT_format(resource_name, resource)
            if result[vdom_name][resource_name] == {}:
                del result[vdom_name][resource_name]
    f = open(operation.scope_config, "w")
    yaml.dump(result, f)
    f.close()

def getFortigateDomain(domains, data):
    for vdom_name, vdom in data.items():
        if vdom_name == 'vdom':
            getFortigateDomain(domains, vdom)
        elif vdom_name != "root": 
            domains[vdom_name] = vdom
    return domains
