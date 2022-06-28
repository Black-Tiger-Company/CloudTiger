output "network_parameters" {
  value = {
    network_name = format("%s_%s_network", var.network.module_prefix, var.network.network_name)
    network_id   = "network_id"
    private_subnets = merge({
      for private_subnet_name, private_subnet in nutanix_subnet.private_subnets :
      private_subnet_name => {
        cidr_block         = private_subnet.subnet_ip
        vlan_id            = private_subnet.vlan_id
        uuid               = private_subnet.metadata.uuid
        gateway_ip_address = private_subnet.default_gateway_ip
      }
      }
    )
    public_subnets = {
      for public_subnet_name, public_subnet in nutanix_subnet.public_subnets :
      public_subnet_name => {
        cidr_block = public_subnet.subnet_ip
        vlan_id    = public_subnet.vlan_id
      }
    }
  }
  description = "description"
  depends_on  = []
}