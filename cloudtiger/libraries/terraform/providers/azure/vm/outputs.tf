
output "vm_parameters" {
  value = {
    vm_name           = azurerm_virtual_machine.virtual_machine.name
    private_ip        = azurerm_network_interface.network_interface.private_ip_address
    subnet_full_name  = var.vm.subnet_name
    network_full_name = var.vm.network_name
    subnet            = var.vm.subnet_name
    network_name      = var.vm.network_name
    user              = var.vm.user
    public_ip         = var.vm.subnet_type != "private" ? azurerm_public_ip.public_ip[0].ip_address : "0.0.0.0"
    ssh_key           = basename(var.vm.ssh_public_key_path)
    group             = var.vm.group
  }
  description = "Map of VMs parameters"
  depends_on  = [azurerm_virtual_machine.virtual_machine]
}