
locals {

  main_disk = data.vsphere_virtual_machine.packer_template.disks.0

  cdrom_backed = [{ "Backing" : {} }]

  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }
}

data "vsphere_virtual_machine" "packer_template" {
  name          = var.vm.system_image
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_datacenter" "datacenter" {
  name = var.vm.datacenter
}

data "vsphere_network" "network" {

  name          = var.vm.subnet_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_virtual_machine" "vm_info" {
  count         = (var.vm.imported == "true") ? 1 : 0
  name          = var.vm.vm_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

resource "vsphere_virtual_machine" "virtual_machine" {

  ### added to avoid messing with cdrom reader or very specific settings on imported machines
  lifecycle {
    ignore_changes = [
      cdrom,
      tools_upgrade_policy,
      annotation,
      disk.0.eagerly_scrub,
      disk.0.thin_provisioned,
      disk.0.size
    ]
  }

  name     = var.vm.vm_name
  num_cpus = var.vm.instance_type.nb_vcpu_per_socket
  memory   = var.vm.instance_type.memory
  folder   = lookup(var.vm.extra_parameters, "folder", "unset_folder")

  scsi_type                  = lookup(var.vm.extra_parameters, "scsi_type", "pvscsi")
  resource_pool_id           = var.vm.extra_parameters["resource_pool_id"]
  guest_id                   = var.vm.extra_parameters["guest_id"]
  wait_for_guest_net_timeout = lookup(var.vm.extra_parameters, "wait_for_guest_net_timeout", 5)

  storage_policy_id    = lookup(var.vm.extra_parameters, "storage_policy_id", null)
  alternate_guest_name = lookup(var.vm.extra_parameters, "alternate_guest_name", null)
  annotation           = lookup(var.vm.extra_parameters, "annotation", null)

  datastore_id = lookup(var.vm.extra_parameters, "datastore", lookup(var.vm.root_volume, "datastore", null))

  dynamic "clone" {
    for_each = ((var.vm.system_image == null) || (var.vm.imported)) ? [] : [1]
    content {
      template_uuid   = data.vsphere_virtual_machine.packer_template.id
      linked_clone    = false
      ovf_network_map = {}
      ovf_storage_map = {}
    }
  }

  custom_attributes = lookup(var.vm.extra_parameters, "custom_attributes", null)

  enable_disk_uuid = tobool(lower(lookup(var.vm.extra_parameters, "enable_disk_uuid", "true")))
  disk {
    label             = "disk0"
    size              = max(lookup(var.vm.root_volume, "size", var.vm.default_root_volume_size), local.main_disk.size)
    eagerly_scrub     = lookup(local.main_disk, "eagerly_scrub", true)
    thin_provisioned  = lookup(local.main_disk, "thin_provisioned", false)
    keep_on_remove    = true
    storage_policy_id = lookup(local.main_disk, "storage_policy_id", null)
  }

  dynamic "disk" {
    for_each = local.non_empty_data_volumes
    content {
      label             = lookup(disk.value, "disk_label", format("disk%s", disk.value.index))
      size              = lookup(disk.value, "size", var.vm.default_data_volume_size)
      unit_number       = disk.value.index
      datastore_id      = disk.value.datastore
      eagerly_scrub     = lookup(disk.value, "eagerly_scrub", false)
      thin_provisioned  = lookup(disk.value, "thin_provisioned", true)
      disk_sharing      = lookup(disk.value, "disk_sharing", "sharingNone")
      keep_on_remove    = true
      storage_policy_id = lookup(disk.value, "storage_policy_id", null)

    }
  }

  dynamic "network_interface" {
    for_each = (var.vm.imported == "false") ? [1] : []
    content {
      network_id = data.vsphere_network.network.id
    }
  }

  dynamic "network_interface" {
    for_each = (var.vm.imported == "true") ? data.vsphere_virtual_machine.vm_info[0].network_interfaces : []
    content {
      # network_id = (length(regexall("[a-z]+", "dvportgroup")) > 0) ? element(lookup(var.vm.extra_parameters, "multiple_network_interface", ["dvportgroup-125"]),network_interface.key) : network_interface.value.id
      network_id     = network_interface.value.network_id
      adapter_type   = data.vsphere_virtual_machine.vm_info[0].network_interface_types[network_interface.key]
      use_static_mac = (lookup(var.vm.extra_parameters, "mac_address", "auto") != "auto") ? true : null
      mac_address    = (lookup(var.vm.extra_parameters, "mac_address", "auto") != "auto") ? network_interface.value.mac_address : null
    }
  }

  dynamic "vapp" {
    for_each = tobool(lookup(var.vm.extra_parameters, "no_vapp", "false")) ? [] : [1]
    content {
      properties = {
        "IP_address"    = lookup(var.vm.extra_parameters, "IP_address", lookup(var.vm, "private_ip", "unset_ip_address"))
        "Netmask"       = lookup(var.vm.extra_parameters, "Netmask", cidrnetmask(var.network[var.vm.network_name]["subnets"][var.vm.subnet_name].cidr_block))
        "Gateway"       = lookup(var.vm.extra_parameters, "Gateway", var.network[var.vm.network_name]["subnets"][var.vm.subnet_name].gateway_ip_address)
        "Name_servers"  = lookup(var.vm.extra_parameters, "Name_servers", join(",", var.network[var.vm.network_name]["subnets"][var.vm.subnet_name].nameservers))
        "DNS_suffix"    = lookup(var.vm.extra_parameters, "DNS_suffix", null)
        "Host_FQDN"     = lookup(var.vm.extra_parameters, "Host_FQDN", var.vm.vm_name)
        "Network_iface" = lookup(var.vm.extra_parameters, "Network_iface", var.network[var.vm.network_name]["subnets"][var.vm.subnet_name].network_interface)
      }
    }
  }

  cpu_hot_add_enabled    = tobool(lookup(var.vm.extra_parameters, "cpu_hot_add_enabled", false))
  cpu_reservation        = tonumber(replace(lookup(var.vm.extra_parameters, "cpu_reservation", "None"), "None", "0"))
  enable_logging         = tobool(replace(lookup(var.vm.extra_parameters, "enable_logging", "None"), "None", "false"))
  memory_hot_add_enabled = tobool(lookup(var.vm.extra_parameters, "memory_hot_add_enabled", false))
  memory_reservation     = tonumber(replace(lookup(var.vm.extra_parameters, "memory_reservation", 0), "None", "0"))
  sata_controller_count  = tonumber(lookup(var.vm.extra_parameters, "sata_controller_count", 0))
  num_cores_per_socket   = lookup(var.vm.extra_parameters, "num_cores_per_socket", 1)
  cpu_limit              = lookup(var.vm.extra_parameters, "cpu_limit", -1)
  memory_share_level     = lookup(var.vm.extra_parameters, "memory_share_level", "normal")
  memory_limit           = lookup(var.vm.extra_parameters, "memory_limit", -1)
  cpu_share_level        = lookup(var.vm.extra_parameters, "cpu_share_level", "normal")
  sync_time_with_host    = tobool(replace(lookup(var.vm.extra_parameters, "sync_time_with_host", "None"), "None", "false"))
  tools_upgrade_policy   = lookup(var.vm.extra_parameters, "tools_upgrade_policy", "manual")

  dynamic "cdrom" {
    for_each = length(lookup(var.vm.extra_parameters, "cdrom_unbacked", [])) > 0 ? [1] : []
    content {
      client_device = true
    }
  }

  dynamic "cdrom" {
    for_each = contains(keys(local.cdrom_backed[0]["Backing"]), "Datastore") ? [1] : []
    content {
      datastore_id = var.vm.extra_parameters.cdrom_backed[0]["Backing"]["Datastore"]["Value"]
      path         = split(" ", var.vm.extra_parameters.cdrom_backed[0]["Backing"]["FileName"])[1]
    }
  }

  dynamic "cdrom" {
    for_each = contains(keys(local.cdrom_backed[0]["Backing"]), "DeviceName") ? [1] : []
    content {
      client_device  = false
      device_address = "ide:1:0"
      key            = var.vm.extra_parameters["cdrom_backed"][0]["Key"]
    }
  }

}
