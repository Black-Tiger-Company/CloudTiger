terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_addrgrp" "trname" {
  name          = var.firewall_addr_group.name
  allow_routing = var.firewall_addr_group.allow_routing
  color         = var.firewall_addr_group.color
  exclude       = var.firewall_addr_group.exclude
  visibility    = var.firewall_addr_group.visibility

  member {
    name = ""
  }

	dynamic "member" {
		for_each = var.firewall_addr_group.members
		content {
			name = member
		}
	}

}