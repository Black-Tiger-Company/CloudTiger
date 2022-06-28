# Cloud Tiger without admin rights on windows

This document explains how to install the various tools needed by Cloud Tiger on Windows without admin rights

## Installing tools on Windows

If running the project on a Windows machine without admin rights, you will need :

- Cygwin (as a Linux shell)
- Ansible for Windows
- Terraform for Windows

## Install Cygwin

Go to https://www.cygwin.com/install.html and download setup-x86_64.exe 

To install :

```bash
./setup-x86_64.exe --no-admin
```

Select ‘Install from Internet’

Choose root directory (default)

Choose package directory to store installation files

Use System Proxy Settings

Select any mirror site to download

In ‘Select Packages’ :

- Select Category dropdown and search for lynx
- Go to All -> Web -> lynx: A text-based Web Browser
- Select latest version
- Click next to complete installation

## Configure Cygwin

### Install apt-cyg

This is a package manager for cygwin

To install:

```bash
lynx -source rawgit.com/transcode-open/apt-cyg/master/apt-cyg > apt-cyg
install apt-cyg /bin
```

## Install Ansible dependencies

Install dependencies
```bash
apt-cyg install binutils curl gcc-core gmp libffi-devel libgmp-devel make python python-crypto python-openssl python-setuptools python-devel git nano openssh openssl openssl-devel python3 python3-devel python3-pip libpq-devel
```

Install Ansible

```bash
pip3 install ansible
```

## Install Terraform

Download Terraform for windows 64 bits [here](https://www.terraform.io/downloads.html)

Copy paste the terraform.exe file in your <CYGWIN_ROOT>/bin folder

## Install project dependencies

Install project dependencies using pip

```bash
pip3 install -r requirements.txt
```