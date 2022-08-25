terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_address" "trname" {
  name                 = var.firewall_address.name
  allow_routing        = var.firewall_address.allow_routing
  color                = var.firewall_address.color
  type                 = var.firewall_address.type
  subnet               = var.firewall_address.subnet
  fqdn                 = var.firewall_address.fqdn
  associated_interface = var.firewall_address.associated_interface
  end_ip               = var.firewall_address.end_ip
  start_ip             = var.firewall_address.start_ip
  uuid                 = var.firewall_address.uuid
  visibility           = var.firewall_address.visibility
}