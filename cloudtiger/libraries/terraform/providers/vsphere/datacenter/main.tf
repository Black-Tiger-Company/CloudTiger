### vcenter specific resources
resource "vsphere_datacenter" "datacenter" {
  count = (var.datacenter.managed == true ? 1 : 0)
  name  = var.datacenter.datacenter_name
}

data "vsphere_datacenter" "datacenter" {
  count = (var.datacenter.managed == false ? 1 : 0)
  name  = var.datacenter.datacenter_name
}

locals {
  current_datacenter = var.datacenter.managed == true ? vsphere_datacenter.datacenter[0] : data.vsphere_datacenter.datacenter[0]
}