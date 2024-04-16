terraform {
  required_providers {
    nutanix = {
      source  = "nutanix/nutanix"
      version = "1.2.0"
    }
  }
}

data "nutanix_clusters" "clusters" {}

locals {
  cluster_map = { for cluster in data.nutanix_clusters.clusters.entities :
    cluster.name => cluster
  }

  cloud_init_templates = {
    "debian-10-genericcloud-amd64.qcow2"     = "cloudinit_debian.cfg.tpl"
    "debian-11-genericcloud-amd64.qcow2"     = "cloudinit_debian_11.cfg.tpl"
    "debian-test-user-data-packer-image-11"  = "cloudinit_debian_11.cfg.tpl"
    "ubuntu-20.04-server-cloudimg-amd64.img" = "cloudinit_ubuntu.cfg.tpl"
    "ubuntu-22.04-server-cloudimg-amd64.img" = "cloudinit_ubuntu.cfg.tpl"
    "ubuntu-2204-lts-server-bt-ad-template-nutanix" = "cloudinit_ubuntu2204.cfg.tpl"
  }

  subnet_has_managed_ips = lookup(var.network[var.vm.network_name]["subnets"][var.vm.subnet_name], "managed_ips", false)

  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }

}

data "nutanix_subnet" "subnets" {
  subnet_name = var.vm.subnet_name
}


resource "nutanix_virtual_machine" "virtual_machine" {

  # name = format("%s_%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name)
  name         = var.vm.vm_name
  cluster_uuid = local.cluster_map[var.vm.availability_zone].metadata.uuid

  lifecycle {
    ignore_changes = [
      guest_customization_cloud_init_user_data,
      owner_reference,
      project_reference,
      disk_list[0].data_source_reference,
      parent_reference
    ]
  }

  guest_customization_cloud_init_user_data = (lookup(var.vm.extra_parameters, "cloud_init_set", false) == true) ? null : base64encode(templatefile(format("%s/%s", path.module, local.cloud_init_templates[var.vm.system_image]),
    {
      vm_name    = var.vm.vm_name
      ad_groups   = lookup(var.vm, "ad_groups", [])
      user       = lookup(var.vm, "user", "unset_user")
      vm_address = lookup(var.vm, "private_ip", "learned")
      vm_gateway  = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["gateway_ip_address"]
      netmask     = split("/", var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["cidr_block"])[1]
      nameservers = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["nameservers"]
      search      = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["search"]
      password   = var.vm.default_password
      domain_ldap = var.vm.domain_ldap
      uppercase_domain_ldap = upper(var.vm.domain_ldap)
      ou_ldap = var.vm.ou_ldap
      user_ldap_join = var.vm.user_ldap_join
      password_user_ldap_join = var.vm.password_user_ldap_join
      ldap_user_search_base = var.vm.ldap_user_search_base
      ldap_sudo_search_base = var.vm.ldap_sudo_search_base
      users_list = var.vm.users_list
    }
  ))

  ### IP assignment
  # If the VLAN has IP management (var.vm.extra_parameters["managed_ip"] is True) : 
  # - we use an assigned dynamic nic with the provided IP (the IP has potentially been provided by cloudtiger init 1)
  # If the VLAN has NO IP management :
  # - if the private IP is provided (!= "not_learned_yet") : we do not use a dynamic nic, the address is set using cloudinit
  # - if the private IP is not provided (== "not_learned_yet") : we use a dynamic nic of type "LEARNED"

  dynamic "nic_list" {
    for_each = (local.subnet_has_managed_ips) ? [1] : []
    content {
      subnet_uuid = data.nutanix_subnet.subnets.metadata.uuid
      ip_endpoint_list {
        type = "ASSIGNED"
        ip   = var.vm.private_ip
      }
      nic_type = "NORMAL_NIC"
    }
  }

  dynamic "nic_list" {
    for_each = local.subnet_has_managed_ips ? [] : [1]
    content {
      subnet_uuid = data.nutanix_subnet.subnets.metadata.uuid
    }
  }


  num_vcpus_per_socket = var.vm.instance_type.nb_vcpu_per_socket
  num_sockets          = var.vm.instance_type.nb_sockets
  memory_size_mib      = var.vm.instance_type.memory

  parent_reference = {
    kind = "vm"
    # name = var.vm.system_image
    # uuid = "399221a1-09b8-47af-a7a4-3a3ae647d432"
    # uuid = var.vm.system_image
    uuid = var.vm.extra_parameters.source_image_uuid
  }


  disk_list {
    data_source_reference = {
      kind = "vm"
      uuid = var.vm.extra_parameters.source_image_uuid
    }
  }

  dynamic "disk_list" {
    for_each = local.non_empty_data_volumes
    content {
      disk_size_mib = lookup(disk_list.value, "size", var.vm.default_data_volume_size) * 1024
      device_properties {
        device_type = "DISK"
        disk_address = {
          "adapter_type" = "SCSI"
          "device_index" = disk_list.value.index
        }
      }
    }
  }

}

### this data field allows to grab the IP set for the machine in "LEARNED" network configuration
data "nutanix_virtual_machine" "virtual_machine_data" {
  vm_id = nutanix_virtual_machine.virtual_machine.id
}