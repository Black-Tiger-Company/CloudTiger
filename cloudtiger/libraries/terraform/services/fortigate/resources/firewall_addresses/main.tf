terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.13.2"
    }
  }
}

resource "fortios_firewall_address" "trname" {
  for_each            = var.firewall_address
  name                 = var.firewall_address[each.key].name
  allow_routing        = var.firewall_address[each.key].allow_routing
  color                = var.firewall_address[each.key].color
  type                 = var.firewall_address[each.key].type
  subnet               = var.firewall_address[each.key].subnet
  fqdn                 = var.firewall_address[each.key].fqdn
  associated_interface = var.firewall_address[each.key].associated_interface
  end_ip               = var.firewall_address[each.key].end_ip
  start_ip             = var.firewall_address[each.key].start_ip
  uuid                 = var.firewall_address[each.key].uuid
  visibility           = var.firewall_address[each.key].visibility
}