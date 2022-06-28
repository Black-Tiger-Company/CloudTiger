# output vm_parameters {
#   value       = {
# 	vm_name = google_compute_instance.virtual_machine.name
# 	private_ip = google_compute_instance.virtual_machine.network_interface.0.network_ip
# 	subnet_full_name = google_compute_instance.virtual_machine.network_interface.0.subnetwork
# 	network_full_name = google_compute_instance.virtual_machine.network_interface.0.network
# 	subnet = var.vm.subnet_name
# 	network_name = var.vm.network_name
# 	user = var.vm.user
# 	public_ip = length(google_compute_instance.virtual_machine.network_interface.0.access_config) == 0 ? "0.0.0.0" : google_compute_instance.virtual_machine.network_interface.0.access_config.0.nat_ip
# 	ssh_key = var.vm.ssh_public_key
# 	group = var.vm.group
#   }
#   description = "Map of VMs parameters"
#   depends_on  = [google_compute_instance.virtual_machine]
# }

output "vm_parameters" {
  value = {
    vm_name           = google_compute_instance.virtual_machine.name
    private_ip        = google_compute_instance.virtual_machine.network_interface.0.network_ip
    subnet_full_name  = var.vm.subnet_name
    network_full_name = var.vm.network_name
    subnet            = var.vm.subnet_name
    network_name      = var.vm.network_name
    user              = var.vm.user
    public_ip         = var.vm.subnet_type != "private" ? google_compute_instance.virtual_machine.network_interface.0.access_config.0.nat_ip : "0.0.0.0"
    ssh_key           = basename(var.vm.ssh_public_key_path)
    group             = var.vm.group
  }
  description = "Map of VMs parameters"
  depends_on  = [google_compute_instance.virtual_machine]
}