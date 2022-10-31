terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_user_group" "trnamex2" {
  name  = lookup(var.user_group, "name ", null )
  fosid  = lookup(var.user_group, "fosid ", null )
  group_type  = lookup(var.user_group, "group_type ", null ) # Valid values: firewall, fsso-service, rsso, guest
  authtimeout  = lookup(var.user_group, "authtimeout ", null )
  auth_concurrent_override  = lookup(var.user_group, "auth_concurrent_override ", null ) # Valid values: enable, disable
  auth_concurrent_value  = lookup(var.user_group, "auth_concurrent_value ", null )
  http_digest_realm  = lookup(var.user_group, "http_digest_realm ", null )
  sso_attribute_value  = lookup(var.user_group, "sso_attribute_value ", null )
  # member  = lookup(var.user_group, "member ", null )
  # match  = lookup(var.user_group, "match ", null )
  user_id  = lookup(var.user_group, "user_id ", null ) # Valid values: email, auto-generate, specify
  password  = lookup(var.user_group, "password ", null ) # Valid values: auto-generate, specify, disable
  user_name  = lookup(var.user_group, "user_name ", null ) # Valid values: disable, enable
  sponsor  = lookup(var.user_group, "sponsor ", null ) # Valid values: optional, mandatory, disabled
  company  = lookup(var.user_group, "company ", null ) # Valid values: optional, mandatory, disabled
  email  = lookup(var.user_group, "email ", null ) # Valid values: disable, enable
  mobile_phone  = lookup(var.user_group, "mobile_phone ", null ) # Valid values: disable, enable
  sms_server  = lookup(var.user_group, "sms_server ", null ) # Valid values: fortiguard, custom
  sms_custom_server  = lookup(var.user_group, "sms_custom_server ", null )
  expire_type  = lookup(var.user_group, "expire_type ", null ) # Valid values: immediately, first-successful-login
  expire  = lookup(var.user_group, "expire ", null )
  max_accounts  = lookup(var.user_group, "max_accounts ", null )
  multiple_guest_add  = lookup(var.user_group, "multiple_guest_add ", null ) # Valid values: disable, enable
  # guest  = lookup(var.user_group, "guest ", null )
  dynamic_sort_subtable  = lookup(var.user_group, "dynamic_sort_subtable ", null )
  vdomparam  = lookup(var.user_group, "vdomparam ", null )

}