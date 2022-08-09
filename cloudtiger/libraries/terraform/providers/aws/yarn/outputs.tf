output "yarn_parameters" {
  value = {
    ssh_key           = basename(var.vm.ssh_public_key_path)
  }
}