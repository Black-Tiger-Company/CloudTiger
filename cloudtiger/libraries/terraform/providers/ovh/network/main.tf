############
# Network (VPC for AWS)
############

 resource "ovh_cloud_project_network_private" "network" {
    service_name = var.network.network_name
    name         = format("%s%s_network", var.network.module_prefix, var.network.network_name)
    regions      = [var.network.location]
    provider     = ovh.ovh
    vlan_id      = var.network.vlan_id
 }

############
# Private subnets
# isolated from Internet in ingress
############


 resource "ovh_cloud_project_network_private_subnet" "private_subnets" {

  for_each = var.network.private_subnets

    service_name = var.network.network_name
    # Identifiant de la ressource ovh_cloud_network_private nommée network
    network_id   = ovh_cloud_project_network_private.network.id
    start        = cidrhost(each.value.cidr_block, 0)
    end          = cidrhost(each.value.cidr_block, cidrnetmask(local.cidr_block))
    network      = var.network.cidr_block
    dhcp         = true
    region       = var.network.location
    provider     = ovh.ovh
    no_gateway   = true
 }

############
# Public subnets
# accessible from Internet in ingress
############

 resource "ovh_cloud_project_network_private_subnet" "public_subnets" {

  for_each = var.network.public_subnets

    service_name = var.network.network_name
    # Identifiant de la ressource ovh_cloud_network_private nommée network
    network_id   = ovh_cloud_project_network_private.network.id
    start        = cidrhost(each.value.cidr_block, 0)
    end          = cidrhost(each.value.cidr_block, cidrnetmask(local.cidr_block))
    network      = var.network.cidr_block
    dhcp         = true
    region       = var.network.location
    provider     = ovh.ovh
    no_gateway   = true
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
  direction         = each.value.direction
  ethertype         = "IPv4"
  protocol          = each.value.protocol
  port_range_min    = replace(each.value.to_port, "-1", "*")
  port_range_max    = replace(each.value.to_port, "-1", "*")
  remote_ip_prefix  = each.value.cidr[0]
  security_group_id = lookup(openstack_networking_secgroup_v2.private_network_security_group, each.value.attached_subnet, lookup(openstack_networking_secgroup_v2.public_network_security_group, each.value.attached_subnet, {})).id
}

resource "openstack_networking_secgroup_rule_v2" "security_rule_egress" {
  for_each                   = local.mapped_firewall_rules_ingress
  direction         = each.value.direction
  ethertype         = "IPv4"
  protocol          = each.value.protocol
  port_range_min    = replace(each.value.to_port, "-1", "*")
  port_range_max    = replace(each.value.to_port, "-1", "*")
  remote_ip_prefix  = each.value.cidr[0]
  security_group_id = lookup(openstack_networking_secgroup_v2.private_network_security_group, each.value.attached_subnet, lookup(openstack_networking_secgroup_v2.public_network_security_group, each.value.attached_subnet, {})).id
}
