terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_user_local" "trnamex2" {
  name  = lookup(var.user_local, "name ", null )
  fosid  = lookup(var.user_local, "fosid ", null )
  status  = lookup(var.user_local, "status ", null ) # Valid values: enable, disable
  type  = lookup(var.user_local, "type ", null ) # Valid values: password, radius, tacacs+, ldap
  passwd  = lookup(var.user_local, "passwd ", null )
  ldap_server  = lookup(var.user_local, "ldap_server ", null )
  radius_server  = lookup(var.user_local, "radius_server ", null )
  tacacs_server  = lookup(var.user_local, "tacacs_server ", null )
  two_factor  = lookup(var.user_local, "two_factor ", null )
  two_factor_authentication  = lookup(var.user_local, "two_factor_authentication ", null ) # Valid values: fortitoken, email, sms
  two_factor_notification  = lookup(var.user_local, "two_factor_notification ", null ) # Valid values: email, sms
  fortitoken  = lookup(var.user_local, "fortitoken ", null )
  email_to  = lookup(var.user_local, "email_to ", null )
  sms_server  = lookup(var.user_local, "sms_server ", null ) # Valid values: fortiguard, custom
  sms_custom_server  = lookup(var.user_local, "sms_custom_server ", null )
  sms_phone  = lookup(var.user_local, "sms_phone ", null )
  passwd_policy  = lookup(var.user_local, "passwd_policy ", null )
  passwd_time  = lookup(var.user_local, "passwd_time ", null )
  authtimeout  = lookup(var.user_local, "authtimeout ", null )
  workstation  = lookup(var.user_local, "workstation ", null )
  auth_concurrent_override  = lookup(var.user_local, "auth_concurrent_override ", null ) # Valid values: enable, disable
  auth_concurrent_value  = lookup(var.user_local, "auth_concurrent_value ", null )
  ppk_secret  = lookup(var.user_local, "ppk_secret ", null )
  ppk_identity  = lookup(var.user_local, "ppk_identity ", null )
  username_sensitivity  = lookup(var.user_local, "username_sensitivity ", null ) # Valid values: disable, enable
  username_case_insensitivity  = lookup(var.user_local, "username_case_insensitivity ", null ) # Valid values: enable, disable
  username_case_sensitivity  = lookup(var.user_local, "username_case_sensitivity ", null ) # Valid values: disable, enable
  vdomparam  = lookup(var.user_local, "vdomparam ", null )


}