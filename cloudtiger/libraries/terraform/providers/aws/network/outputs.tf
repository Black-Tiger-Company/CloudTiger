output "network_parameters" {
  value = {
    network_name = format("%s_%s_network", var.network.module_prefix, var.network.network_name)
    network_id   = aws_vpc.network.id
    private_subnets = {
      for private_subnet_name, private_subnet in aws_subnet.private_subnets :
      private_subnet_name => {
        cidr_block = private_subnet.cidr_block
        id         = private_subnet.id
      }
      # {
      # 	# network = private_subnet.network
      # 	cidr_block = private_subnet.ip_cidr_range
      # }
    }
    public_subnets = {
      for public_subnet_name, public_subnet in aws_subnet.public_subnets :
      public_subnet_name => {
        cidr_block = public_subnet.cidr_block
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