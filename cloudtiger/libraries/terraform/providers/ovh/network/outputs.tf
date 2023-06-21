output "network_parameters" {
  value = {
    network_name = format("%s_%s_network", var.network.module_prefix, var.network.network_name)
    network_id   = ovh_cloud_project_network_private.network.id
    private_subnets = {
      for private_subnet_name, private_subnet in ovh_cloud_project_network_private_subnet.private_subnets :
      private_subnet_name => {
        cidr_block = private_subnet.cidr
        id         = private_subnet.id
      }
      # {
      # 	# network = private_subnet.network
      # 	cidr_block = private_subnet.ip_cidr_range
      # }
    }
    public_subnets = {
      for public_subnet_name, public_subnet in ovh_cloud_project_network_private_subnet.public_subnets :
      public_subnet_name => {
        cidr_block = public_subnet.cidr
        id         = public_subnet.id
      }
      # {
      # 	# network = private_subnet.network
      # 	cidr_block = private_subnet.ip_cidr_range
      # }
    }
  }
  description = "description"
  depends_on  = []
}