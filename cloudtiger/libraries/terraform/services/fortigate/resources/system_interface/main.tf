terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_system_interface" "trname" {
  algorithm    = var.system_interface.algorithm
  defaultgw    = var.system_interface.defaultgw
  distance     = var.system_interface.distance
  ip           = var.system_interface.ip
  #mtu          = var.system_interface.mtu
  #mtu_override = var.system_interface.mtu_override
  name         = var.system_interface.name
  type         = var.system_interface.type
  vdom         = var.system_interface.vdom
  mode         = var.system_interface.mode
  #snmp_index   = var.system_interface.snmp_index
  description  = var.system_interface.description
  ipv6 {
    nd_mode = "basic"
  }
}