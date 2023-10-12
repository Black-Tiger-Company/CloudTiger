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
# Network (VPC for AWS)
############

# Associating cloud project to vRack
resource "ovh_vrack_cloudproject" "vcp" {
  # service_name = var.service_name
  # project_id   = var.project_id
  service_name = "demo-blacktiger"
  project_id   = "XXX"
}

resource "ovh_cloud_project_kube" "my_kube_cluster" {
  service_name = var.service_name
  name         = "my-super-kube-cluster"
  region       = "BHS5"
  version      = "1.22"
}

 resource "ovh_cloud_project_network_private" "network" {
    # service_name = var.network.network_name
    service_name = "demo-blacktiger"
    name         = format("%s%s_network", var.network.module_prefix, var.network.network_name)
    regions      = [var.network.location]
    # provider     = ovh.ovh
    vlan_id      = var.network.vlan_id
 }

############
# Private subnets
# isolated from Internet in ingress
############


 resource "ovh_cloud_project_network_private_subnet" "private_subnets" {

  for_each = var.network.private_subnets

    # service_name = var.network.network_name
    service_name = "demo-blacktiger"
    # Identifiant de la ressource ovh_cloud_network_private nommée network
    network_id   = ovh_cloud_project_network_private.network.id
    start        = cidrhost(each.value.cidr_block, 0)
    end          = cidrhost(each.value.cidr_block, tonumber(split("/", each.value.cidr_block)[1]))
    network      = var.network.network_cidr
    dhcp         = true
    region       = var.network.location
    # provider     = ovh.ovh
    no_gateway   = false
 }

############
# Public subnets
# accessible from Internet in ingress
############

 resource "ovh_cloud_project_network_private_subnet" "public_subnets" {

  for_each = var.network.public_subnets

    # service_name = var.network.network_name
    service_name = "demo-blacktiger"
    # Identifiant de la ressource ovh_cloud_network_private nommée network
    network_id   = ovh_cloud_project_network_private.network.id
    start        = cidrhost(each.value.cidr_block, 0)
    end          = cidrhost(each.value.cidr_block, tonumber(split("/", each.value.cidr_block)[1]))
    network      = var.network.network_cidr
    dhcp         = true
    region       = var.network.location
    # provider     = ovh.ovh
    no_gateway   = false
 }

############
# Security Group / Firewall group
############

resource "openstack_networking_secgroup_v2" "public_network_security_group" {
  for_each            = var.network.public_subnets
  name                = format("%s%s_%s_subnet_sg", var.network.module_prefix, var.network.network_name, each.key)
  description = "Description SG"
}

resource "openstack_networking_secgroup_v2" "private_network_security_group" {
  for_each            = var.network.private_subnets
  name                = format("%s%s_%s_subnet_sg", var.network.module_prefix, var.network.network_name, each.key)
  description = "Description SG"
}

locals{
  mapped_firewall_rules_ingress = { for firewall_rule in var.network.firewall_rules_ingress :
    firewall_rule.rule_name => firewall_rule
  }

  mapped_firewall_rules_egress = { for firewall_rule in var.network.firewall_rules_egress :
    firewall_rule.rule_name => firewall_rule
  }

  protocol_map = {
    "tcp" = "Tcp"
    "udp" = "Udp"
    "icmp" = "Icmp"
    "ah" = "Ah"
    "esp" = "Esp"
  }

}


resource "openstack_networking_secgroup_rule_v2" "security_rule_ingress" {
  for_each                   = local.mapped_firewall_rules_ingress
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = each.value.protocol
  port_range_min    = each.value.to_port
  port_range_max    = each.value.to_port
  remote_ip_prefix  = each.value.cidr[0]
  security_group_id = lookup(openstack_networking_secgroup_v2.private_network_security_group, each.value.attached_subnet, lookup(openstack_networking_secgroup_v2.public_network_security_group, each.value.attached_subnet, {})).id
}

resource "openstack_networking_secgroup_rule_v2" "security_rule_egress" {
  for_each                   = local.mapped_firewall_rules_ingress
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = each.value.protocol
  port_range_min    = each.value.to_port
  port_range_max    = each.value.to_port
  remote_ip_prefix  = each.value.cidr[0]
  security_group_id = lookup(openstack_networking_secgroup_v2.private_network_security_group, each.value.attached_subnet, lookup(openstack_networking_secgroup_v2.public_network_security_group, each.value.attached_subnet, {})).id
}
