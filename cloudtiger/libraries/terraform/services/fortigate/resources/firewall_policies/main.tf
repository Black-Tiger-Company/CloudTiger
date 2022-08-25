terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_policy" "trname" {
  action             = var.firewall_policy.action
  name               = var.firewall_policy.name
  policyid           = var.firewall_policy.policyid
  schedule           = var.firewall_policy.schedule
  inspection_mode    = var.firewall_policy.inspection_mode
  nat                = var.firewall_policy.nat
  dynamic_sort_subtable = var.firewall_policy.dynamic_sort_subtable
  srcaddr {
    name = var.firewall_policy.srcaddr_name
  }

  dstaddr {
    name = var.firewall_policy.dstaddr_name
  }

  srcintf {
    name = var.firewall_policy.scrintf_name
  }

  dstintf {
    name = var.firewall_policy.dstintf_name
  }

  service {
    name = var.firewall_policy.service_name
  }
}