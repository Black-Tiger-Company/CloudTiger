locals {
  default_ip = length(data.nutanix_virtual_machine.virtual_machine_data.nic_list) > 0 ? (length(data.nutanix_virtual_machine.virtual_machine_data.nic_list[0].ip_endpoint_list) > 0 ? data.nutanix_virtual_machine.virtual_machine_data.nic_list[0].ip_endpoint_list[0].ip : "192.168.0.1") : "192.168.0.1"
}

output "vm_parameters" {
  value = {
    vm_name      = nutanix_virtual_machine.virtual_machine.name
    private_ip   = (!(local.subnet_has_managed_ips)) ? lookup(var.vm, "private_ip", "unset") : local.default_ip
    # private_ip   = (!(local.subnet_has_managed_ips)) ? lookup(var.vm, "private_ip", "unset") : nutanix_virtual_machine.virtual_machine.nic_list[0].ip_endpoint_list[0].ip
    subnet       = var.vm.subnet_name
    network_name = var.vm.network_name
    user         = var.vm.user
    ssh_key      = var.vm.ssh_public_key
    group        = var.vm.group
    port         = lookup(var.vm.extra_parameters, "custom_ssh_port", "22")
  }
  description = "Map of VMs parameters"
}