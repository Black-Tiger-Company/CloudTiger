
data "vsphere_compute_cluster" "cluster" {
  for_each      = var.datacenter.unmanaged.compute_clusters
  name          = each.value.name
  datacenter_id = local.current_datacenter.id
}

data "vsphere_host" "host" {
  count         = length(var.datacenter.unmanaged.hosts)
  name          = var.datacenter.unmanaged.hosts[count.index]
  datacenter_id = local.current_datacenter.id
}

data "vsphere_datastore" "nfs" {
  count         = length(var.datacenter.unmanaged.datastores.nfs)
  name          = var.datacenter.unmanaged.datastores.nfs[count.index]
  datacenter_id = local.current_datacenter.id
}

data "vsphere_datastore" "san" {
  count         = length(var.datacenter.unmanaged.datastores.san)
  name          = var.datacenter.unmanaged.datastores.nfs[count.index]
  datacenter_id = local.current_datacenter.id
}

# data "vsphere_datastore" "ds" {
# 	name = var.datacenter.datastores.name
# 	datacenter_id = var.datacenters_wanted[lower(var.datastores.datacenter)].id
# }

# data "vsphere_datastore" "default" {
#     name = "bnc2i_dc2_vmstore1"
# 	datacenter_id = var.datacenters_wanted[lower(var.datastores.datacenter)].id
# }

data "vsphere_folder" "folder" {
  for_each = var.datacenter.unmanaged.folders
  path     = format("%s/%s/%s", var.datacenter.datacenter_name, each.value.type, each.value.folder)
}

data "vsphere_virtual_machine" "packer_template" {
  count = length(var.datacenter.templates_list)

  name          = var.datacenter.templates_list[count.index]
  datacenter_id = local.current_datacenter.id
}
