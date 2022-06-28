output "network_parameters" {
  value = {
    network_name = format("%s_network", var.network.network_name)
    network_id   = azurerm_virtual_network.vmnet.id

    private_subnets = {
      for private_subnet_name, private_subnet in azurerm_subnet.private_subnets :
      private_subnet_name => {
        id = private_subnet.id
      }
    }
    public_subnets = {
      for public_subnet_name, public_subnet in azurerm_subnet.public_subnets :
      public_subnet_name => {
        id = public_subnet.id
      }
    }
    public_ip   = azurerm_public_ip.public_ip.id
    nat_gateway = azurerm_nat_gateway.aznat.id
  }
}
