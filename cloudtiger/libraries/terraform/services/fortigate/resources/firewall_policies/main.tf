terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_firewall_policy" "trname" {
  action             = lookup(var.firewall_policy, "action", null) # Valid values: accept, deny, ipsec
  name               = var.firewall_policy.name
  policyid           = var.firewall_policy.policyid
  inspection_mode    = var.firewall_policy.inspection_mode
  nat                = var.firewall_policy.nat
  dynamic_sort_subtable = var.firewall_policy.dynamic_sort_subtable

  uuid = lookup(var.firewall_policy, "uuid", null)
  # srcintf - (Required) Incoming (ingress) interface. The structure of srcintf block is documented below.
  # dstintf - (Required) Outgoing (egress) interface. The structure of dstintf block is documented below.
  # srcaddr - Source address and address group names. The structure of srcaddr block is documented below.
  # dstaddr - Destination address and address group names. The structure of dstaddr block is documented below.
  # srcaddr6 - Source IPv6 address name and address group names. The structure of srcaddr6 block is documented below.
  # dstaddr6 - Destination IPv6 address name and address group names. The structure of dstaddr6 block is documented below.
  ztna_status = lookup(var.firewall_policy, "uuid", null) # Valid values: enable, disable.
  # ztna_ems_tag - Source ztna-ems-tag names. The structure of ztna_ems_tag block is documented below.
  # ztna_geo_tag - Source ztna-geo-tag names. The structure of ztna_geo_tag block is documented below.
  internet_service = lookup(var.firewall_policy, "uuid", null) # Valid values: enable, disable.
  # internet_service_name - Internet Service name. The structure of internet_service_name block is documented below.
  # internet_service_id - Internet Service ID. The structure of internet_service_id block is documented below.
  # internet_service_group - Internet Service group name. The structure of internet_service_group block is documented below.
  # internet_service_custom - Custom Internet Service name. The structure of internet_service_custom block is documented below.
  # internet_service_custom_group - Custom Internet Service group name. The structure of internet_service_custom_group block is documented below.
  internet_service_src = lookup(var.firewall_policy, "internet_service_src", null) # Valid values: enable, disable.
  # internet_service_src_name - Internet Service source name. The structure of internet_service_src_name block is documented below.
  # internet_service_src_id - Internet Service source ID. The structure of internet_service_src_id block is documented below.
  # internet_service_src_group - Internet Service source group name. The structure of internet_service_src_group block is documented below.
  # internet_service_src_custom - Custom Internet Service source name. The structure of internet_service_src_custom block is documented below.
  # internet_service_src_custom_group - Custom Internet Service source group name. The structure of internet_service_src_custom_group block is documented below.
  reputation_minimum = lookup(var.firewall_policy, "reputation_minimum", null)
  reputation_direction = lookup(var.firewall_policy, "reputation_direction", null) # Valid values: source, destination.
  #src_vendor_mac - Vendor MAC source ID. The structure of src_vendor_mac block is documented below.
  rtp_nat = lookup(var.firewall_policy, "rtp_nat", null) # Valid values: disable, enable.
  #rtp_addr - Address names if this is an RTP NAT policy. The structure of rtp_addr block is documented below.
  learning_mode = lookup(var.firewall_policy, "learning_mode", null) # Valid values: enable, disable.
  nat64 = lookup(var.firewall_policy, "nat64", null) # Valid values: enable, disable.
  nat46 = lookup(var.firewall_policy, "nat46", null) # Valid values: enable, disable.
  send_deny_packet = lookup(var.firewall_policy, "firewall_session_dirty", null) # Valid values: disable, enable.
  firewall_session_dirty = lookup(var.firewall_policy, "internet_service_src", null) # Valid values: check-all, check-new.
  status = lookup(var.firewall_policy, "status", null) # Valid values: enable, disable.
  schedule = lookup(var.firewall_policy, "schedule", null) #Default is always)
  schedule_timeout = lookup(var.firewall_policy, "schedule_timeout", null) #  Valid values: enable, disable.
  policy_expiry = lookup(var.firewall_policy, "policy_expiry", null) # Valid values: enable, disable.
  policy_expiry_date = lookup(var.firewall_policy, "policy_expiry_date", null)

  # tos - ToS (Type of Service) value used for comparison.
  # tos_mask - Non-zero bit positions are used for comparison while zero bit positions are ignored.
  # tos_negate - Enable negated TOS match. Valid values: enable, disable.
  # anti_replay - Enable/disable anti-replay check. Valid values: enable, disable.
  # tcp_session_without_syn - Enable/disable creation of TCP session without SYN flag. Valid values: all, data-only, disable.
  # geoip_anycast - Enable/disable recognition of anycast IP addresses using the geography IP database. Valid values: enable, disable.
  # geoip_match - Match geography address based either on its physical location or registered location. Valid values: physical-location, registered-location.
  # dynamic_shaping - Enable/disable dynamic RADIUS defined traffic shaping. Valid values: enable, disable.
  # passive_wan_health_measurement - Enable/disable passive WAN health measurement. When enabled, auto-asic-offload is disabled. Valid values: enable, disable.
  # utm_status - Enable to add one or more security profiles (AV, IPS, etc.) to the firewall policy. Valid values: enable, disable.
  # inspection_mode - Policy inspection mode (Flow/proxy). Default is Flow mode. Valid values: proxy, flow.
  # http_policy_redirect - Redirect HTTP(S) traffic to matching transparent web proxy policy. Valid values: enable, disable.
  # ssh_policy_redirect - Redirect SSH traffic to matching transparent proxy policy. Valid values: enable, disable.
  # webproxy_profile - Webproxy profile name.
  # profile_type - Determine whether the firewall policy allows security profile groups or single profiles only. Valid values: single, group.
  # profile_group - Name of profile group.
  # av_profile - Name of an existing Antivirus profile.
  # webfilter_profile - Name of an existing Web filter profile.
  # dnsfilter_profile - Name of an existing DNS filter profile.
  # emailfilter_profile - Name of an existing email filter profile.
  # dlp_profile - Name of an existing DLP profile.
  # spamfilter_profile - Name of an existing Spam filter profile.
  # dlp_sensor - Name of an existing DLP sensor.
  # file_filter_profile - Name of an existing file-filter profile.
  # ips_sensor - Name of an existing IPS sensor.
  # application_list - Name of an existing Application list.
  # voip_profile - Name of an existing VoIP profile.
  # sctp_filter_profile - Name of an existing SCTP filter profile.
  # icap_profile - Name of an existing ICAP profile.
  # cifs_profile - Name of an existing CIFS profile.
  # videofilter_profile - Name of an existing VideoFilter profile.
  # waf_profile - Name of an existing Web application firewall profile.
  # ssh_filter_profile - Name of an existing SSH filter profile.
  # profile_protocol_options - Name of an existing Protocol options profile.
  # ssl_ssh_profile - Name of an existing SSL SSH profile.
  # logtraffic - Enable or disable logging. Log all sessions or security profile sessions. Valid values: all, utm, disable.
  # logtraffic_start - Record logs when a session starts. Valid values: enable, disable.
  # capture_packet - Enable/disable capture packets. Valid values: enable, disable.
  # auto_asic_offload - Enable/disable policy traffic ASIC offloading. Valid values: enable, disable.
  # np_acceleration - Enable/disable UTM Network Processor acceleration. Valid values: enable, disable.
  # wanopt - Enable/disable WAN optimization. Valid values: enable, disable.
  # wanopt_detection - WAN optimization auto-detection mode. Valid values: active, passive, off.
  # wanopt_passive_opt - WAN optimization passive mode options. This option decides what IP address will be used to connect server. Valid values: default, transparent, non-transparent.
  # wanopt_profile - WAN optimization profile.
  # wanopt_peer - WAN optimization peer.
  # webcache - Enable/disable web cache. Valid values: enable, disable.
  # webcache_https - Enable/disable web cache for HTTPS. Valid values: disable, enable.
  # webproxy_forward_server - Web proxy forward server name.
  # traffic_shaper - Traffic shaper.
  # traffic_shaper_reverse - Reverse traffic shaper.
  # per_ip_shaper - Per-IP traffic shaper.
  # application - Application ID list. The structure of application block is documented below.
  # app_category - Application category ID list. The structure of app_category block is documented below.
  # url_category - URL category ID list. The structure of url_category block is documented below.
  # app_group - Application group names. The structure of app_group block is documented below.
  # nat - Enable/disable source NAT. Valid values: enable, disable.
  # permit_any_host - Accept UDP packets from any host. Valid values: enable, disable.
  # permit_stun_host - Accept UDP packets from any Session Traversal Utilities for NAT (STUN) host. Valid values: enable, disable.
  # fixedport - Enable to prevent source NAT from changing a session's source port. Valid values: enable, disable.
  # ippool - Enable to use IP Pools for source NAT. Valid values: enable, disable.
  # poolname - IP Pool names. The structure of poolname block is documented below.
  # poolname6 - IPv6 pool names. The structure of poolname6 block is documented below.
  # session_ttl - TTL in seconds for sessions accepted by this policy (0 means use the system default session TTL).
  # vlan_cos_fwd - VLAN forward direction user priority: 255 passthrough, 0 lowest, 7 highest.
  # vlan_cos_rev - VLAN reverse direction user priority: 255 passthrough, 0 lowest, 7 highest.
  # inbound - Policy-based IPsec VPN: only traffic from the remote network can initiate a VPN. Valid values: enable, disable.
  # outbound - Policy-based IPsec VPN: only traffic from the internal network can initiate a VPN. Valid values: enable, disable.
  # natinbound - Policy-based IPsec VPN: apply destination NAT to inbound traffic. Valid values: enable, disable.
  # natoutbound - Policy-based IPsec VPN: apply source NAT to outbound traffic. Valid values: enable, disable.
  # fec - Enable/disable Forward Error Correction on traffic matching this policy on a FEC device. Valid values: enable, disable.
  # wccp - Enable/disable forwarding traffic matching this policy to a configured WCCP server. Valid values: enable, disable.
  # ntlm - Enable/disable NTLM authentication. Valid values: enable, disable.
  # ntlm_guest - Enable/disable NTLM guest user access. Valid values: enable, disable.
  # ntlm_enabled_browsers - HTTP-User-Agent value of supported browsers. The structure of ntlm_enabled_browsers block is documented below.
  # fsso - Enable/disable Fortinet Single Sign-On. Valid values: enable, disable.
  # wsso - Enable/disable WiFi Single Sign On (WSSO). Valid values: enable, disable.
  # rsso - Enable/disable RADIUS single sign-on (RSSO). Valid values: enable, disable.
  # fsso_agent_for_ntlm - FSSO agent to use for NTLM authentication.
  # groups - Names of user groups that can authenticate with this policy. The structure of groups block is documented below.
  # users - Names of individual users that can authenticate with this policy. The structure of users block is documented below.
  # fsso_groups - Names of FSSO groups. The structure of fsso_groups block is documented below.
  # devices - Names of devices or device groups that can be matched by the policy. The structure of devices block is documented below.
  # auth_path - Enable/disable authentication-based routing. Valid values: enable, disable.
  # disclaimer - Enable/disable user authentication disclaimer. Valid values: enable, disable.
  # email_collect - Enable/disable email collection. Valid values: enable, disable.
  # vpntunnel - Policy-based IPsec VPN: name of the IPsec VPN Phase 1.
  # natip - Policy-based IPsec VPN: source NAT IP address for outgoing traffic.
  # match_vip - Enable to match packets that have had their destination addresses changed by a VIP. Valid values: enable, disable.
  # match_vip_only - Enable/disable matching of only those packets that have had their destination addresses changed by a VIP. Valid values: enable, disable.
  # diffserv_forward - Enable to change packet's DiffServ values to the specified diffservcode-forward value. Valid values: enable, disable.
  # diffserv_reverse - Enable to change packet's reverse (reply) DiffServ values to the specified diffservcode-rev value. Valid values: enable, disable.
  # diffservcode_forward - Change packet's DiffServ to this value.
  # diffservcode_rev - Change packet's reverse (reply) DiffServ to this value.
  # tcp_mss_sender - Sender TCP maximum segment size (MSS).
  # tcp_mss_receiver - Receiver TCP maximum segment size (MSS).
  # comments - Comment.
  # label - Label for the policy that appears when the GUI is in Section View mode.
  # global_label - Label for the policy that appears when the GUI is in Global View mode.
  # auth_cert - HTTPS server certificate for policy authentication.
  # auth_redirect_addr - HTTP-to-HTTPS redirect address for firewall authentication.
  # redirect_url - URL users are directed to after seeing and accepting the disclaimer or authenticating.
  # identity_based_route - Name of identity-based routing rule.
  # block_notification - Enable/disable block notification. Valid values: enable, disable.
  # custom_log_fields - Custom fields to append to log messages for this policy. The structure of custom_log_fields block is documented below.
  # replacemsg_override_group - Override the default replacement message group for this policy.
  # srcaddr_negate - When enabled srcaddr specifies what the source address must NOT be. Valid values: enable, disable.
  # dstaddr_negate - When enabled dstaddr specifies what the destination address must NOT be. Valid values: enable, disable.
  # service_negate - When enabled service specifies what the service must NOT be. Valid values: enable, disable.
  # internet_service_negate - When enabled internet-service specifies what the service must NOT be. Valid values: enable, disable.
  # internet_service_src_negate - When enabled internet-service-src specifies what the service must NOT be. Valid values: enable, disable.
  # timeout_send_rst - Enable/disable sending RST packets when TCP sessions expire. Valid values: enable, disable.
  # captive_portal_exempt - Enable to exempt some users from the captive portal. Valid values: enable, disable.
  # decrypted_traffic_mirror - Decrypted traffic mirror.
  # ssl_mirror - Enable to copy decrypted SSL traffic to a FortiGate interface (called SSL mirroring). Valid values: enable, disable.
  # ssl_mirror_intf - SSL mirror interface name. The structure of ssl_mirror_intf block is documented below.
  # scan_botnet_connections - Block or monitor connections to Botnet servers or disable Botnet scanning. Valid values: disable, block, monitor.
  # dsri - Enable DSRI to ignore HTTP server responses. Valid values: enable, disable.
  # radius_mac_auth_bypass - Enable MAC authentication bypass. The bypassed MAC address must be received from RADIUS server. Valid values: enable, disable.
  # delay_tcp_npu_session - Enable TCP NPU session delay to guarantee packet order of 3-way handshake. Valid values: enable, disable.
  # vlan_filter - Set VLAN filters.
  # sgt_check - Enable/disable security group tags (SGT) check. Valid values: enable, disable.
  # sgt - Security group tags. The structure of sgt block is documented below.
  # dynamic_sort_subtable - Sort sub-tables, please do not set this parameter when configuring static sub-tables. Options: [ false, true, natural, alphabetical ]. false: Default value, do not sort tables; true/natural: sort tables in natural order. For example: [ a10, a2 ] --> [ a2, a10 ]; alphabetical: sort tables in alphabetical order. For example: [ a10, a2 ] --> [ a10, a2 ].
  # vdomparam - Specifies the vdom to which the resource will be applied when the FortiGate unit is running in VDOM mode. Only one vdom can be specified. If you want to inherit the vdom configuration of the provider, please do not set this parameter.

  
	dynamic "srcaddr" {
		for_each = var.firewall_policy.srcaddr
		content {
			name = srcaddr.value
		}
	}

	dynamic "dstaddr" {
		for_each = var.firewall_policy.dstaddr
		content {
			name = dstaddr.value
		}
	}

  	dynamic "srcintf" {
		for_each = var.firewall_policy.srcintf
		content {
			name = srcintf.value
		}
	}

  dynamic "dstintf" {
		for_each = var.firewall_policy.dstintf
		content {
			name = dstintf.value
		}
	}

  dynamic "service" {
		for_each = var.firewall_policy.service
		content {
			name = service.value
		}
  }
}