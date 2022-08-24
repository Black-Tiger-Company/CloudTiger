output data_addresses {
  value       = local.address_dict
#   value       = data.fortios_firewall_address.addresses
  sensitive   = false
  description = "description"
  depends_on  = []
}

output data_system_interfaces {
	value = local.system_interface_dict
	# value = data.fortios_system_interface.system_interfaces
}