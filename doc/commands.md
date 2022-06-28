# CLI documentation

- [CLI documentation](#cli-documentation)
	- [Create CloudTiger project](#create-cloudtiger-project)
	- [Typical use](#typical-use)
	- [CLI commands](#cli-commands)
		- [options](#options)
			- [Custom gitops folder](#custom-gitops-folder)
			- [Custom library path](#custom-library-path)
			- [Custom output file](#custom-output-file)
			- [Custom error file](#custom-error-file)
		- [Initialization](#initialization)
		- [Terraform](#terraform)
		- [Ansible](#ansible)
		- [API services](#api-services)

## Create CloudTiger project

If you do not have a project folder yet, you can create one with the command :

```bash
cloudtiger <PATH_TO_PROJECT_ROOT> init F
```

Once you have configured the project folder following [these instructions](project_configuration.md), you can proceed with CloudTiger commands.

You can always display the `cloudtiger` helper even if your current working directory is not a CloudTiger project folder.

```bash
cloudtiger # This command will dump the helper
cloudtiger --help # This command too
```

## Typical use

```bash
cloudtiger [global options] <SCOPE> <COMMAND> <SUBCOMMAND> [command options]
```

Notice : CloudTiger commands can work either with `config/<SCOPE>` or `<SCOPE>` as their first argument. Assuming that your working directory is a well-configured CloudTiger project, you have a `config` folder inside it, thus __autocompletion will work with `config/<SCOPE>`__

GOOD PRACTICE 2 : before answering 'yes' to ANY terraform operation, please check the 'Plan' line of the operation, to see which resources will be altered.

## CLI commands

### options

You can set the following options with Cloud Tiger :

#### Custom gitops folder

By default, the `gitops` folder is the current working directory. You can set another one like this :

```bash
cloudtiger --project-root=<PATH_TO_GITOPS_FOLDER> <SCOPE> <COMMAND> <SUBCOMMAND>
```

Notice that in this case, autocompletion for SCOPE path will not work.

#### Custom library path

By default, Cloud Tiger use an internal "library" to obtain Terraform modules, Ansible playbooks, Jinja configuration templates, etc. The internal library is stored in `cloud_tiger/libraries` in the source code of the CLI.

You can set your own "library" path like this :

```bash
cloudtiger --libraries-path=<PATH_TO_LIBRARIES_FOLDER> <SCOPE> <COMMAND> <SUBCOMMAND>
```

#### Custom output file

By default, Cloud Tiger use the standard output for all Terraform and Ansible commands.

You can set a specific file for dumping outputs like this :

```bash
cloudtiger --output-file=<PATH_TO_OUTPUT_FILE> <SCOPE> <COMMAND> <SUBCOMMAND>
```

#### Custom error file

By default, Cloud Tiger use the standard error for all Terraform and Ansible commands errors.

You can set a specific file for dumping errors like this :

```bash
cloudtiger --error-file=<PATH_TO_ERROR_FILE> <SCOPE> <COMMAND> <SUBCOMMAND>
```

### Initialization

Create a bootstrap CloudTiger root project :

```bash
cloudtiger <PATH_TO_YOUR_ROOT_PROJECT> init folder
```

Setup the CloudTiger project configuration (will have many prompts) :

```bash
cloudtiger <PATH_TO_YOUR_ROOT_PROJECT> init config
```

Check if an SSH key pair is available :

```bash
cloudtiger <SCOPE> init 0
```

Collect IPs for VMs and store them into a file `config/scopes/<SCOPE>/config_ips.yml` :

```bash
cloudtiger <SCOPE> init 1
```

Copy Terraform modules needed by your scope into `terraform` folder, and create a scope folder in `scopes/<SCOPE>/terraform`, based on templates in `cloudtiger/libraries/internal/terraform_providers` and .j2 files in `config/generic_terraform` :

```bash
cloudtiger <SCOPE> init 2
```

### Terraform

Run `terraform init ...` in `scopes/<SCOPE>/terraform` folder :

```bash
cloudtiger <SCOPE> tf 1
```

same with `terraform apply ...`, combined with `terraform output` to `scopes/<SCOPE>/inventory/terraform_output.json`:

```bash
cloudtiger <SCOPE> tf 2
```

You can also run `terraform plan`, `terraform refresh` and `terraform destroy` with :

```bash
cloudtiger <SCOPE> tf plan
cloudtiger <SCOPE> tf refresh
cloudtiger <SCOPE> tf destroy
```

Remove all VMs from your current tfstate, then try to import all VMs listed into the `config.yml` into the tfstate :

```bash
cloudtiger <SCOPE> tf import
```

WARNING : this command only works for Nutanix and vSphere for the moment, still experimental for AWS, Azure and GCP

### Ansible

Prepare Ansible inventory (`ssf.cfg`. `hosts.yml`) from `config.yml` and Terraform output :

```bash
cloudtiger <SCOPE> ans 1
```

Merge Ansible requirement files from `cloudtiger/libraries/ansible/requirements.yml` and `<PROJECT_ROOT>/standard/ansible_requirements.yml` into `<PROJECT_ROOT>/ansible/requirements.yml`, then run `ansible install -r ansible/requirements.yml` :

```bash
cloudtiger <SCOPE> ans D
```

Hint : Ansible by default will not try to upgrade roles already installed. You can force reinstallation (of all roles, warning !) with this option :

```bash
cloudtiger <SCOPE> ans D -F
```

Copy Ansible playbooks from `cloudtiger/libraries/ansible/playbooks` to `<PROJECT_ROOT>/ansible/playbooks`

```bash
cloudtiger <SCOPE> ans P
```

Prepare Ansible meta-playbook `execute_ansible.yml` :

```bash
cloudtiger <SCOPE> ans 2
```

Check SSH connexion to VMs (not mandatory for executing Ansible) :

```bash
cloudtiger <SCOPE> ans H
```

Once it is done, you can run Ansible meta-playbook `execute_ansible.yml` :

```bash
cloudtiger <SCOPE> ans 3
```

WARNING : if you are trying to connect to newly created VMs with Ansible, you will have a warning that the fingerprint of the machine is unknown (or has changed, if you have changed the remote host), and will have a prompt to validate or reject the fingerprint.
To avoid having to validate manually many fingerprint, you can add the option '--no-check/-n' :

```bash
cloudtiger <SCOPE> ans 3 -n
```

### API services

You can use CloudTiger to configure services providing an API with a Terraform connector supported by CloudTiger.

To this purpose, first check that you have defined the credentials for the target service in `secrets/<SERVICE_NAME>/<service_host>.env`

Currently supported services are :

- `gitlab`
- `nexus`

To create a service folder in `scopes/<SCOPE>/<SERVICE_NAME>` :

```bash
cloudtiger <SCOPE> service <SERVICE_NAME> 0
```

To run `terraform init/apply/plan/destroy` in the folder `scopes/<SCOPE>/<SERVICE_NAME>` :

```bash
cloudtiger <SCOPE> service <SERVICE_NAME> init
cloudtiger <SCOPE> service <SERVICE_NAME> plan
cloudtiger <SCOPE> service <SERVICE_NAME> apply
cloudtiger <SCOPE> service <SERVICE_NAME> destroy
```
