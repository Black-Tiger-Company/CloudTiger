terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.13.2"
    }
  }
}

resource "fortios_firewall_addrgrp" "trname" {
  for_each      = var.firewall_addr_group
  name          = var.firewall_addr_group[each.key].name
  allow_routing = var.firewall_addr_group[each.key].allow_routing
  color         = var.firewall_addr_group[each.key].color
  exclude       = var.firewall_addr_group[each.key].exclude
  visibility    = var.firewall_addr_group[each.key].visibility

  member {
    name = ""
  }

	dynamic "member" {
		for_each = var.firewall_addr_group[each.key].members
		content {
			name = member
		}
	}

}