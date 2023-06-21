output "vm_parameters" {
  value = {
    vm_name           = openstack_compute_instance_v2.virtual_machine.name
    private_ip        = openstack_compute_instance_v2.virtual_machine.access_ip_v4
    subnet_full_name  = var.vm.subnet_name
    # subnet_full_name  = openstack_compute_instance_v2.virtual_machine.network[var.vm.subnet_name].name
    # network_full_name = openstack_compute_instance_v2.security_group_vm.vpc_id
    subnet            = var.vm.subnet_name
    network_name      = var.vm.network_name
    user              = var.vm.user
    public_ip         = openstack_compute_instance_v2.virtual_machine.access_ip_v4
    # public_ip         = var.vm.subnet_type == "private" ? "0.0.0.0" : openstack_compute_instance_v2.virtual_machine.network["Ext-Net"].fixed_ip_v4
    ssh_key           = basename(var.vm.ssh_public_key_path)
    group             = var.vm.group
  }
  description = "Map of VMs parameters"
  depends_on  = [openstack_compute_instance_v2.virtual_machine]
}