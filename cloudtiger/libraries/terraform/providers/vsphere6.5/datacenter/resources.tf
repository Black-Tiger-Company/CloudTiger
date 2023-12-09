
resource "vsphere_compute_cluster" "cluster" {
  for_each      = var.datacenter.compute_clusters
  name          = each.value.name
  datacenter_id = local.current_datacenter.id
  #   host_system_ids = [vsphere_host.host.*.id]

  drs_enabled          = true
  drs_automation_level = "fullyAutomated"

  ha_enabled = true
}

resource "vsphere_host" "host" {
  for_each = var.datacenter.hosts
  hostname = each.value.hostname
  username = each.value.username
  password = each.value.password
  license  = each.value.license
  cluster  = vsphere_compute_cluster.cluster[each.value.compute_cluster].id
}

resource "vsphere_nas_datastore" "datastore" {
  count           = length(var.datacenter.datastores.nfs)
  name            = var.datacenter.nfs[count.index]
  host_system_ids = [vsphere_host.host.*.id]

  type         = "NFS"
  remote_hosts = ["nfs"]
  remote_path  = format("/%s/datastore/%s", var.datacenter.datacenter_name, var.datacenter.nfs[count.index])
}

# resource "vsphere_vmfs_datastore" "datastore" {
# 	count = length(var.datacenter.datastores.san)
#   name           = var.datacenter.datastores.nfs[count.index]
#   host_system_id = [data.vsphere_host.host.id]
#   folder         = "datastore-folder"

#   disks = [data.vsphere_vmfs_disks.available.disks]
# }

resource "vsphere_folder" "folder" {
  for_each      = var.datacenter.folders
  path          = format("%s/%s/%s", var.datacenter.datacenter_name, each.value.type, each.value.folder)
  type          = each.value.type
  datacenter_id = local.current_datacenter.id
}