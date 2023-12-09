data "vsphere_datacenter" "datacenter" {
  name = var.network.datacenter_name
}

data "vsphere_network" "networks" {
  for_each      = var.network.private_subnets
  name          = each.key
  datacenter_id = data.vsphere_datacenter.datacenter.id
}