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
    "fortigate",
    "grafana",
    "keycloak"
]

# supported_public_clouds = [
#     "aws",
#     "azure",
#     "gcp",
#     "ovh"
# ]

# supported_private_providers = [
#     "nutanix",
#     "vsphere"
# ]

supported_providers = {
    "public" : [
        {
            "name" : "aws",
            "common_name": "Amazon AWS",
            "default_base_folder": "aws"
        },
        {
            "name" : "azure",
            "common_name": "Microsoft Azure",
            "default_base_folder": "azure"
        },
        {
            "name" : "gcp",
           "common_name": "Google Cloud Services",
            "default_base_folder": "gcp"
        },
        {
            "name" : "ovh",
            "common_name": "OVH Cloud",
            "default_base_folder": "ovh"
        }
    ],
    "private" : [
        {
            "name" : "nutanix",
            "common_name": "Nutanix Hyper-Converged Infrastructure",
            "default_base_folder": "nutanix"
        },
        {
            "name" : "vsphere",
            "common_name": "VMware ESXi",
            "default_base_folder": "vsphere"
        },
        {
            "name" : "proxmox",
            "common_name": "Proxmox VE",
            "default_base_folder": "vsphere"
        }
    ]
}

terraform_vm_resource_name = {
    "aws": "aws_instance",
    "azure": "azurerm_virtual_machine",
    "gcp": "google_compute_instance",
    "vsphere": "vsphere_virtual_machine",
    "nutanix": "nutanix_virtual_machine"
}

provider_secrets_requirements = {
    "nutanix": {
        "required": [
            "TF_VAR_nutanix_timeout",
            "TF_VAR_nutanix_port",
            "TF_VAR_nutanix_insecure",
            "TF_VAR_nutanix_user",
            "TF_VAR_nutanix_password",
            "TF_VAR_nutanix_endpoint"
        ],
        "optional": [
            "CLOUDTIGER_BACKEND_USERNAME",
            "CLOUDTIGER_BACKEND_PASSWORD",
            "CLOUDTIGER_BACKEND_ADDRESS",
            "CLOUDTIGER_BACKEND_DB"
        ]
    }
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

non_scope_init_actions = [
    "folder",
    "config"
]

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
        "set_admin": "set_admin",
        "3": "set_admin",
        "set_mode": "set_mode",
        "4": "set_mode",
        "set_mode": "set_mode",
        "5": "set_dns",
        "set_dns": "set_dns",
        "6": "delete_dns",
        "delete_dns": "delete_dns",
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
        "S": "setup",
        "setup": "setup",
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
        "convert": "convert",
        "C": "convert",
        "destroy": "destroy",
        "D": "destroy",
        "import": "import"
    },
    "admin": {
        "gather": "gather",
        "G": "gather",
        "dns": "dns",
        "D": "dns",
        "vms": "vms",
        "V": "vms",
        "subnets": "subnets",
        "S": "subnets",
        "clusters": "clusters",
        "C": "clusters",
        "M": "monitoring",
        "monitoring": "monitoring"
    },
    "config": {
        "generate": "generate",
        "G": "generate"
    }
}

common_environments = [
    "prod",
    "preprod",
    "staging",
    "integration",
    "qa",
    "dev",
    "test",
    "demo",
    "sandbox"
]

common_internal_customers = [
    "dev",
    "demo",
    "devops",
    "front",
    "back",
    "sys",
    "internal"
]

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

environment_name_mapping = {
    "preprod" : "pp",
    "prod" : ""
}

custom_ssh_port_per_vm_type = {
    "sftp" : "8022"
}

normalized_naming = {
    "environment": {
        "prod": "prd",
        "preprod": "ppr",
        "staging": "stg",
        "integration": "int",
        "qa": "qa",
        "dev": "dev",
        "test": "tst",
        "demo": "dmo",
        "sandbox": "sbx"
    },
    "type": {
        "kubenode": "k8nod",
        "kubenode_high_memory": "k8ram",
        "kubenode_high_compute": "k8cpu",
        "kubemaster": "k8mst",
        "standard": "std"
    },
    "customer": {
        "dev": "dev",
        "demo": "demo",
        "devops": "dvps",
        "front": "frt",
        "back": "bck",
        "sys": "sys",
        "internal": "int"
    }
}

clusterized_hypervisors = [
    "nutanix",
    "vsphere"
]

worldwide_cloud_datacenters = {
    "aws" : {
        "datacenters" : [
            "us-east-1",
            "us-west-1",
            "us-central-1",
            "us-central-2",
            "us-east-2",
            "ca-central-1",
            "eu-west-1",
            "eu-west-2",
            "eu-central-1",
            "eu-west-3",
            "eu-west-4",
            "eu-north-1",
            "ap-northeast-1"
        ],
        "default_datacenter" : "ca-central-1"
    },
    "azure" : {
        "datacenters" : [
            "eastus",
            "westus",
            "westus",
            "northcentralus",
            "eastus2",
            "canadacentral",
            "northeurope",
            "uksouth",
            "westeurope",
            "francecentral",
            "northeurope",
            "japaneast",
            "japanwest"
        ],
        "default_datacenter" : "canadacentral"
    },
    "gcp" : {
        "datacenters" : [
            "us-east1",
            "us-east4",
            "us-central1",
            "us-west1",
            "us-west2",
            "northamerica-northeast1",
            "europe-west2",
            "europe-west1",
            "europe-west3",
            "europe-west6",
            "asia-northeast1",
            "asia-northeast2"
        ],
        "default_datacenter" : "northamerica-northeast1"
    }
}

worldwide_cloud_default_network = {
    "default_cidr" : "10.0.0.0/16",
    "default_cidr_per_env" : {
        "prod" : "12.0.",
        "preprod": "16.0.",
        "staging": "13.0.",
        "integration": "18.0.",
        "qa": "15.0.",
        "dev" : "11.0.",
        "test": "10.0.",
        "demo": "14.0.",
        "sandbox": "17.0."
    },
    "subnets" : [
        {
            "name" : "dmz",
            "cidr_block_suffix": "5.0/24",
            "availability_zone": "a",
            "public": True
        },
        {
            "name": "datalake",
            "cidr_block_suffix": "10.0/24",
            "availability_zone": "a",
            "public": False
        }
    ]
}

pvs_suffix = {
    "aws": "p1",
    "azure": "1",
    "gcp": "1"
}