terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_vpnipsec_phase2interface" "trnamex1" {
  name  = lookup(var.vpnipsec_phase2interface, "name ", null )
  phase1name  = lookup(var.vpnipsec_phase2interface, "phase1name ", null )
  dhcp_ipsec  = lookup(var.vpnipsec_phase2interface, "dhcp_ipsec ", null ) # Valid values: enable, disable
  proposal  = lookup(var.vpnipsec_phase2interface, "proposal ", null ) # Valid values: null-md5, null-sha1, null-sha256, null-sha384, null-sha512, des-null, des-md5, des-sha1, des-sha256, des-sha384, des-sha512, 3des-null, 3des-md5, 3des-sha1, 3des-sha256, 3des-sha384, 3des-sha512, aes128-null, aes128-md5, aes128-sha1, aes128-sha256, aes128-sha384, aes128-sha512, aes128gcm, aes192-null, aes192-md5, aes192-sha1, aes192-sha256, aes192-sha384, aes192-sha512, aes256-null, aes256-md5, aes256-sha1, aes256-sha256, aes256-sha384, aes256-sha512, aes256gcm, chacha20poly1305, aria128-null, aria128-md5, aria128-sha1, aria128-sha256, aria128-sha384, aria128-sha512, aria192-null, aria192-md5, aria192-sha1, aria192-sha256, aria192-sha384, aria192-sha512, aria256-null, aria256-md5, aria256-sha1, aria256-sha256, aria256-sha384, aria256-sha512, seed-null, seed-md5, seed-sha1, seed-sha256, seed-sha384, seed-sha512
  pfs  = lookup(var.vpnipsec_phase2interface, "pfs ", null ) # Valid values: enable, disable
  ipv4_df  = lookup(var.vpnipsec_phase2interface, "ipv4_df ", null ) # Valid values: enable, disable
  dhgrp  = lookup(var.vpnipsec_phase2interface, "dhgrp ", null ) # Valid values: 1, 2, 5, 14, 15, 16, 17, 18, 19, 20, 21, 27, 28, 29, 30, 31, 32
  replay  = lookup(var.vpnipsec_phase2interface, "replay ", null ) # Valid values: enable, disable
  keepalive  = lookup(var.vpnipsec_phase2interface, "keepalive ", null ) # Valid values: enable, disable
  auto_negotiate  = lookup(var.vpnipsec_phase2interface, "auto_negotiate ", null ) # Valid values: enable, disable
  add_route  = lookup(var.vpnipsec_phase2interface, "add_route ", null ) # Valid values: phase1, enable, disable
  inbound_dscp_copy  = lookup(var.vpnipsec_phase2interface, "inbound_dscp_copy ", null ) # Valid values: phase1, enable, disable
  auto_discovery_sender  = lookup(var.vpnipsec_phase2interface, "auto_discovery_sender ", null ) # Valid values: phase1, enable, disable
  auto_discovery_forwarder  = lookup(var.vpnipsec_phase2interface, "auto_discovery_forwarder ", null ) # Valid values: phase1, enable, disable
  keylifeseconds  = lookup(var.vpnipsec_phase2interface, "keylifeseconds ", null )
  keylifekbs  = lookup(var.vpnipsec_phase2interface, "keylifekbs ", null )
  keylife_type  = lookup(var.vpnipsec_phase2interface, "keylife_type ", null ) # Valid values: seconds, kbs, both
  single_source  = lookup(var.vpnipsec_phase2interface, "single_source ", null ) # Valid values: enable, disable
  route_overlap  = lookup(var.vpnipsec_phase2interface, "route_overlap ", null ) # Valid values: use-old, use-new, allow
  encapsulation  = lookup(var.vpnipsec_phase2interface, "encapsulation ", null ) # Valid values: tunnel-mode, transport-mode
  l2tp  = lookup(var.vpnipsec_phase2interface, "l2tp ", null ) # Valid values: enable, disable
  comments  = lookup(var.vpnipsec_phase2interface, "comments ", null )
  initiator_ts_narrow  = lookup(var.vpnipsec_phase2interface, "initiator_ts_narrow ", null ) # Valid values: enable, disable
  diffserv  = lookup(var.vpnipsec_phase2interface, "diffserv ", null ) # Valid values: enable, disable
  diffservcode  = lookup(var.vpnipsec_phase2interface, "diffservcode ", null )
  protocol  = lookup(var.vpnipsec_phase2interface, "protocol ", null )
  src_name  = lookup(var.vpnipsec_phase2interface, "src_name ", null )
  src_name6  = lookup(var.vpnipsec_phase2interface, "src_name6 ", null )
  src_addr_type  = lookup(var.vpnipsec_phase2interface, "src_addr_type ", null ) # Valid values: subnet, range, ip, name, subnet6, range6, ip6, name6
  src_start_ip  = lookup(var.vpnipsec_phase2interface, "src_start_ip ", null )
  src_start_ip6  = lookup(var.vpnipsec_phase2interface, "src_start_ip6 ", null )
  src_end_ip  = lookup(var.vpnipsec_phase2interface, "src_end_ip ", null )
  src_end_ip6  = lookup(var.vpnipsec_phase2interface, "src_end_ip6 ", null )
  src_subnet  = lookup(var.vpnipsec_phase2interface, "src_subnet ", null )
  src_subnet6  = lookup(var.vpnipsec_phase2interface, "src_subnet6 ", null )
  src_port  = lookup(var.vpnipsec_phase2interface, "src_port ", null )
  dst_name  = lookup(var.vpnipsec_phase2interface, "dst_name ", null )
  dst_name6  = lookup(var.vpnipsec_phase2interface, "dst_name6 ", null )
  dst_addr_type  = lookup(var.vpnipsec_phase2interface, "dst_addr_type ", null ) # Valid values: subnet, range, ip, name, subnet6, range6, ip6, name6
  dst_start_ip  = lookup(var.vpnipsec_phase2interface, "dst_start_ip ", null )
  dst_start_ip6  = lookup(var.vpnipsec_phase2interface, "dst_start_ip6 ", null )
  dst_end_ip  = lookup(var.vpnipsec_phase2interface, "dst_end_ip ", null )
  dst_end_ip6  = lookup(var.vpnipsec_phase2interface, "dst_end_ip6 ", null )
  dst_subnet  = lookup(var.vpnipsec_phase2interface, "dst_subnet ", null )
  dst_subnet6  = lookup(var.vpnipsec_phase2interface, "dst_subnet6 ", null )
  dst_port  = lookup(var.vpnipsec_phase2interface, "dst_port ", null )
  vdomparam  = lookup(var.vpnipsec_phase2interface, "vdomparam ", null )

}