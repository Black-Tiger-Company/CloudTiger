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
#   arp_reply                        = "enable"
#   dns_mapping_ttl                  = 0
#   fosid                            = 0
#   http_cookie_age                  = 60
#   http_cookie_domain_from_host     = "disable"
#   http_cookie_generation           = 0
#   http_cookie_share                = "same-ip"
#   http_ip_header                   = "disable"
#   http_multiplex                   = "disable"
#   https_cookie_secure              = "disable"
#   ldb_method                       = "static"
#   mappedport                       = "0-65535"
#   max_embryonic_connections        = 1000
#   nat_source_vip                   = "disable"
#   outlook_web_access               = "disable"
#   persistence                      = "none"
#   portforward                      = "disable"
#   portmapping_type                 = "1-to-1"
#   protocol                         = "tcp"
#   ssl_algorithm                    = "high"
#   ssl_client_fallback              = "enable"
#   ssl_client_renegotiation         = "secure"
#   ssl_client_session_state_max     = 1000
#   ssl_client_session_state_timeout = 30
#   ssl_client_session_state_type    = "both"
#   ssl_dh_bits                      = "2048"
#   ssl_hpkp                         = "disable"
#   ssl_hpkp_age                     = 5184000
#   ssl_hpkp_include_subdomains      = "disable"
#   ssl_hsts                         = "disable"
#   ssl_hsts_age                     = 5184000
#   ssl_hsts_include_subdomains      = "disable"
#   ssl_http_location_conversion     = "disable"
#   ssl_http_match_host              = "enable"
#   ssl_max_version                  = "tls-1.2"
#   ssl_min_version                  = "tls-1.1"
#   ssl_mode                         = "half"
#   ssl_pfs                          = "require"
#   ssl_send_empty_frags             = "enable"
#   ssl_server_algorithm             = "client"
#   ssl_server_max_version           = "client"
#   ssl_server_min_version           = "client"
#   ssl_server_session_state_max     = 100
#   ssl_server_session_state_timeout = 60
#   ssl_server_session_state_type    = "both"
#   weblogic_server                  = "disable"
#   websphere_server                 = "disable"

  dynamic "mappedip" {
    content {
        range = mappedip.value["mappedip"]
    }
  }
}