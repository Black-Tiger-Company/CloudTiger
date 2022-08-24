terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.13.1"
    }
  }
}

data "fortios_firewall_addresslist" address_list {
}

data "fortios_system_interfacelist" system_interface_list {
}

locals {
	system_interface_list = tolist(toset(data.fortios_system_interfacelist.system_interface_list.namelist))
	address_list = tolist(toset(data.fortios_firewall_addresslist.address_list.namelist))
}


data "fortios_system_interface" system_interfaces {
	count = length(local.system_interface_list)
	name = local.system_interface_list[count.index]
}

data "fortios_firewall_address" addresses {
	count = length(local.address_list)
	name = local.address_list[count.index]
}

locals {
	system_interface_dict = {
		for system_interface in data.fortios_system_interface.system_interfaces :
		system_interface.name => {
			"name" = system_interface.name
			"properties" = {
				"dnssl" = lookup(system_interface, "dnssl", {"domain":""}).domain
				"ip" = system_interface.ip
				"vlanid" = system_interface.vlanid
			}
		}
		if system_interface.name != null && system_interface.vlanid != null
	}

	# system_interface_dict = data.fortios_system_interfacelist.system_interface_list.namelist
	# system_interface_dict = length(data.fortios_system_interface.system_interfaces)

	address_dict = {
		for address in data.fortios_firewall_address.addresses :
		address.name => address.subnet
		if address.name != null
	}

	# address_dict = data.fortios_firewall_addresslist.address_list.namelist
	# address_dict = length(data.fortios_firewall_address.addresses)
}