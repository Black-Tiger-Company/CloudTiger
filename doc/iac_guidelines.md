# Terraform modules guidelines

- [Terraform modules guidelines](#terraform-modules-guidelines)
	- [Development quickstart](#development-quickstart)
	- [How to write your code](#how-to-write-your-code)
		- [How Terraform works](#how-terraform-works)
			- [Provider](#provider)
			- [Variables](#variables)
			- [Data and resources](#data-and-resources)
			- [Outputs](#outputs)
			- [Modules](#modules)
		- [Structure of Terraform code inside CloudTiger](#structure-of-terraform-code-inside-cloudtiger)
			- [Main Terraform folder](#main-terraform-folder)
			- [Terraform modules folder](#terraform-modules-folder)
		- [Adding a new module](#adding-a-new-module)
	- [Important notice](#important-notice)
		- [Terminology digression](#terminology-digression)
		- [Length of names and labels](#length-of-names-and-labels)
		- [Map vs list](#map-vs-list)
		- [Looping on modules](#looping-on-modules)
		- [Interoperability between cloud providers](#interoperability-between-cloud-providers)
		- [Readability and simplicity of the architecture](#readability-and-simplicity-of-the-architecture)

This document aims at describing code writing guidelines for developing Terraform architectures and modules.

## Development quickstart

If you want to edit an existing Terraform module of CloudTiger or develop a new one, follow this steps :

- Get a project root prepared for CloudTiger
- Install the CloudTiger CLI in "development" mode (using `pip3 install -e` option)
- Create yourself a "development" scope in the gitops project you chose
- Create a file `config.yml` in `<YOUR_GITOPS_FOLDER/config/<YOUR_DEVELOPMENT_SCOPE>`
- Put the following line into it : `provider: <CHOSEN_PROVIDER>`
- In the gitops folder, run :
	- `cloudtiger config/<YOUR_DEVELOPMENT_SCOPE> init 0`
	- `cloudtiger config/<YOUR_DEVELOPMENT_SCOPE> init 2`
	- `cloudtiger config/<YOUR_DEVELOPMENT_SCOPE> tf init`

Then start editing your Terraform code in `<CLOUDTIGER_SOURCES>/cloudtiger/libraries/terraform/providers/<CHOSEN_PROVIDER>/<CHOSEN_MODULE>`. If you do not know how to write your code, go to the next section of this document.

Every time you want to test your code, do the following operations :

- `cloudtiger config/<YOUR_DEVELOPMENT_SCOPE> init 2` (it will copy your modifications of Terraform files into `<YOUR_GITOPS_FOLDER/terraform` and update the content of the folder `<YOUR_GITOPS_FOLDER/scopes/<YOUR_DEVELOPMENT_SCOPE>/terraform` which is the folder actually used by the Terraform executable)
- `cloudtiger config/<YOUR_DEVELOPMENT_SCOPE> tf plan` (if you only wish to show the plan)
- `cloudtiger config/<YOUR_DEVELOPMENT_SCOPE> tf apply` (if you wish to apply your modifications)

## How to write your code

### How Terraform works

Terraform is a standalone executable, that you execute on a folder containing files expected by Terraform.

All files with a `.tf` extension inside this folder will be automatically loaded by Terraform during execution.

All the code written in all the `.tf` files will be used by Terrafom at execution time. You can write your code in as many files as you want, there is not enforced structure.

Files with a `.tfvars` and `.tfvars.json` extension allow to define variables respectively in HCL and json format for the execution. A file named `terraform.tfvars` and all files with a `.auto.tfvars` or `.auto.tfvars.json` will be automatically loaded, otherwise you have to explicitely list the `.tfvars` files to load by the Terrafom CLI at execution.

#### Provider

Inside the `.tf` files, Terraform will be looking for a block like this :

```tf
terraform {
	required_providers {
		<CHOSEN_PROVIDER> = {
			...
		}
	}
}
```

that will specify your chosen cloud provider, and a block like this :

```tf
provider "<CHOSEN_PROVIDER>" {
	<PROVIDER_CREDENTIALS> = ...
}
```

that will specify the credentials to connect to the provider

#### Variables

Terraform uses two kinds of variables :

- "public" variables declared externally at execution
- "internal" variables

The "public" variables are simply named "variables", the "internal" variables are called "locals" by Terraform

To use a variable inside Terraform, you have to declare it like this :

```tf
variable "<VARIABLE_NAME>" {
	...
}
```

Then you refer to it like this : `var.<VARIABLE_NAME>`

The values of all variables must be set at execution time, either using `.tfvars` files, or directly in the arguments of the CLI. If no values are set, Terraform will look at the variable definition if a default value is set. If not, it will return an error

To use a local variable, you have to declare it like this :

```tf
locals  {
	"<VARIABLE_NAME>" = ...
}
```

Then you refer to it like this : `local.<VARIABLE_NAME>`

#### Data and resources

Terraform can either dump the content of existing cloud resources, or create them

To read content of existing resources, you use `data` blocks :

```tf
data DATA_TYPE DATA_NAME {

}
```

To create resources, you use `resource` blocks :

```tf
resource DATA_TYPE DATA_NAME {

}
```

#### Outputs

An "output" is a kind of variable that will be dumped by Terraform at the end of its execution. It is useful to pipe the results of Terraform with other actions.

You declare it like this :

```tf
output "<OUTPUT_NAME>" {
	...
}
```

Output content can refers to variables, locals, resources or data.

#### Modules

Modules are a way to make Terraform code reusable. A module is a separated folder, containing all the needed files by Terraform (i.e. variables, resources, data, etc.) at the exception of the provider field, and the `terraform {}` block.

It means that insides modules you have to declare input variables and outputs.

You can call a module inside your main Terraform folder like this :

```tf
module "MODULE_NAME" {
	source = "<PATH_TO_MODULE_FOLDER>
	MODULE_VARIABLE_ONE = MODULE_VARIABLE_ONE_VALUE
	...
}
```

All the variables of the module must have their values provided at execution time, either by setting them in the `module` block, or by using default values in the declaration of the variables in the module folder.

Then, you can get the values contained in the `outputs` of the module folder by calling `module.MODULE_NAME.OUTPUT_NAME` in the main Terraform folder.

### Structure of Terraform code inside CloudTiger

#### Main Terraform folder

Inside CloudTiger, all the modules are listed in `cloudtiger/cloudtiger/libraries/terraform/providers/<CHOSEN_PROVIDER>` for cloud providers and in `cloudtiger/cloudtiger/libraries/terraform/services/<CHOSEN_SERVICE>` for services with API.

The content of the "main" Terraform folder is provided as "templates". There are two of them :

- `cloudtiger/cloudtiger/libraries/internal/terraform_providers` for creating cloud resources
- `cloudtiger/cloudtiger/libraries/internal/terraform_services ` for managing API services

The template Terraform folder has the following structure in CloudTiger :

```txt
└── cloudtiger
    └── libraries
        └── internal
            ├── terraform_providers
            │   ├── disk_standard.yml
            │   ├── firewall_standard.yml
            │   └── vm_standard.yml
            ├── terraform_providers
            │   ├── services
            │   │   ├── vm.tfvars.j2
            │   │   ├── network.tfvars.j2
            │   │   ...
            │   ├── modules.tf.j2
            │   ├── outputs.tf.j2
            │   ├── provider.tf.j2
            │   ├── terraform.tfvars.j2
            │   ├── main.tf
            │   └── variables.tf
            └── terraform_services
                ├── <SERVICE>
                │ └── main.tf.j2
                ...
```

The `cloudtiger config/<SCOPE> init 2` command generates the following folder :

```txt
└── scopes
    └── <SCOPE_NAME>
        └── terraform
            ├── configuration.yml
            ├── main.tf
            ├── services
            │   ├── network.tfvars
            │   ├── vm.tfvars
            │   │   ...
            ├── modules.tf
            ├── outputs.tf
            ├── provider.tf
            ├── terraform.tfstate
            ├── terraform.tfstate.backup
            ├── terraform.tfvars
            └── variables.tf
...
```

In greater details :

- `provider.tf.j2` -> `provider.tf` : used to import the credentials for the chosen cloud provider
- `variables.tf` : definition of the variables used at the highest level of Terraform
- `terraform.tf.j2` -> `terraform.tfvars` defines the basic variables of the architecture
- `main.tf.j2` -> `modules.tf` is used to import Terraform modules from the Terraform library and provide them inputs
- `services/*.tfvars.j2` -> `services/*.tfvars` : the .tfvars files in this subfolder define the parameters for all modules of the architecture (networks, virtual machines, kubernetes clusters, databases, etc), in an easy-to-understand structure
- `main.tf.j2` -> `main.tf` remaps the inputs from `terraform.tfvars` and `services/*.tfvars` into more complete Terraform structures given as inputs to the library modules, through `modules.tf`
-`outputs.tf.j2` ->  `outputs.tf` defines the data that will be dump as output at the application of Terraform on the folder structure
-`disk_standard.yml` ->  `disk_standard.auto.tfvars.json` defines the standardized disk values
-`firewall_standard.yml` ->  `firewall_standard.auto.tfvars.json` defines the standardized firewall values
-`vm_standard.yml` ->  `vm_standard.auto.tfvars.json` defines the standardized VM values

#### Terraform modules folder

Typical "module" structure :

```txt
├── terraform
│   ├── docker_registry
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── function
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── kafka
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── <MODULE_NAME>
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
...
```

In greater details :

- "<MODULE_NAME>" : functional name of the module, that will be imported from the `modules.tf` file in the scope definition
- variables.tf : declaration of Terraform variables
- main.tf : definition of the resources
- outputs.tf : declaration of the outputs

WARNING : every Terraform module should have this structure (it is a Terraform demand, not a demand from this project's design)

### Adding a new module

In order to develop/edit a new module, you need to :

- create the module folder in `cloudtiger/libraries/terraform`, and create `main.tf`, `variables.tf` and `outputs.tf` in this folder
- add the module in `cloudtiger/cloudtiger/libraries/internal/terraform_providers/modules.tf.j2`, with the condition to activate it (ususally have a key defined in `config.yml`)
- create the file `cloudtiger/cloudtiger/libraries/internal/terraform_providers/<MODULE>.tfvars.j2` listing the variables for the module
- edit the file `cloudtiger/cloudtiger/libraries/internal/terraform_providers/outputs.tf.j2` to define the outputs of the module if necessary.

### Adding a new service

In order to develop/edit a new service, you need to :

- create the service folder in `cloudtiger/libraries/internal/terraform_services`, and create a `main.tf.j2` file in this folder

The `main.tf.j2` file should have a structure close to this one :

```tf
terraform {
  required_providers {
    <PROVIDER_NAME> = {
      source = <SOURCE>
      version = <VERSION>
    }
  }
}

provider "<PROVIDER_NAME" {
  <KEY> = <VALUE>
  ...
}

variable "<SERVICE_NAME>_config" {}

variable "<OTHER_VARIABLES>" {}

...

### <SERVICE_NAME> module
module "<SERVICE_NAME>" {
  source = "{{ ''.join(["../"] * (scope.split('/')|length + 2)) }}terraform/services/<SERVICE_NAME>/resources"

	<SERVICE_NAME>_config = var.<SERVICE_NAME>
}

### another <SERVICE_NAME> module
module ...
```

- then, you need to create the modules for your service in a new folder `cloudtiger/libraries/terraform/services/<SERVICE_NAME>`. Follow the instructions above about "Creating a new module"
- then, you have to declare the new service in the list of available services in `cloudtiger/data.py` :

```python
...
available_api_services = [
    "nexus",
    "gitlab",
    "<SERVICE_NAME>" ### <- add your service name in this list
]
...
```

- finally, add the helper for your new service in the helper of the `service` function in `cloudtiger/cli.py` :

```python
@click.pass_context
def service(context, name, step):
    """ Service configuration through Terraform
\nservice names:
\n- gitlab                : configure Gitlab
\n- nexus                 : configure Nexus
\n- <SERVICE_NAME>        : <SERVICE_DESCRIPTION>
...
```

## Important technical points

### Terminology digression

Terraform provides the option of "workspace" : you can have multiple distinct Terraform states into the same Terraform folder by creating and switching between "workspaces".

Thus, we must preserve the term "workspace". This feature has been proposed by Hashicorp to allow dealing with environments (dev, testbed, preprod, prod) easily : identical structure, different instances.

We must also preserve the term "environment" for the same reason.

The idea of the "scope" term and concept is to allow multiple Terraform state (with different structures, meaning that "workspaces" won't be sufficient to deal with it) files in a single gitlab-defined (and potentially management-defined) "project".

### Length of names and labels

Beware that, depending on the chosen cloud provider, many names have constraints on allowed length and possible characters : you must make intensive use of `replace` and `substr` Terraform function to ensure the use of characters ('_' and other special characters often not allowed in names) and the length of the string (names length often limited to 64 characters, or even less).

### Map vs list

Terraform cannot update lists smartly : if you want to create a new resource in the beginning or the middle of a list, Terraform will DESTROY all elements of the list whose index must change.

So as much as possible use MAPS to create groups of resources !

### Looping on modules

Since Terraform v0.13, it is possible to loop on a module, take this into account for creating groups of resources

### Interoperability between cloud providers

The structures of the scopes and the modules aim at staying as much provider-agnostic as possible.

It means :

- keep module names GENERIC (use a functional name, like "kubernetes cluster", "functions as a service", "key-value database", etc) instead of cloud-specific name ("EC2", "Azure SQL Server", "BigQuery"). Ideally, a module created for a provider should have an equivalent for other providers.
- ensure that the `variables.tf` file stay CONSISTENT between all versions of a module between all providers

### Readability and simplicity of the architecture

The architecture of a scope is essentially defined in the `terraform.tfvars` and `services/*.tfvars` files. 

+ They are meant to not be provider-dependant. Ideally the same architecture files should be valid among any cloud provider.
+ They are meant to be simple and high-level. All remapping and restructuring of the variables needed to be pushed into Terraform modules are done in `main.tf`. That is the reason of existence of this file.
