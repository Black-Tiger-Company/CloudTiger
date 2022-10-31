terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_addrgrp" "trname" {

  name = var.firewall_addr_group.name
  type  = lookup(var.firewall_addr_group, "type", null)
  category = lookup(var.firewall_addr_group, "category", null)    # Valid values: default, ztna-ems-tag, ztna-geo-tag.
  uuid = lookup(var.firewall_addr_group, "uuid", null)   #(UUID; automatically assigned but can be manually reset).
  comment = lookup(var.firewall_addr_group, "comment", null)
  exclude = lookup(var.firewall_addr_group, "exclude", null) # Valid values: enable, disable.
  visibility = lookup(var.firewall_addr_group, "visibility", null) # Valid values: enable, disable.
  color = lookup(var.firewall_addr_group, "color", null)
  allow_routing = lookup(var.firewall_addr_group, "allow_routing", null) # Valid values: enable, disable.
  fabric_object = lookup(var.firewall_addr_group, "fabric_object", null)  # Valid values: enable, disable.
  dynamic_sort_subtable = lookup(var.firewall_addr_group, "dynamic_sort_subtable", null) # Options: [ false, true, natural, alphabetical ]. false: Default value, do not sort tables; true/natural: sort tables in natural order. For example: [ a10, a2 ] --> [ a2, a10 ]; alphabetical: sort tables in alphabetical order. For example: [ a10, a2 ] --> [ a10, a2 ].
  vdomparam = lookup(var.firewall_addr_group, "vdomparam", null)

	dynamic "member" {
		for_each = var.firewall_addr_group.members
		content {
			name = member.value
		}
	}

	dynamic "exclude_member" {
		for_each = lookup(var.firewall_addr_group, "exclude_members", [])
		content {
			name = exclude_member.value
		}
	}

  #   tagging - Config object tagging. The structure of tagging block is documented below.s
}