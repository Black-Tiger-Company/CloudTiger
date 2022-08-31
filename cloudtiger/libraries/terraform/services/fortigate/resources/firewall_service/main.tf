terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewallservice_custom" "trname" {
  app_service_type    = var.firewall_service.app_service_type
  category            = var.firewall_service.category
  check_reset_range   = var.firewall_service.check_reset_range
  color               = var.firewall_service.color
  helper              = var.firewall_service.helper
  iprange             = var.firewall_service.iprange
  name                = var.firewall_service.name
  protocol            = var.firewall_service.protocol
  protocol_number     = var.firewall_service.protocol_number
  proxy               = var.firewall_service.proxy
  tcp_halfclose_timer = var.firewall_service.tcp_halfclose_timer
  tcp_halfopen_timer  = var.firewall_service.tcp_halfopen_timer
  tcp_portrange       = var.firewall_service.tcp_portrange
  tcp_timewait_timer  = var.firewall_service.tcp_timewait_timer
  udp_idle_timer      = var.firewall_service.udp_idle_timer
  visibility          = var.firewall_service.visibility
}