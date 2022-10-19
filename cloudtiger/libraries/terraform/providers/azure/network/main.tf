resource "azurerm_resource_group" "rg" {
  name = format("%s%s_network_rg", var.network.module_prefix, var.network.network_name)
  tags = merge(
    var.network.module_labels,
    {
      "name" = format("%s_%s_firewall", var.network.module_prefix, var.network.network_name)
    }
  )
  location = var.network.location
}

################
# Virtual network
################

resource "azurerm_virtual_network" "vmnet" {
  name                = var.network.network_name
  address_space       = formatlist("%s", var.network.network_cidr)
  location            = var.network.location
  resource_group_name = azurerm_resource_group.rg.name
}

################
# Private subnet
################

resource "azurerm_subnet" "private_subnets" {
  for_each             = var.network.private_subnets
  name                 = each.key
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vmnet.name
  address_prefixes     = formatlist("%s", var.network.private_subnets[each.key].cidr_block)
}

################
# Public subnet
################

resource "azurerm_subnet" "public_subnets" {
  for_each             = var.network.public_subnets
  name                 = each.key
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vmnet.name
  address_prefixes     = formatlist("%s", var.network.public_subnets[each.key].cidr_block)
}

################
# Publique IP
################

resource "azurerm_public_ip" "public_ip" {
  name                = format("%s-PublicIP", var.network.network_name)
  location            = var.network.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
  # location              = [var.network.common_availability_zone[0]]
}

################
# NAT Gateway
################

resource "azurerm_nat_gateway" "aznat" {
  name                = format("%s-nat-Gateway", azurerm_public_ip.public_ip.name)
  location            = var.network.location
  resource_group_name = azurerm_resource_group.rg.name
  zones               = (var.network.common_availability_zone == []) ? null : var.network.common_availability_zone
  depends_on          = [azurerm_virtual_network.vmnet]
}

################
# Association between gateway and public IP
################

resource "azurerm_nat_gateway_public_ip_association" "ip_association" {
  # for_each 			 = var.network
  nat_gateway_id       = azurerm_nat_gateway.aznat.id
  public_ip_address_id = azurerm_public_ip.public_ip.id

  depends_on = [azurerm_nat_gateway.aznat, azurerm_public_ip.public_ip]
}

################
# Security groups
################

resource "azurerm_network_security_group" "public_network_security_group" {
  for_each            = var.network.public_subnets
  name                = format("%s%s_%s_subnet_sg", var.network.module_prefix, var.network.network_name, each.key)
  location            = var.network.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_network_security_group" "private_network_security_group" {
  for_each            = var.network.private_subnets
  name                = format("%s%s_%s_subnet_sg", var.network.module_prefix, var.network.network_name, each.key)
  location            = var.network.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet_network_security_group_association" "public_network_security_association" {
  for_each                  = var.network.public_subnets
  subnet_id                 = azurerm_subnet.public_subnets[each.key].id
  network_security_group_id = azurerm_network_security_group.public_network_security_group[each.key].id
}

resource "azurerm_subnet_network_security_group_association" "private_network_security_association" {
  for_each                  = var.network.private_subnets
  subnet_id                 = azurerm_subnet.private_subnets[each.key].id
  network_security_group_id = azurerm_network_security_group.private_network_security_group[each.key].id
}

################
# Firewall rules
################
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

resource "azurerm_network_security_rule" "security_rule_ingress" {
  for_each                   = local.mapped_firewall_rules_ingress
  name                       = format("%s_%s", each.value.description, each.key)

  priority                   = each.value.priority
  direction                  = each.value.direction
  access                     = each.value.access
  protocol                   = local.protocol_map[each.value.protocol]
  source_port_range          = each.value.source_port_range
  # source_port_range          = replace(each.value.from_port, "-1", "*")
  destination_port_range     = replace(each.value.to_port, "-1", "*")
  source_address_prefix      = each.value.cidr[0]
  destination_address_prefix = "*"

  resource_group_name         = azurerm_resource_group.rg.name
  network_security_group_name = lookup(azurerm_network_security_group.private_network_security_group, each.value.attached_subnet, lookup(azurerm_network_security_group.public_network_security_group, each.value.attached_subnet, {})).name
}

resource "azurerm_network_security_rule" "security_rule_egress" {
  for_each                   = local.mapped_firewall_rules_egress
  name                       = format("%s_%s", each.value.description, each.key)

  priority                   = each.value.priority
  direction                  = each.value.direction
  access                     = each.value.access
  protocol                   = local.protocol_map[each.value.protocol]
  source_port_range          = each.value.source_port_range
  # source_port_range          = replace(each.value.from_port, "-1", "*")
  destination_port_range     = replace(each.value.to_port, "-1", "*")
  source_address_prefix      = each.value.cidr[0]
  destination_address_prefix = "*"

  resource_group_name         = azurerm_resource_group.rg.name
  network_security_group_name = lookup(azurerm_network_security_group.private_network_security_group, each.value.attached_subnet, lookup(azurerm_network_security_group.public_network_security_group, each.value.attached_subnet, {})).name
}