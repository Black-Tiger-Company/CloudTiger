terraform {
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = ">= 0.13.0"
    }
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.42.0"
    }
  }
}


############
# Virtual Machine
############

resource "openstack_compute_instance_v2" "virtual_machine" {
  name            = format("%s%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name)
  image_name      = var.vm.system_image
  flavor_name     = var.vm.instance_type.type
  security_groups = [format("%s%s_%s_subnet_sg", var.vm.module_prefix, var.vm.network_name, var.vm.subnet_name)]

  metadata = merge(
    var.vm.module_labels,
    {
      "Name"  = format("%s%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name),
      "group" = var.vm.group
    }
  )

  network {
    name = format("%s%s_network", var.vm.module_prefix, var.vm.network_name)
    fixed_ip_v4 = var.vm.private_ip
  }

  dynamic "network" {
    for_each = (var.vm.subnet_type == "public") ? [1] : []
    content {
      name = "Ext-Net"
    }
  }

  lifecycle {
    ignore_changes = [image_id]
  }
}

############
# Data Volume
############

locals {
  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }
}

resource "openstack_blockstorage_volume_v2" "vm_data_volume" {

  for_each = local.non_empty_data_volumes

  name = format("%s%s_data_volume", var.vm.module_prefix, var.vm.vm_name)
  size = lookup(each.value, "size", var.vm.default_data_volume_size)
  # provider = openstack.ovh
}


resource "openstack_compute_volume_attach_v2" "vm_data_volume_attachment" {

  for_each = local.non_empty_data_volumes

  volume_id   = openstack_blockstorage_volume_v2.vm_data_volume[each.key].id
  instance_id = openstack_compute_instance_v2.virtual_machine.id

}
