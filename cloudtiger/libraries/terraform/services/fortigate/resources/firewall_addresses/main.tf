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
  subnet               = lookup(var.firewall_address, "subnet", null)
  fqdn                 = lookup(var.firewall_address, "fqdn", null)
  associated_interface = lookup(var.firewall_address, "associated_interface", null)
  end_ip               = lookup(var.firewall_address, "end_ip", null)
  start_ip             = lookup(var.firewall_address, "start_ip", null)
  uuid                 = lookup(var.firewall_address, "uuid", null)
  visibility           = lookup(var.firewall_address, "visibility", null)

  sub_type             = lookup(var.firewall_address, "sub_type", null)
  clearpass_spt        = lookup(var.firewall_address, "clearpass_spt", null) # Valid values: unknown, healthy, quarantine, checkup, transient, infected.
  start_mac            = lookup(var.firewall_address, "start_mac", null)
  end_mac              = lookup(var.firewall_address, "end_mac", null)
  country              = lookup(var.firewall_address, "country", null)
  wildcard_fqdn = lookup(var.firewall_address, "wildcard_fqdn", null)
  cache_ttl = lookup(var.firewall_address, "cache_ttl", null)
  wildcard = lookup(var.firewall_address, "wildcard", null)
  sdn = lookup(var.firewall_address, "sdn", null)
  interface = lookup(var.firewall_address, "interface", null)
  tenant = lookup(var.firewall_address, "tenant", null)
  organization = lookup(var.firewall_address, "organization", null)
  epg_name = lookup(var.firewall_address, "epg_name", null)
  subnet_name = lookup(var.firewall_address, "subnet_name", null)
  sdn_tag = lookup(var.firewall_address, "sdn_tag", null)
  policy_group = lookup(var.firewall_address, "policy_group", null)
  obj_tag = lookup(var.firewall_address, "obj_tag", null)
  obj_type = lookup(var.firewall_address, "obj_type", null)
  tag_detection_level = lookup(var.firewall_address, "tag_detection_level", null)
  tag_type = lookup(var.firewall_address, "tag_type", null)
  comment = lookup(var.firewall_address, "comment", null)
  filter = lookup(var.firewall_address, "filter", null)
  sdn_addr_type = lookup(var.firewall_address, "sdn_addr_type", null) # Valid values: private, public, all.
  node_ip_only = lookup(var.firewall_address, "node_ip_only", null) # Valid values: enable, disable.
  obj_id = lookup(var.firewall_address, "obj_id", null)
  fabric_object = lookup(var.firewall_address, "fabric_object", null) # Valid values: enable, disable.
  dynamic_sort_subtable = lookup(var.firewall_address, "dynamic_sort_subtable", null)

  #macaddr - Multiple MAC address ranges. The structure of macaddr block is documented below.
  #fsso_group - FSSO group(s). The structure of fsso_group block is documented below.
  # list = lookup(var.firewall_address, "list", null)
  #  tagging = lookup(var.firewall_address, "tagging", null)
  #vdomparam - Specifies the vdom to which the resource will be applied when the FortiGate unit is running in VDOM mode. Only one vdom can be specified. If you want to inherit the vdom configuration of the provider, please do not set this parameter.
}