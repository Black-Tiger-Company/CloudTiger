output "vm_parameters" {
  value = {
    vm_name           = aws_instance.virtual_machine.tags.Name
    private_ip        = aws_instance.virtual_machine.private_ip
    subnet_full_name  = aws_instance.virtual_machine.subnet_id
    network_full_name = aws_security_group.security_group_vm.vpc_id
    subnet            = var.vm.subnet_name
    network_name      = var.vm.network_name
    user              = var.vm.user
    public_ip         = var.vm.subnet_type == "private" ? "0.0.0.0" : aws_instance.virtual_machine.public_ip
    ssh_key           = basename(var.vm.ssh_public_key_path)
    group             = aws_instance.virtual_machine.tags.group
  }
  description = "Map of VMs parameters"
  depends_on  = [aws_instance.virtual_machine]
}