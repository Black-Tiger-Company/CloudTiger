resource "vsphere_folder" "folder" {
  path          = var.folder.path
  type          = var.folder.type
  datacenter_id = var.datacenter[var.folder.datacenter_name].datacenter_id
}