output "vm_parameters" {
  value = {
    vm_name      = vsphere_virtual_machine.virtual_machine.name
    private_ip   = vsphere_virtual_machine.virtual_machine.default_ip_address
    network_name = var.vm.network_name
    user         = lookup(var.vm, "user", "unset_user")
    subnet       = var.vm.subnet_name
    ssh_key      = var.vm.ssh_public_key
    group        = var.vm.group
    port         = lookup(var.vm.extra_parameters, "custom_ssh_port", "22")
  }
  description = "Map of VMs parameters"
  depends_on  = [vsphere_virtual_machine.virtual_machine]
}

output "vm_data" {
  value     = vsphere_virtual_machine.virtual_machine
  sensitive = true
}