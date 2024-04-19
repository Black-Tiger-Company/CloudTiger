
locals {

  main_disk = data.vsphere_virtual_machine.ova_template.disks.0

  cdrom_backed = [{ "Backing" : {} }]

  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }

  cloud_init_templates = {
    "jammy/current/jammy-server-cloudimg-amd64.ova" = "cloudinit_ubuntu2204.cfg.tpl"
    "ubuntu-2204-lts-server-bt-ad-template" = "cloudinit_ubuntu2204.cfg.tpl"
    "ubuntu2204-template" = "cloudinit_ubuntu2204.cfg.tpl"
    "bt-ubuntu-2204-server-model" = "cloudinit_ubuntu2204.cfg.tpl"
  }

  guestIdMappings = {
    "ubuntu-2204-lts-server-bt-ad-template" = "ubuntu64Guest"
    "ubuntu2204-template" = "ubuntu64Guest"
    "bt-ubuntu-2204-server-model" = "ubuntu64Guest"
  }
}

data "vsphere_virtual_machine" "ova_template" {
  name          = var.vm.system_image
  datacenter_id = data.vsphere_datacenter.datacenter.id
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

# locals {
#   # Split the folder path
#   folder_paths = split("/", var.vm.folder)

#   full_paths = [for i in range(length(local.folder_paths)) : join("/", slice(local.folder_paths, 0, i + 1))]
# }

# resource "vsphere_folder" "folders" {
#   for_each      = { for idx, path in local.full_paths : path => idx }
#   path          = each.key
#   type          = "vm"
#   datacenter_id = data.vsphere_datacenter.datacenter.id

# }

resource "vsphere_virtual_machine" "virtual_machine" {
  #depends_on    = [vsphere_folder.folders]

  ### added to avoid messing with cdrom reader or very specific settings on imported machines
  lifecycle {
    ignore_changes = [
      cdrom,
      tools_upgrade_policy,
      annotation,
      disk.0.eagerly_scrub,
      disk.0.thin_provisioned,
      vapp.0.properties
    ]
  }

  name     = var.vm.vm_name
  num_cpus = var.vm.instance_type.nb_sockets * var.vm.instance_type.nb_vcpu_per_socket
  memory   = var.vm.instance_type.memory
  folder   = var.vm.folder

  scsi_type                  = "pvscsi"
  resource_pool_id           = data.vsphere_resource_pool.pool.id
  guest_id                   = local.guestIdMappings[var.vm.system_image]
  host_system_id    = data.vsphere_host.host.id

  datastore_id = data.vsphere_datastore.datastore_root.id

  dynamic "clone" {
    for_each = ((var.vm.system_image == null) || (var.vm.imported)) ? [] : [1]
    content {
      template_uuid   = data.vsphere_virtual_machine.ova_template.id
      linked_clone    = false
      timeout         = 120
      ovf_network_map = {}
      ovf_storage_map = {}
    }
  }

  vapp {
    properties = {
      "hostname"     = var.vm.vm_name,
      "instance-id"     = var.vm.vm_name,
      "user-data"     = base64encode(templatefile(format("%s/%s", path.module, local.cloud_init_templates[var.vm.system_image]),
        {
          vm_name    = var.vm.vm_name
          ad_groups   = lookup(var.vm, "ad_groups", [])
          user       = lookup(var.vm, "user", "unset_user")
          vm_address = lookup(var.vm, "private_ip", "learned")
          vm_gateway  = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["gateway_ip_address"]
          netmask     = split("/", var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["cidr_block"])[1]
          nameservers = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["nameservers"]
          search      = var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["search"]
          # interface   = lookup(var.network[var.vm.network_name]["subnets"][var.vm.subnet_name], "network_interface")
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
    }
  }

  enable_disk_uuid = tobool(lower(lookup(var.vm.extra_parameters, "enable_disk_uuid", "true")))
  disk {
    label             = "disk0"
    datastore_id      = data.vsphere_datastore.datastore_root.id
    size              = max(lookup(var.vm, "root_volume_size", var.vm.default_root_volume_size), local.main_disk.size)
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
      datastore_id      = data.vsphere_datastore.datastore_datadisks[disk.key].id
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
  num_cores_per_socket   = lookup(var.vm.instance_type, "nb_vcpu_per_socket", 1)
  cpu_limit              = lookup(var.vm.extra_parameters, "cpu_limit", -1)
  memory_share_level     = lookup(var.vm.extra_parameters, "memory_share_level", "normal")
  memory_limit           = lookup(var.vm.extra_parameters, "memory_limit", -1)
  cpu_share_level        = lookup(var.vm.extra_parameters, "cpu_share_level", "normal")
  sync_time_with_host    = tobool(replace(lookup(var.vm.extra_parameters, "sync_time_with_host", "None"), "None", "false"))
  tools_upgrade_policy   = lookup(var.vm.extra_parameters, "tools_upgrade_policy", "manual")

  cdrom {
    client_device = true
  }

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
