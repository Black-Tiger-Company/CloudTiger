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
    "debian-11-genericcloud-amd64.qcow2"     = "cloudinit_debian.cfg.tpl"
    "ubuntu-20.04-server-cloudimg-amd64.img" = "cloudinit_ubuntu.cfg.tpl"
    "ubuntu-22.04-server-cloudimg-amd64.img" = "cloudinit_ubuntu.cfg.tpl"
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

data "nutanix_image" "image" {
  image_name = var.vm.system_image
}

resource "nutanix_virtual_machine" "virtual_machine" {

  # name = format("%s_%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name)
  name         = var.vm.vm_name
  cluster_uuid = local.cluster_map[var.vm.availability_zone].metadata.uuid

  lifecycle {
    ignore_changes = [
      guest_customization_cloud_init_user_data,
      nic_list,
      owner_reference,
      project_reference,
      disk_list
      # disk_list[1].data_source_reference.uuid
    ]
  }

  guest_customization_cloud_init_user_data = (lookup(var.vm.extra_parameters, "cloud_init_set", false) == true) ? null : base64encode(templatefile(format("%s/%s", path.module, local.cloud_init_templates[var.vm.system_image]),
    {
      # vm_address = nutanix_virtual_machine.virtual_machine.nic_list[0].ip_endpoint_list[0].ip
      vm_address = lookup(var.vm, "private_ip", "learned")
      # vm_address = !lookup(var.vm.extra_parameters, "post_assigned", true) ? "vm_address" : var.vm.private_ip
      vm_gateway  = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["gateway_ip_address"]
      netmask     = cidrnetmask(var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["cidr_block"])
      nameservers = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["nameservers"]
      search      = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["search"]
      interface   = lookup(var.network[var.vm.network_name]["subnets"][var.vm.subnet_name], "network_interface")
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
    for_each = (!(local.subnet_has_managed_ips)) ? [1] : []
    content {
      subnet_uuid = data.nutanix_subnet.subnets.metadata.uuid
      ip_endpoint_list {
        type = "LEARNED"
        ip   = lookup(var.vm.extra_parameters, "assigned_ip", "192.168.0.0")
      }
      nic_type = "NORMAL_NIC"
    }
  }

  num_vcpus_per_socket = var.vm.instance_type.nb_vcpu_per_socket
  num_sockets          = var.vm.instance_type.nb_sockets
  memory_size_mib      = var.vm.instance_type.memory

  disk_list {
    data_source_reference = {
      kind = "image"
      uuid = data.nutanix_image.image.metadata.uuid
    }
    disk_size_mib = lookup(var.vm.root_volume, "size", var.vm.default_root_volume_size) * 1024
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