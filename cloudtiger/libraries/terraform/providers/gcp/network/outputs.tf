output "network_parameters" {
  value = {
    network_name = google_compute_network.network.name
    private_subnets = {
      for private_subnet_name, private_subnet in google_compute_subnetwork.private_subnets :
      private_subnet_name => {
        cidr_block = private_subnet.ip_cidr_range
      }
      # {
      # 	# network = private_subnet.network
      # 	cidr_block = private_subnet.ip_cidr_range
      # }
    }
    public_subnets = {
      for public_subnet_name, public_subnet in google_compute_subnetwork.public_subnets :
      public_subnet_name => {
        cidr_block = public_subnet.ip_cidr_range
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
