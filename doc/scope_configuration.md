# Scope configuration

- [Scope configuration](#scope-configuration)
	- [Global parameters](#global-parameters)
	- [Backend parameters](#backend-parameters)
	- [Network parameters](#network-parameters)
	- [VM parameters](#vm-parameters)
	- [Ansible parameters](#ansible-parameters)
		- [Role](#role)
		- [Playbook](#playbook)
		- [Command](#command)
	- [Next step](#next-step)

In this document, we describe how to define a scope configuration file.

As explained in the "project configuration" documentation, CloudTiger groups infrastructures as "scopes", which are just groups of VMs and infrastructure resources (VLANs, PaaS, SaaS)

A scope is defined as a folder path stored in the `config` folder of your project root, containing a file named `config.yml`.

The `config.yml` file is a YAML file, that should contains the following values :

## Global parameters

- `provider` : set the value to a supported provider. Check available values [here](config_options.md)
- `region` : only for AWS, Azure, GCP. Define the datacenter region where the resources will be deployed. Check available values [here](config_options.md)
- `ssh_key_name` : Optional. Set the value to the name (without directory) of the private SSH key you will use to connect to the VMs. If the key is not provided, CloudTiger will look for a private key using the environment variable `CLOUDTIGER_PRIVATE_SSH_KEY_PATH` defined in the `.env` file in the project root.
- `use_tf_backend` : optional. Set to True if you want Terraform to use a backend. Default is False

## Backend parameters

If you set `use_tf_backend` to True, you will have to add extra parameters to your provider's secret file. Edit the file `secrets/<PROVIDER>/.env` to add the following lines :

```bash
export CLOUDTIGER_BACKEND_USERNAME=...
export CLOUDTIGER_BACKEND_PASSWORD=...
export CLOUDTIGER_BACKEND_ADDRESS=...
export CLOUDTIGER_BACKEND_DB=...
```

Be sure to set correct values for each variables. The backend will be invoked when calling `tf init`.

## Network parameters

- `network`: this key defines the networks and subnetworks for the current scope. Follow this format :

```yaml
network:
  <NETWORK_NAME>:
    network_cidr: ...
    datacenter: datacenter
    subnets:
      <SUBNET_NAME>:
        availability_zone: ...
        cidr_block: ...
        gateway_ip_address: ...
        nameservers:
        - ...
        network_interface: ...
        unmanaged: true
        managed_ips: true
        vlan_id: ...
```

- <NETWORK_NAME> : should be the name of a VPC (AWS and GCP) or a Virtual Network (Azure). For Nutanix and vSphere, the value is not used, you can choose whatever value you want. You can have as many networks that you want.
- `network_cidr` : only for AWS, GCP, Azure. CIDR block for the network. Format should be `192.168.0.1/32`
- `prefix` : Optional. a prefix that will be added to the name of the network in the provider. By default an empty string.
- <SUBNET_NAME> : should be the name of the subnet (AWS, GCP, Azure) or VLAN (Nutanix, vSphere). You can have as many networks that you want.
- `datacenter` : only for vSphere. Name of the datacenter hosting the network.
- `cidr_block` : CIDR block for the subnetwork. Format should be `192.168.0.1/32`
- `gateway_ip_address` : only for vSphere and Nutanix. The IP address of the subnet's gateway.
- `nameservers` : only for vSphere and Nutanix. Optional. The list of the IPs of DNS resolvers used by the subnet
- `network_interface` : only for vSphere and Nutanix. The name of the network interface used by VMs connected to this subnet
- `unmanaged` : optional. Default False. Set to True if the subnet is created and managed outside of the current scope (common case for Nutanix and vSphere).
- `managed_ips` : optional. Default False. Set to True if you want the provider to automatically assign an IP to created VMs, without having to provide specific IPs.
- `vlan_id` : only for vSphere and Nutanix. The ID of the subnet.

## VM parameters

- `vm` : this key defines the VMs for the current scope. Follow this format :

```yaml
vm:
  <NETWORK_NAME>:
    <SUBNET_NAME>:
      <VM_NAME>:
        group: ...
        type: ...
        prefix: ...
        availability_zone: ...
        system_image: ...
        subnet_type: ...
        private_ip: ...
        root_volume_type: ...
        volumes:
          data:
            index: 1
        ingress_rules: ["...","..."]
        ingress_cidr:
          ssh: ["0.0.0.0/0"]
        egress_rules: ["default"]
        instance_profile: "default"
```

- <NETWORK_NAME> : the network where the VM will be deployed. Should match a network defined in the `network` key.
- <SUBNET_NAME> : the subnet where the VM will be deployed. Should match a subnet defined in the `network["<NETWORK_NAME>"]` key.
- `group` : Optional. a comma-separated list of tags that will be applied to the VM. These tags will be included in the Terraform output. Used by Ansible to target hosts. Default is "ungrouped".
- `type` : Optional. Can be set to attribute a predefined `type` to the VM, that will provide default memory, CPU numbers and disk size. Check available values [here](config_options.md)
- `prefix` : Optional. a prefix that will be added to the name of the network in the provider. By default an empty string.
- `availability_zone` : For AWS, GCP, Azure, it defines the availability zone where to deploy the machine. It must be an availability zone well defined for the chosen `region`. Check available values [here](config_options.md)
- `system_image` : an OS image for the VM. Check available values [here](config_options.md).
- `subnet_type` : optional. Default "private". Set to "public" if this VM needs to be publicly available.
- `private_ip` : optional. If provided, will be the IP of the VM (WARNING : you need to ensure the IP is available and belongs to the subnet of the VM). If not provided, CloudTiger will try to find an available IP from the VM's subnet.
- `size` : main physical specifications of the VM. Check below for detailed description.
- `volumes` : optional. Allow to set the size, type and numbers of the VM's physical volumes. Check below for detailed description.
- `root_volume_type` : optional. Can be set to attribute a predefined `type` to the root volume, that will provide default type and size. Check available values [here](config_options.md). WARNING : if `root` is not defined in the `volumes` key, either `root_volume_type` or `type` must be provided.
- `data_volume_type`: optional. Can be set to attribute a predefined `type` to the first "data" volume, that will provide default type and size. Check available values [here](config_options.md). WARNING : if `data` is not defined in the `volumes` key, either `data_volume_type` or `type` must be provided.
- `ingress_rules` : only for AWS, GCP, Azure. A list of ingress security rules from a set of predefined rules. Check available values [here](config_options.md)
- `ingress_cidr` : only for AWS, GCP, Azure. A list of allowed ingress CIDRs per ingress rule.
- `egress_rules` : only for AWS, GCP, Azure. A list of egress security rules from a set of predefined rules. Check available values [here](config_options.md)
- `instance_profile` : optional. only for AWS, GCP, Azure. An IAM profile to attribute to the VM, from the list of profiles defined in the `profile` key of the `config.yml`.

Description of the `size` key :

```yaml
        size:
          memory: ...
          nb_sockets: ...
          nb_vcpu_per_socket: ...
```

- `memory` : RAM of the VM in gigabytes
- `nb_sockets` : optional. Number of vCPUs sockets. Default 1.
- `nb_vcpu_per_socket` : Number of vCPUs per socket.

Description of the `volumes` key :

```yaml
        volumes:
          <VOLUME_NAME>:
            datastore: ...
            index: 1
            eagerly_scrub: ...
            name: ...
            size: ...
            thin_provisioned: ...
            vmdk_path: ...
```

- <VOLUME_NAME> : name of the volume as it will appear in the Terraform state. If `root` is not in the list of volumes, parameters for the root volume will be infered either from the `type` of the VM, of from `root_volume_type`. Same for `data`.
- `index`: number of the volume. `root` is '0' by default. Has an impact on the device name in the machine (On Unix, volume devices will typically be labelled /dev/sda for volume 0, /dev/sdb for volume 1, etc)
- `name` : name of the volume in the provider. Should be `Hard disk X` for vSphere, starting at `Hard Disk 1` for the root volume.
- `size` : size of the volume in Gigabytes
- `datastore` : only for vSphere. ID of the datastore
- `thin_provisioned` : only for vSphere. Set to true will have the volume NOT pre-allocated in terms of size on the vSphere disk.
- `vmdk_path` : only for vSphere. Path of the associated vmdk file on the vSphere disk.
- `eagerly_scrub` : only for vSphere.

## Ansible parameters

The `ansible` key of the `config.yml` allows to define a list of Ansible actions to apply on the created VMs. The syntax is the following one :

```yaml
ansible:
- name: ...
  type: role
  hosts: ...
  roles:
  - source: ...
    params:
      become: true
      ...
- name: ...
  type: playbook
  params:
    become: true
    ...
    hosts: ...
  source: ...
- name: ...
  type: command
  hosts: ...
  commands:
  - source: ...
    name: ...
    params:
      become: true
      ...
```

Once you have defined this key, CloudTiger convert it into an aggregated playbook located in `<PROJECT_ROOT>/scopes/<SCOPE>/inventory/execute_ansible.yml` by running the command :

`cloudtiger config/<SCOPE> ans 2`

The `ansible` key should be a list. Each element of the list is an Ansible action, that could be :

- an Ansible role
- an Ansible playbook
- a Shell command

### Role

```yaml
ansible:
- name: ...
  type: role
  hosts: ...
  roles:
  - source: ...
    params:
      become: true
      ...
```

- `name` : name of the action that will be displayed by Ansible at run
- `type` : should be "role"
- `hosts` : target hosts. Can be `all` for all VMs of the scope, or a "group", or a subnet, or a VM name.
- `roles` : a list of roles called for this action
- `source` : the source of the role. Should be a role defined in `<PROJECT_ROOT>/ansible/requirements.yml`
- `params` : the parameters for the role, plus the extra parameter `become` : `true` if you need privilege escalation for the role

### Playbook

```yaml
ansible:
- name: ...
  type: playbook
  params:
    become: true
    ...
    hosts: ...
  source: ...
```

- `name` : name of the action that will be displayed by Ansible at run
- `type` : should be "playbook"
- `hosts` : target hosts. Can be `all` for all VMs of the scope, or a "group", or a subnet, or a VM name.
- `source` : the source of the playbook. Should be a playbook defined in `<PROJECT_ROOT>/ansible/playbooks`
- `params` : the parameters for the playbook, plus the extra parameter `become` : `true` if you need privilege escalation for the playbook

### Command

```yaml
ansible:
- name: ...
  type: command
  hosts: ...
  commands:
  - source: ...
    name: ...
    params:
      become: true
```

- `name` : name of the action that will be displayed by Ansible at run
- `type` : should be "command"
- `hosts` : target hosts. Can be `all` for all VMs of the scope, or a "group", or a subnet, or a VM name.
- `source` : the Shell command to execute
- `params` : the extra parameter `become` : `true` if you need privilege escalation for the playbook

## Next step

Once everything is well defined, you can proceed to [CloudTiger commands](commands.md)