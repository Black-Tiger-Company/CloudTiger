
locals {

  cdrom_backed = [{ "Backing" : {} }]

  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }

  cloud_init_templates = {
    "jammy/current/jammy-server-cloudimg-amd64.ova" = "cloudinit_ubuntu2204.cfg.tpl"
  }
}

data "vsphere_datacenter" "datacenter" {
  name = var.vm.datacenter
}

data "vsphere_host" "host" {
  name          = var.vm.availability_zone
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_resource_pool" "pool" {
  name          = var.vm.extra_parameters.resource_pool
  datacenter_id = data.vsphere_datacenter.datacenter.id
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

data "vsphere_datastore" "datastore_root" {

  name          = lookup(var.vm.root_volume, "datastore", var.vm.extra_parameters.datastore)
  datacenter_id = data.vsphere_datacenter.datacenter.id

}

data "vsphere_datastore" "datastore_datadisks" {

  for_each = local.non_empty_data_volumes

  name          = lookup(each.value, "datastore", var.vm.extra_parameters.datastore)
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
  folder   = "sandbox"

  scsi_type                  = "pvscsi"
  resource_pool_id           = data.vsphere_resource_pool.pool.id
  host_system_id    = data.vsphere_host.host.id

  datastore_id = data.vsphere_datastore.datastore_root.id
  datacenter_id        = data.vsphere_datacenter.datacenter.id

  ovf_deploy {
    allow_unverified_ssl_cert = true
    remote_ovf_url            = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.ova"
    disk_provisioning         = "thin"
    ovf_network_map = {
      "Network 1" = data.vsphere_network.network.id
      "Network 2" = data.vsphere_network.network.id
    }
  }

  extra_config = {
    "guestinfo.hostname"     = var.vm.vm_name,
    "guestinfo.instance-id"     = var.vm.vm_name,
    "guestinfo.password"     = "ubuntu"
    "guestinfo.userdata"          = base64encode(templatefile(format("%s/%s", path.module, local.cloud_init_templates[var.vm.system_image]),
    {
      vm_name    = var.vm.vm_name
      user       = lookup(var.vm, "user", "unset_user")
      vm_address = lookup(var.vm, "private_ip", "learned")
      vm_gateway  = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["gateway_ip_address"]
      netmask     = split("/", var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["cidr_block"])[1]
      nameservers = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["nameservers"]
      search      = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["search"]
      interface   = lookup(var.network[var.vm.network_name]["subnets"][var.vm.subnet_name], "network_interface")
      password   = var.vm.default_password
      users_list = var.vm.users_list
    }
  ))
    "guestinfo.userdata.encoding" = "base64"
  }

  enable_disk_uuid = tobool(lower(lookup(var.vm.extra_parameters, "enable_disk_uuid", "true")))
  disk {
    label             = "disk0"
    datastore_id      = data.vsphere_datastore.datastore_root.id
    size              = lookup(var.vm.root_volume, "size", var.vm.default_root_volume_size)
    eagerly_scrub     = true
    thin_provisioned  = false
    keep_on_remove    = true
    storage_policy_id = null
  }

  dynamic "disk" {
    for_each = local.non_empty_data_volumes
    content {
      label             = lookup(disk.value, "disk_label", format("disk%s", disk.value.index))
      size              = lookup(disk.value, "size", var.vm.default_data_volume_size)
      unit_number       = disk.value.index
      datastore_id      = data.vsphere_datastore.datastore_datadisks[each.key].id
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
