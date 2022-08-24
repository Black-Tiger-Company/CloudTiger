terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.13.2"
    }
  }
}

resource "fortios_firewall_policy" "trname" {
  for_each = var.firewall_policy
  action             = var.firewall_policy[each.key].action
  name               = var.firewall_policy[each.key].name
  policyid           = var.firewall_policy[each.key].policyid
  schedule           = var.firewall_policy[each.key].schedule
  inspection_mode    = var.firewall_policy[each.key].inspection_mode
  nat                = var.firewall_policy[each.key].nat
  dynamic_sort_subtable = var.firewall_policy[each.key].dynamic_sort_subtable
  srcaddr {
    name = var.firewall_policy[each.key].srcaddr_name
  }

  dstaddr {
    name = var.firewall_policy[each.key].dstaddr_name
  }

  srcintf {
    name = var.firewall_policy[each.key].scrintf_name
  }

  dstintf {
    name = var.firewall_policy[each.key].dstintf_name
  }

  service {
    name = var.firewall_policy[each.key].service_name
  }
}