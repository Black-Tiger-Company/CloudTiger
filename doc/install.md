# Installing CloudTiger
- [Installing CloudTiger](#installing-cloudtiger)
	- [As a Python package](#as-a-python-package)
		- [fping](#fping)
		- [Python](#python)
		- [Ansible](#ansible)
		- [Terraform](#terraform)
		- [Kubernetes and Helm](#kubernetes-and-helm)
		- [On MacOS](#on-macos)
	- [Installation from sources](#installation-from-sources)
			- [debug mode](#debug-mode)
			- [production mode](#production-mode)
	- [As a Docker](#as-a-docker)
		- [From sources](#from-sources)
		- [From Docker repository](#from-docker-repository)
		- [Run the docker](#run-the-docker)
	- [Next step](#next-step)

Currently, you can run CloudTiger either :

- as a python package built from sources
- as a Docker

## As a Python package

You will need to have :

- a Unix shell (install [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) if you are on Windows and have admin rights. If you are on Windows without admin rights, use [Cygwin](cygwin.md))
- python3 >= 3.8 + pip
- Ansible
- Terraform
- fping

Optionally, according to your use case, you may need to install :

- kubectl
- Helm

### fping

On linuses :

```bash
sudo apt install fping
```

### Python

You can find documentation for installing Terraform for your OS [here](https://learn.hashicorp.com/terraform/getting-started/install.html)

Install pip for python3 if you do not have it (commands for Ubuntu and Debian-like linux) with the following commands :

commands for Ubuntu and Debian-like linux :

```bash
sudo apt update
sudo apt install python3-pip
```

commands for MacOS :

```bash
brew update
brew install python3-pip
```

WARNING : be sure to have a Python version >= 3.8. Check it with this command :

```bash
python3 --version
```

### Ansible

[Ansible](https://www.ansible.com/) is a Configuration Management tool that allows parallelized SSH connections to remote hosts and management of various remote commands.

You can install Ansible through pip with the following commands :

```bash
pip3 install ansible
```

You can check the Ansible documentation for more [details](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) if needed.

Some Unix distribution will need you to install the `sshpass` program :

```bash
sudo apt install sshpass
```

### Terraform

[Terraform](https://www.terraform.io/) is an Infrastructure as Code tool developed by HashiCorp.

On ubuntu/debian be sure you have all dependencies :

```bash
sudo apt install curl lsb-release software-properties-common
```

Then follow the instructions for your OS [here](https://www.terraform.io/downloads)

### Kubernetes and Helm

[Kubernetes](https://kubernetes.io/) is a tool for managing high-availability containerized applications.

[Helm](https://helm.sh/) is a 'package manager' for Kubernetes.

CloudTiger does not need Kubernetes and Helm by default, but if you wish to use some of their features, for example through Ansible roles, you will probably need to install Kubernetes' client (kubectl) and helm locally on your workstation.

- check installation of kubectl [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- check installation of helm [here](https://helm.sh/docs/intro/install/)

### On MacOS

You will need to install `jmespath` in order to use Ansible correctly. You can do it with the following commands :

```bash
pip3 install jmespath
```

## Installation from sources

You will first need to download the repository of the project

```bash
git clone http://esturgeon.btgroup.io/terraform-ecosystem/cloud-tiger.git
```

Cloud Tiger runs with python 3. For debug purposes, you must enforce that the `python` executable points to Python 3. To ensure this version, you can run the following command (on Debian-like OS) :

```bash
sudo apt install python-is-python3
```

Or add this command in `~/.bashrc` or `~/.bash_aliases` :

```bash
alias python=python3
```

#### debug mode

If you want to install the package in debug mode (no admin rights needed, your local Python will use the package's source directly where you downloaded it), run the following command, which should be sufficient for executing the "Quickstart" :

```bash
pip3 install -e .
```

When installing in debug mode, you may have to edit your PATH to include the folder where the cloudtiger executable has been installed. It should be something like `/home/<YOUR_USER>/.local/bin`, and is prompted as a WARNING in the logs of the previous command.

Check the existence of the following files :

- ~/.bash_profile
- ~/profile

Choose the one that already exists, then edit it (with vi or nano or your favorite IDE)

```bash
vi ~/.bash_profile
```

Then add the following line at the end :

```bash
export PATH=$PATH:/home/<YOUR_USER>/.local/bin
```

Then reload your environment

```bash
source ~/.bash_profile
```

#### production mode

If you want to install the package to your main local Python's site-package (not recommended for debug and/or quickstart), run the following command :

```bash
make install
```

If your current Python's site-package is in a admin-owned repository, you will need to run the following command :

```bash
sudo make install
```

## As a Docker

First, you need to install Docker on your OS

Then, you can either build the docker from sources, or pull it from the official Black Tiger docker repository

### From sources

Run the following command in the root folder of the CloudTiger project

```bash
docker build -t cloudtiger .
```

### From Docker repository

Login to the Docker repository :

```bash
docker login saumon.btgroup.io
```

Pull the docker image :

```bash
docker pull cloudtiger:latest
```

### Run the docker

Once you have built and/or pulled the docker, launch it like this :

```bash
docker run -v $(pwd):/workdir -it cloudtiger bash
```

It will prompt a bash terminal inside the docker, where all cloudtiger commands are available. The `-v $(pwd):/workdir` will map you current working directory as the docker's working directory, so you can run the commands directly in the current folder at the bash prompt. Feel secure that any files that will be created or edited will keep your current ACLs (owner will not change).

## Next step

Once CloudTiger is installed, you can proceed with your [project configuration](project_configuration.md)