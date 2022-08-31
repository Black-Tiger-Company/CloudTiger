terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewallservice_group" "trname" {
  color = var.firewall_service_group.color
  name  = var.firewall_service_group.name
  proxy = var.firewall_service_group.proxy

  dynamic "member" {
    for_each = var.firewall_service_group.member
    content {
      name = "test"
    }
  }
}