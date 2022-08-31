terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_localinpolicy" "trname" {
    action 			  = lookup(var.firewall_local_in_policy, "action", null) # Valid values: accept, deny.
	ha_mgmt_intf_only = var.firewall_local_in_policy.ha_mgmt_intf_only # Valid values: enable, disable.
	intf              = var.firewall_local_in_policy.intf
	policyid          = var.firewall_local_in_policy.policyid
	schedule          = var.firewall_local_in_policy.schedule
	status            = var.firewall_local_in_policy.status #Valid values: enable, disable.

	uuid = lookup(var.firewall_local_in_policy, "uuid", null)
	srcaddr_negate = lookup(var.firewall_local_in_policy, "srcaddr_negate", null) # Valid values: enable, disable.
	dstaddr_negate = lookup(var.firewall_local_in_policy, "dstaddr_negate", null) # Valid values: enable, disable.
	service_negate = lookup(var.firewall_local_in_policy, "service_negate", null) # Valid values: enable, disable.
	comments = lookup(var.firewall_local_in_policy, "comments", null)
	dynamic_sort_subtable = lookup(var.firewall_local_in_policy, "dynamic_sort_subtable", null) #. Options: [ false, true, natural, alphabetical ]. false: Default value, do not sort tables; true/natural: sort tables in natural order. For example: [ a10, a2 ] --> [ a2, a10 ]; alphabetical: sort tables in alphabetical order. For example: [ a10, a2 ] --> [ a10, a2 ].
	
	dynamic "srcaddr" {
		for_each = var.firewall_local_in_policy.srcaddr
		content {
			name = srcaddr.value
		}
	}

	dynamic "dstaddr" {
		for_each = var.firewall_local_in_policy.dstaddr
		content {
			name = dstaddr.value
		}
	}

    dynamic "service" {
		for_each = var.firewall_local_in_policy.service
		content {
			name = service.value
		}
  }

  # vdomparam - Specifies the vdom to which the resource will be applied when the FortiGate unit is running in VDOM mode. Only one vdom can be specified. If you want to inherit the vdom configuration of the provider, please do not set this parameter.

}