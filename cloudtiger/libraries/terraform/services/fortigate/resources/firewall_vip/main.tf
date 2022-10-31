terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_vip" "trname" {
  name                             = var.firewall_vip.name
  color                            = var.firewall_vip.color
  extintf                          = var.firewall_vip.extintf
  extip                            = var.firewall_vip.extip
  extport                          = var.firewall_vip.extport
  comment                          = var.firewall_vip.comment
  type                             = var.firewall_vip.type
  arp_reply                        = lookup(var.firewall_vip, "arp_reply", null)
  dns_mapping_ttl                  = lookup(var.firewall_vip, "dns_mapping_ttl", null)
  fosid                            = lookup(var.firewall_vip, "fosid", null)
  http_cookie_age                  = lookup(var.firewall_vip, "http_cookie_age", null)
  http_cookie_domain_from_host     = lookup(var.firewall_vip, "http_cookie_domain_from_host", null)
  http_cookie_generation           = lookup(var.firewall_vip, "http_cookie_generation", null)
  http_cookie_share                = lookup(var.firewall_vip, "http_cookie_share", null)
  http_ip_header                   = lookup(var.firewall_vip, "http_ip_header", null)
  http_multiplex                   = lookup(var.firewall_vip, "http_multiplex", null)
  https_cookie_secure              = lookup(var.firewall_vip, "https_cookie_secure", null)
  ldb_method                       = lookup(var.firewall_vip, "ldb_method", null)
  mappedport                       = lookup(var.firewall_vip, "mappedport", null)
  max_embryonic_connections        = lookup(var.firewall_vip, "max_embryonic_connections", null)
  nat_source_vip                   = lookup(var.firewall_vip, "nat_source_vip", null)
  outlook_web_access               = lookup(var.firewall_vip, "outlook_web_access", null)
  persistence                      = lookup(var.firewall_vip, "persistence", null)
  portforward                      = lookup(var.firewall_vip, "portforward", null)
  portmapping_type                 = lookup(var.firewall_vip, "portmapping_type", null)
  protocol                         = lookup(var.firewall_vip, "protocol", null)
  ssl_algorithm                    = lookup(var.firewall_vip, "ssl_algorithm", null)
  ssl_client_fallback              = lookup(var.firewall_vip, "ssl_client_fallback", null)
  ssl_client_renegotiation         = lookup(var.firewall_vip, "ssl_client_renegotiation", null)
  ssl_client_session_state_max     = lookup(var.firewall_vip, "ssl_client_session_state_max", null)
  ssl_client_session_state_timeout = lookup(var.firewall_vip, "ssl_client_session_state_timeout", null)
  ssl_client_session_state_type    = lookup(var.firewall_vip, "ssl_client_session_state_type", null)
  ssl_dh_bits                      = lookup(var.firewall_vip, "ssl_dh_bits", null)
  ssl_hpkp                         = lookup(var.firewall_vip, "ssl_hpkp", null)
  ssl_hpkp_age                     = lookup(var.firewall_vip, "ssl_hpkp_age", null)
  ssl_hpkp_include_subdomains      = lookup(var.firewall_vip, "ssl_hpkp_include_subdomains", null)
  ssl_hsts                         = lookup(var.firewall_vip, "ssl_hsts", null)
  ssl_hsts_age                     = lookup(var.firewall_vip, "ssl_hsts_age", null)
  ssl_hsts_include_subdomains      = lookup(var.firewall_vip, "ssl_hsts_include_subdomains", null)
  ssl_http_location_conversion     = lookup(var.firewall_vip, "ssl_http_location_conversion", null)
  ssl_http_match_host              = lookup(var.firewall_vip, "ssl_http_match_host", null)
  ssl_max_version                  = lookup(var.firewall_vip, "ssl_max_version", null)
  ssl_min_version                  = lookup(var.firewall_vip, "ssl_min_version", null)
  ssl_mode                         = lookup(var.firewall_vip, "ssl_mode", null)
  ssl_pfs                          = lookup(var.firewall_vip, "ssl_pfs", null)
  ssl_send_empty_frags             = lookup(var.firewall_vip, "ssl_send_empty_frags", null)
  ssl_server_algorithm             = lookup(var.firewall_vip, "ssl_server_algorithm", null)
  ssl_server_max_version           = lookup(var.firewall_vip, "ssl_server_max_version", null)
  ssl_server_min_version           = lookup(var.firewall_vip, "ssl_server_min_version", null)
  ssl_server_session_state_max     = lookup(var.firewall_vip, "ssl_server_session_state_max", null)
  ssl_server_session_state_timeout = lookup(var.firewall_vip, "ssl_server_session_state_timeout", null)
  ssl_server_session_state_type    = lookup(var.firewall_vip, "ssl_server_session_state_type", null)
  weblogic_server                  = lookup(var.firewall_vip, "weblogic_server", null)
  websphere_server                 = lookup(var.firewall_vip, "websphere_server", null)

  # dynamic "mappedip" {
  #   content {
  #       range = mappedip.value["mappedip"]
  #   }
  # }
}