resource "azurerm_resource_group" "rg" {
  name = format("%s%s_rg", var.network.module_prefix, var.network.network_name)
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
