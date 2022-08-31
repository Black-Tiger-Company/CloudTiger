terraform {
  required_providers {
    fortios = {
      source = "fortinetdev/fortios"
      version = "1.15.0"
    }
  }
}

resource "fortios_user_ldap" "trnamex2" {
  name  = lookup(var.user_ldap, "name ", null )
server  = lookup(var.user_ldap, "server ", null )
secondary_server  = lookup(var.user_ldap, "secondary_server ", null )
tertiary_server  = lookup(var.user_ldap, "tertiary_server ", null )
server_identity_check  = lookup(var.user_ldap, "server_identity_check ", null ) # Valid values: enable, disable
source_ip  = lookup(var.user_ldap, "source_ip ", null )
source_port  = lookup(var.user_ldap, "source_port ", null )
cnid  = lookup(var.user_ldap, "cnid ", null )
dn  = lookup(var.user_ldap, "dn ", null )
type  = lookup(var.user_ldap, "type ", null ) # Valid values: simple, anonymous, regular
two_factor  = lookup(var.user_ldap, "two_factor ", null ) # Valid values: disable, fortitoken-cloud
two_factor_authentication  = lookup(var.user_ldap, "two_factor_authentication ", null ) # Valid values: fortitoken, email, sms
two_factor_notification  = lookup(var.user_ldap, "two_factor_notification ", null ) # Valid values: email, sms
username  = lookup(var.user_ldap, "username ", null )
password  = lookup(var.user_ldap, "password ", null )
group_member_check  = lookup(var.user_ldap, "group_member_check ", null ) # Valid values: user-attr, group-object, posix-group-object
group_search_base  = lookup(var.user_ldap, "group_search_base ", null )
group_object_filter  = lookup(var.user_ldap, "group_object_filter ", null )
group_filter  = lookup(var.user_ldap, "group_filter ", null )
secure  = lookup(var.user_ldap, "secure ", null ) # Valid values: disable, starttls, ldaps
ssl_min_proto_version  = lookup(var.user_ldap, "ssl_min_proto_version ", null ) # Valid values: default, SSLv3, TLSv1, TLSv1-1, TLSv1-2
ca_cert  = lookup(var.user_ldap, "ca_cert ", null )
port  = lookup(var.user_ldap, "port ", null )
password_expiry_warning  = lookup(var.user_ldap, "password_expiry_warning ", null ) # Valid values: enable, disable
password_renewal  = lookup(var.user_ldap, "password_renewal ", null ) # Valid values: enable, disable
member_attr  = lookup(var.user_ldap, "member_attr ", null )
account_key_processing  = lookup(var.user_ldap, "account_key_processing ", null ) # Valid values: same, strip
account_key_filter  = lookup(var.user_ldap, "account_key_filter ", null )
search_type  = lookup(var.user_ldap, "search_type ", null ) # Valid values: recursive
client_cert_auth  = lookup(var.user_ldap, "client_cert_auth ", null ) # Valid values: enable, disable
client_cert  = lookup(var.user_ldap, "client_cert ", null )
obtain_user_info  = lookup(var.user_ldap, "obtain_user_info ", null ) # Valid values: enable, disable
user_info_exchange_server  = lookup(var.user_ldap, "user_info_exchange_server ", null )
interface_select_method  = lookup(var.user_ldap, "interface_select_method ", null ) # Valid values: auto, sdwan, specify
interface  = lookup(var.user_ldap, "interface ", null )
antiphish  = lookup(var.user_ldap, "antiphish ", null ) # Valid values: enable, disable
password_attr  = lookup(var.user_ldap, "password_attr ", null )
vdomparam  = lookup(var.user_ldap, "vdomparam ", null )
  
}