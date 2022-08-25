"""
This file stores some common data structures
"""

DEFAULT_ANSIBLE_PYTHON_INTERPRETER = "python3"
DEFAULT_SSH_PORT = "22"

available_infra_services = [
    "kubernetes",
    "network",
    "policy",
    "profile",
    "role",
    "vm"
]

available_api_services = [
    "nexus",
    "gitlab",
    "fortigate"
]

terraform_vm_resource_name = {
    "aws": "aws_instance",
    "azure": "azurerm_virtual_machine",
    "gcp": "google_compute_instance",
    "vsphere": "vsphere_virtual_machine",
    "nutanix": "nutanix_virtual_machine"
}

provider_secrets_helper = {
    "tf_backend": {
        "keys" : [
            {
                "helper" : "Please provide the address of your remote Terraform backend",
                "name" : "CLOUDTIGER_BACKEND_ADDRESS"
            },
            {
                "helper" : "Please provide the username of your remote Terraform backend",
                "name" : "CLOUDTIGER_BACKEND_USERNAME"
            },
            {
                "helper" : "Please provide the password of your remote Terraform backend",
                "name" : "CLOUDTIGER_BACKEND_PASSWORD",
                "sensitive": True
            },
            {
                "helper" : "Please provide the database of your remote Terraform backend",
                "name" : "CLOUDTIGER_BACKEND_DB"
            }
        ]
    },
    "aws": {
        "templates": [".env.tpl"],
        "initial_helper" : "We are now going to ask you your AWS credentials",
        "keys" : [
            {
                "helper": "Please provide your AWS access key ID",
                "name": "AWS_ACCESS_KEY_ID",
                "sensitive": False
            },
            {
                "helper": "Please provide your AWS secret access key",
                "name": "AWS_SECRET_ACCESS_KEY",
                "sensitive": True
            },
            {
                "helper": "Please provide your AWS default region",
                "name": "AWS_DEFAULT_REGION",
                "sensitive": False
            }
        ],
        "final_helper": "You are now done with setting your AWS credentials for CloudTiger"
    },
    "azure": {
        "templates": [".env.tpl", "az_account.json.tpl", "service_principal.json.tpl"],
        "initial_helper" : """Azure credentials are completely contained in files downloaded on the Azure GUI.
Please follow the instructions available here :
https://docs.microsoft.com/en-us/azure/virtual-machines/linux/terraform-install-configure""",
        "keys" : [],
        "final_helper": """Once you have set the files az_account.json and service_principal.json in secrets/azure folder you are ready to use CloudTiger for Azure"""
    },
    "gcp": {
        "templates": [".env.tpl", "credentials.json.tpl"],
        "initial_helper" : """GCP credentials are completely contained in files downloaded on the GCP GUI.
Please follow the instructions available here :
https://cloud.google.com/community/tutorials/getting-started-on-gcp-with-terraform.""",
        "keys" : [
            {
                "helper": "Please provide the path to your GCP credentials file",
                "name": "CREDENTIALS_FILE",
                "sensitive": False
            },
            {
                "helper": "Please provide your GCP project ID. You can find it in the credentials.json",
                "name": "PROJECT_ID",
                "sensitive": False
            },
            {
                "helper": "Please provide your GCP region",
                "name": "REGION",
                "sensitive": False
            }
        ],
        "final_helper": "You are now done with setting your GCP credentials for CloudTiger"
    },
    "vsphere": {
        "templates": [".env.tpl"],
        "initial_helper" : "We are now going to ask you your vSphere credentials",
        "keys" : [
            {
                "helper": "Please provide your vSphere username",
                "name": "TF_VAR_vsphere_user",
                "sensitive": False
            },
            {
                "helper": "Please provide your vSphere password",
                "name": "TF_VAR_vsphere_password",
                "sensitive": True
            },
            {
                "helper": "Please provide your vSphere URL",
                "name": "TF_VAR_vsphere_url",
                "sensitive": False
            }
        ],
        "final_helper": "You are now done with setting your vSphere credentials for CloudTiger"
    },
    "nutanix": {
        "templates": [".env.tpl"],
        "initial_helper" : "We are now going to ask you your Nutanix credentials",
        "keys" : [
            {
                "helper": "Please provide your Nutanix username",
                "name": "TF_VAR_nutanix_user",
                "sensitive": False
            },
            {
                "helper": "Please provide your Nutanix password",
                "name": "TF_VAR_nutanix_password",
                "sensitive": True
            },
            {
                "helper": "Please provide your Nutanix URL",
                "name": "TF_VAR_nutanix_endpoint",
                "sensitive": False
            },
            {
                "helper": "Please provide timeout for Nutanix connection",
                "name": "TF_VAR_nutanix_timeout",
                "sensitive": False,
                "default": 5
            },
            {
                "helper": "Please provide port for Nutanix URL connection",
                "name": "TF_VAR_nutanix_port",
                "sensitive": False,
                "default": 9440
            },
            {
                "helper": "Is your Nutanix connection insecure ? (write true or false)",
                "name": "TF_VAR_nutanix_insecure",
                "sensitive": False,
                "default": "false"
            }
        ],
        "final_helper": "You are now done with setting your Nutanix credentials for CloudTiger"
    },
}

allowed_actions = {
    "init": {
        "folder": "folder",
        "F": "folder",
        "config": "config",
        "C": "config",
        "ssh_keys": "set_ssh_keys",
        "0": "set_ssh_keys",
        "configure_ip": "configure_ip",
        "1": "configure_ip",
        "scope_folder": "prepare_scope_folder",
        "2": "prepare_scope_folder",
        "meta_aggregate": "init_meta_aggregate",
        "M1": "init_meta_aggregate",
        "meta_distribute": "init_meta_distribute",
        "M2": "init_meta_distribute"
    },
    "tf": {
        "provider": "set_provider",
        "0": "set_provider",
        "init": "init",
        "1": "init",
        "apply": "apply",
        "2": "apply",
        "refresh": "refresh",
        "R": "refresh",
        "destroy": "destroy",
        "D": "destroy",
        "output": "output",
        "O": "output",
        "plan": 'plan',
        "import": "import",
        "I": "import",
        "console": "console",
        "rm": "rm"
    },
    "ans": {
        "inventory": "create_inventory",
        "1": "create_inventory",
        "prep_ansible": "prepare_ansible",
        "2": "prepare_ansible",
        "setup_ssh": "setup_ssh_connection",
        "H": "setup_ssh_connection",
        "dependencies": "install_ansible_dependencies",
        "D": "install_ansible_dependencies",
        "playbooks": "install_ansible_playbooks",
        "P": "install_ansible_playbooks",
        "run_ansible": "execute_ansible",
        "3": "execute_ansible",
        "Z": "securize",
        "securize": "securize",
        "meta_aggregate": "meta_aggregate",
        "M1": "meta_aggregate",
        "meta_distribute": "meta_distribute",
        "M2": "meta_distribute"
    },
    "service": {
        "prepare": "prepare",
        "0": "prepare",
        "init": "init",
        "1": "init",
        "apply": "apply",
        "2": "apply",
        "plan": "plan",
        "P": "plan",
        "refresh": "refresh",
        "R": "refresh",
        "destroy": "destroy",
        "D": "destroy",
        "import": "import"
    },
    "admin": {
        "gather": "gather"
    }
}

common_group_names = [
    "lb",
    "keycloak",
    "nginx",
    "haproxy",
    "mongo",
    "postgres",
    "kubemaster",
    "kubenode",
    "kube",
    "spark",
    "gitlab",
    "nexus",
    "elastic",
    "ftp"
]

common_environment_tags = {
    "pp": "preprod",
    "preprod": "preprod",
    "pprod": "preprod",
    "prod": "prod",
    "recload": "recload",
    "rec": "recload",
    "dev": "dev",
    "admin": "admin",
    "sandbox": "sandbox",
    "sdbx": "sandbox"
}

services_resources_mapping = {
    "nexus": {
        "repositories": [
            ("", "nexus_repository.repositories"),
            ("blob-store-", "nexus_blobstore_file.blobstore")
        ],
        "privileges": [
            ("", "nexus_privilege.privileges")
        ],
        "roles": [
            ("", "nexus_role.roles"),
        ],
        "users": [
            ("", "nexus_security_user.users"),
        ],
    }
}
