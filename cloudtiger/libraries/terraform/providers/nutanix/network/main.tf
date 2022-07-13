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
}

resource "nutanix_subnet" "private_subnets" {

  for_each = var.network.private_subnets

  cluster_uuid = local.cluster_map[each.value.availability_zone].metadata.uuid

  name        = each.key
  subnet_type = "VLAN"

}

resource "nutanix_subnet" "public_subnets" {

  for_each     = var.network.public_subnets
  cluster_uuid = var.network.datacenter_name

  name        = format("%s_%s_%s_private_subnet", var.network.module_prefix, var.network.network_name, each.key)
  subnet_type = "VLAN"

  categories {
    name  = "name"
    value = format("%s_%s_virtual_machine", var.network.module_prefix, var.network.network_name)
  }

  dynamic "categories" {
    for_each = var.network.module_labels
    content {
      name  = categories.key
      value = categories.value
    }
  }
}