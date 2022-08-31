terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_vpnssl_settings" "trnamex2" {
  status  = lookup(var.vpnssl_settings, "status ", null ) # Valid values: enable, disable
  reqclientcert  = lookup(var.vpnssl_settings, "reqclientcert ", null ) # Valid values: enable, disable
  user_peer  = lookup(var.vpnssl_settings, "user_peer ", null )
  ssl_max_proto_ver  = lookup(var.vpnssl_settings, "ssl_max_proto_ver ", null ) # Valid values: tls1-0, tls1-1, tls1-2, tls1-3
  ssl_min_proto_ver  = lookup(var.vpnssl_settings, "ssl_min_proto_ver ", null ) # Valid values: tls1-0, tls1-1, tls1-2, tls1-3
  tlsv1_0  = lookup(var.vpnssl_settings, "tlsv1_0 ", null ) # Valid values: enable, disable
  tlsv1_1  = lookup(var.vpnssl_settings, "tlsv1_1 ", null ) # Valid values: enable, disable
  tlsv1_2  = lookup(var.vpnssl_settings, "tlsv1_2 ", null ) # Valid values: enable, disable
  tlsv1_3  = lookup(var.vpnssl_settings, "tlsv1_3 ", null ) # Valid values: enable, disable
  banned_cipher  = lookup(var.vpnssl_settings, "banned_cipher ", null )
  ciphersuite  = lookup(var.vpnssl_settings, "ciphersuite ", null ) # Valid values: TLS-AES-128-GCM-SHA256, TLS-AES-256-GCM-SHA384, TLS-CHACHA20-POLY1305-SHA256, TLS-AES-128-CCM-SHA256, TLS-AES-128-CCM-8-SHA256
  ssl_insert_empty_fragment  = lookup(var.vpnssl_settings, "ssl_insert_empty_fragment ", null ) # Valid values: enable, disable
  https_redirect  = lookup(var.vpnssl_settings, "https_redirect ", null ) # Valid values: enable, disable
  x_content_type_options  = lookup(var.vpnssl_settings, "x_content_type_options ", null ) # Valid values: enable, disable
  ssl_client_renegotiation  = lookup(var.vpnssl_settings, "ssl_client_renegotiation ", null ) # Valid values: disable, enable
  force_two_factor_auth  = lookup(var.vpnssl_settings, "force_two_factor_auth ", null ) # Valid values: enable, disable
  unsafe_legacy_renegotiation  = lookup(var.vpnssl_settings, "unsafe_legacy_renegotiation ", null ) # Valid values: enable, disable
  servercert  = lookup(var.vpnssl_settings, "servercert ", null )
  algorithm  = lookup(var.vpnssl_settings, "algorithm ", null ) # Valid values: high, medium, default, low
  idle_timeout  = lookup(var.vpnssl_settings, "idle_timeout ", null )
  auth_timeout  = lookup(var.vpnssl_settings, "auth_timeout ", null )
  login_attempt_limit  = lookup(var.vpnssl_settings, "login_attempt_limit ", null )
  login_block_time  = lookup(var.vpnssl_settings, "login_block_time ", null )
  login_timeout  = lookup(var.vpnssl_settings, "login_timeout ", null )
  dtls_hello_timeout  = lookup(var.vpnssl_settings, "dtls_hello_timeout ", null )
  # tunnel_ip_pools  = lookup(var.vpnssl_settings, "tunnel_ip_pools ", null )
  # tunnel_ipv6_pools  = lookup(var.vpnssl_settings, "tunnel_ipv6_pools ", null )
  dns_suffix  = lookup(var.vpnssl_settings, "dns_suffix ", null )
  dns_server1  = lookup(var.vpnssl_settings, "dns_server1 ", null )
  dns_server2  = lookup(var.vpnssl_settings, "dns_server2 ", null )
  wins_server1  = lookup(var.vpnssl_settings, "wins_server1 ", null )
  wins_server2  = lookup(var.vpnssl_settings, "wins_server2 ", null )
  ipv6_dns_server1  = lookup(var.vpnssl_settings, "ipv6_dns_server1 ", null )
  ipv6_dns_server2  = lookup(var.vpnssl_settings, "ipv6_dns_server2 ", null )
  ipv6_wins_server1  = lookup(var.vpnssl_settings, "ipv6_wins_server1 ", null )
  ipv6_wins_server2  = lookup(var.vpnssl_settings, "ipv6_wins_server2 ", null )
  route_source_interface  = lookup(var.vpnssl_settings, "route_source_interface ", null ) # Valid values: enable, disable
  url_obscuration  = lookup(var.vpnssl_settings, "url_obscuration ", null ) # Valid values: enable, disable
  http_compression  = lookup(var.vpnssl_settings, "http_compression ", null ) # Valid values: enable, disable
  http_only_cookie  = lookup(var.vpnssl_settings, "http_only_cookie ", null ) # Valid values: enable, disable
  deflate_compression_level  = lookup(var.vpnssl_settings, "deflate_compression_level ", null )
  deflate_min_data_size  = lookup(var.vpnssl_settings, "deflate_min_data_size ", null )
  port  = lookup(var.vpnssl_settings, "port ", null )
  port_precedence  = lookup(var.vpnssl_settings, "port_precedence ", null ) # Valid values: enable, disable
  auto_tunnel_static_route  = lookup(var.vpnssl_settings, "auto_tunnel_static_route ", null ) # Valid values: enable, disable
  header_x_forwarded_for  = lookup(var.vpnssl_settings, "header_x_forwarded_for ", null ) # Valid values: pass, add, remove
  # source_interface  = lookup(var.vpnssl_settings, "source_interface ", null )
  # source_address  = lookup(var.vpnssl_settings, "source_address ", null )
  source_address_negate  = lookup(var.vpnssl_settings, "source_address_negate ", null ) # Valid values: enable, disable
  # source_address6  = lookup(var.vpnssl_settings, "source_address6 ", null )
  source_address6_negate  = lookup(var.vpnssl_settings, "source_address6_negate ", null ) # Valid values: enable, disable
  default_portal  = lookup(var.vpnssl_settings, "default_portal ", null )
  # authentication_rule  = lookup(var.vpnssl_settings, "authentication_rule ", null )
  browser_language_detection  = lookup(var.vpnssl_settings, "browser_language_detection ", null ) # Valid values: enable, disable
  dtls_tunnel  = lookup(var.vpnssl_settings, "dtls_tunnel ", null ) # Valid values: enable, disable
  dtls_max_proto_ver  = lookup(var.vpnssl_settings, "dtls_max_proto_ver ", null ) # Valid values: dtls1-0, dtls1-2
  dtls_min_proto_ver  = lookup(var.vpnssl_settings, "dtls_min_proto_ver ", null ) # Valid values: dtls1-0, dtls1-2
  check_referer  = lookup(var.vpnssl_settings, "check_referer ", null ) # Valid values: enable, disable
  http_request_header_timeout  = lookup(var.vpnssl_settings, "http_request_header_timeout ", null )
  http_request_body_timeout  = lookup(var.vpnssl_settings, "http_request_body_timeout ", null )
  auth_session_check_source_ip  = lookup(var.vpnssl_settings, "auth_session_check_source_ip ", null ) # Valid values: enable, disable
  tunnel_connect_without_reauth  = lookup(var.vpnssl_settings, "tunnel_connect_without_reauth ", null ) # Valid values: enable, disable
  tunnel_user_session_timeout  = lookup(var.vpnssl_settings, "tunnel_user_session_timeout ", null )
  hsts_include_subdomains  = lookup(var.vpnssl_settings, "hsts_include_subdomains ", null ) # Valid values: enable, disable
  transform_backward_slashes  = lookup(var.vpnssl_settings, "transform_backward_slashes ", null ) # Valid values: enable, disable
  encode_2f_sequence  = lookup(var.vpnssl_settings, "encode_2f_sequence ", null ) # Valid values: enable, disable
  encrypt_and_store_password  = lookup(var.vpnssl_settings, "encrypt_and_store_password ", null ) # Valid values: enable, disable
  client_sigalgs  = lookup(var.vpnssl_settings, "client_sigalgs ", null ) # Valid values: no-rsa-pss, all
  dual_stack_mode  = lookup(var.vpnssl_settings, "dual_stack_mode ", null ) # Valid values: enable, disable
  tunnel_addr_assigned_method  = lookup(var.vpnssl_settings, "tunnel_addr_assigned_method ", null ) # Valid values: first-available, round-robin
  saml_redirect_port  = lookup(var.vpnssl_settings, "saml_redirect_port ", null )
  web_mode_snat  = lookup(var.vpnssl_settings, "web_mode_snat ", null ) # Valid values: enable, disable
  dynamic_sort_subtable  = lookup(var.vpnssl_settings, "dynamic_sort_subtable ", null )
  vdomparam  = lookup(var.vpnssl_settings, "vdomparam ", null )

}