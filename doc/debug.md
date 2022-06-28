# Debug

- [Debug](#debug)
	- [CLI logs](#cli-logs)
	- [Manual SSH access](#manual-ssh-access)
	- [Debugging a Terraform module/provider](#debugging-a-terraform-moduleprovider)
	- [Debugging an Ansible playbook/role](#debugging-an-ansible-playbookrole)
	- [tf init](#tf-init)

Various tips for development and debugging

## CLI logs

Cloud Tiger dumps its logs in a file called `cloudtiger.log` located in the "gitops" folder (current folder or specified gitops folder)

## Manual SSH access

Create a ssh-agent :

```bash
eval `ssh-agent -s`
```

Add a private SSH key to the agent :

```bash
ssh-add <PATH_TO_SSH_KEY>
```

Connect to a remote machine with an SSH key from the agent while forwaring the private SSH key in RAM in the SSH session on the remote machine (thus allowing jumping to another machine with the same key without needing to write the private key on the first remote machine) :

```bash
ssh -A <USER>@<ADDRESS>
```

## Debugging a Terraform module/provider

If you have installed the package in debug mode, like this :

```bash
pip3 install -e .
```

follow the quickstart, then once you have reached this command :

```bash
cloudtiger <SCOPE> tf apply
```

you can edit the Terraform files (in `cloud_tiger/libraries/terraform/<PROVIDER>...` for the modules,, and in `cloud_tiger/libraries/terraform/templates/public_cloud/...` or in `cloud_tiger/libraries/terraform/templates/vm_vsphere_generic/...`), then you can reload the modification in the `gitops` folder with this command 

```bash
cloudtiger <SCOPE> init 2
```

and test Terrafom again with 

```bash
cloudtiger <SCOPE> tf apply
```

## Debugging an Ansible playbook/role

If you have installed the package in debug mode, like this :

```bash
pip3 install -e .
```

follow the quickstart, then once you have reached this command :

```bash
cloudtiger <SCOPE> ans 3
```

you can edit the playbook involved in `cloud_tiger/libraries/ansible/playbooks`, then you can reload the modification in the `gitops` folder with this command : 

```bash
cloudtiger <SCOPE> ans 2
```

TODO : cloud docker + relative path

## tf init

Ensure that you have a Terraform version >= 1.0