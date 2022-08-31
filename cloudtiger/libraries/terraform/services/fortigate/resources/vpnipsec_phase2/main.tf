terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_vpnipsec_phase2" "trnamex2" {
  name  = lookup(var.vpnipsec_phase2, "name ", null )
  phase1name  = lookup(var.vpnipsec_phase2, "phase1name ", null )
  dhcp_ipsec  = lookup(var.vpnipsec_phase2, "dhcp_ipsec ", null ) # Valid values: enable, disable
  use_natip  = lookup(var.vpnipsec_phase2, "use_natip ", null ) # Valid values: enable, disable
  selector_match  = lookup(var.vpnipsec_phase2, "selector_match ", null ) # Valid values: exact, subset, auto
  proposal  = lookup(var.vpnipsec_phase2, "proposal ", null ) # Valid values: null-md5, null-sha1, null-sha256, null-sha384, null-sha512, des-null, des-md5, des-sha1, des-sha256, des-sha384, des-sha512, 3des-null, 3des-md5, 3des-sha1, 3des-sha256, 3des-sha384, 3des-sha512, aes128-null, aes128-md5, aes128-sha1, aes128-sha256, aes128-sha384, aes128-sha512, aes128gcm, aes192-null, aes192-md5, aes192-sha1, aes192-sha256, aes192-sha384, aes192-sha512, aes256-null, aes256-md5, aes256-sha1, aes256-sha256, aes256-sha384, aes256-sha512, aes256gcm, chacha20poly1305, aria128-null, aria128-md5, aria128-sha1, aria128-sha256, aria128-sha384, aria128-sha512, aria192-null, aria192-md5, aria192-sha1, aria192-sha256, aria192-sha384, aria192-sha512, aria256-null, aria256-md5, aria256-sha1, aria256-sha256, aria256-sha384, aria256-sha512, seed-null, seed-md5, seed-sha1, seed-sha256, seed-sha384, seed-sha512
  pfs  = lookup(var.vpnipsec_phase2, "pfs ", null ) # Valid values: enable, disable
  ipv4_df  = lookup(var.vpnipsec_phase2, "ipv4_df ", null ) # Valid values: enable, disable
  dhgrp  = lookup(var.vpnipsec_phase2, "dhgrp ", null ) # Valid values: 1, 2, 5, 14, 15, 16, 17, 18, 19, 20, 21, 27, 28, 29, 30, 31, 32
  replay  = lookup(var.vpnipsec_phase2, "replay ", null ) # Valid values: enable, disable
  keepalive  = lookup(var.vpnipsec_phase2, "keepalive ", null ) # Valid values: enable, disable
  auto_negotiate  = lookup(var.vpnipsec_phase2, "auto_negotiate ", null ) # Valid values: enable, disable
  add_route  = lookup(var.vpnipsec_phase2, "add_route ", null ) # Valid values: phase1, enable, disable
  inbound_dscp_copy  = lookup(var.vpnipsec_phase2, "inbound_dscp_copy ", null ) # Valid values: phase1, enable, disable
  keylifeseconds  = lookup(var.vpnipsec_phase2, "keylifeseconds ", null )
  keylifekbs  = lookup(var.vpnipsec_phase2, "keylifekbs ", null )
  keylife_type  = lookup(var.vpnipsec_phase2, "keylife_type ", null ) # Valid values: seconds, kbs, both
  single_source  = lookup(var.vpnipsec_phase2, "single_source ", null ) # Valid values: enable, disable
  route_overlap  = lookup(var.vpnipsec_phase2, "route_overlap ", null ) # Valid values: use-old, use-new, allow
  encapsulation  = lookup(var.vpnipsec_phase2, "encapsulation ", null ) # Valid values: tunnel-mode, transport-mode
  l2tp  = lookup(var.vpnipsec_phase2, "l2tp ", null ) # Valid values: enable, disable
  comments  = lookup(var.vpnipsec_phase2, "comments ", null )
  initiator_ts_narrow  = lookup(var.vpnipsec_phase2, "initiator_ts_narrow ", null ) # Valid values: enable, disable
  diffserv  = lookup(var.vpnipsec_phase2, "diffserv ", null ) # Valid values: enable, disable
  diffservcode  = lookup(var.vpnipsec_phase2, "diffservcode ", null )
  protocol  = lookup(var.vpnipsec_phase2, "protocol ", null )
  src_name  = lookup(var.vpnipsec_phase2, "src_name ", null )
  src_name6  = lookup(var.vpnipsec_phase2, "src_name6 ", null )
  src_addr_type  = lookup(var.vpnipsec_phase2, "src_addr_type ", null ) # Valid values: subnet, range, ip, name
  src_start_ip  = lookup(var.vpnipsec_phase2, "src_start_ip ", null )
  src_start_ip6  = lookup(var.vpnipsec_phase2, "src_start_ip6 ", null )
  src_end_ip  = lookup(var.vpnipsec_phase2, "src_end_ip ", null )
  src_end_ip6  = lookup(var.vpnipsec_phase2, "src_end_ip6 ", null )
  src_subnet  = lookup(var.vpnipsec_phase2, "src_subnet ", null )
  src_subnet6  = lookup(var.vpnipsec_phase2, "src_subnet6 ", null )
  src_port  = lookup(var.vpnipsec_phase2, "src_port ", null )
  dst_name  = lookup(var.vpnipsec_phase2, "dst_name ", null )
  dst_name6  = lookup(var.vpnipsec_phase2, "dst_name6 ", null )
  dst_addr_type  = lookup(var.vpnipsec_phase2, "dst_addr_type ", null ) # Valid values: subnet, range, ip, name
  dst_start_ip  = lookup(var.vpnipsec_phase2, "dst_start_ip ", null )
  dst_start_ip6  = lookup(var.vpnipsec_phase2, "dst_start_ip6 ", null )
  dst_end_ip  = lookup(var.vpnipsec_phase2, "dst_end_ip ", null )
  dst_end_ip6  = lookup(var.vpnipsec_phase2, "dst_end_ip6 ", null )
  dst_subnet  = lookup(var.vpnipsec_phase2, "dst_subnet ", null )
  dst_subnet6  = lookup(var.vpnipsec_phase2, "dst_subnet6 ", null )
  dst_port  = lookup(var.vpnipsec_phase2, "dst_port ", null )
  vdomparam  = lookup(var.vpnipsec_phase2, "vdomparam ", null )
}