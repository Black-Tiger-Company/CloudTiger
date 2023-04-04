terraform {
  required_providers {
    keycloak = {
      source = "mrparkers/keycloak"
      version = "4.2.0"
    }
    vault = {
      source = "hashicorp/vault"
      version = "3.14.0"
    }
  }
}

resource "vault_mount" "kvv2" {
  path        = "kvV2"
  type        = "kv"
  options     = { version = "2" }
  description = "KV Version 2 secret engine mount"
}

# -------- user ---------------------------
resource "vault_auth_backend" "userpass" {
  type = "userpass"
}

resource "vault_generic_endpoint" "u1" {
  for_each = toset(["emeric.guibert", "user0"])
  depends_on           = [vault_auth_backend.userpass]
  path                 = join("", ["auth/userpass/users/", each.value]) 
  ignore_absent_fields = true

  data_json = <<EOT
{
  "policies" : [ "emeric.guibert"],
  "password": "azerty"
}
EOT
}


# ------- secret -----------------------
resource "vault_generic_secret" "keycloak_devops" {
  path = "kvV2/keycloak_devops"

  data_json = <<EOT
{
  "keycloak_password":   "devops"
}
EOT
depends_on = [
  vault_mount.kvv2
]
}

resource "vault_generic_secret" "keycloak_emeric" {
  path = "kvV2/keycloak_emeric"

  data_json = <<EOT
{
  "keycloak_password":   "emeric"
}
EOT
depends_on = [
  vault_mount.kvv2
]
}


# -------- group -----------------------
resource "vault_identity_group" "internal" {
  name     = "devops"
  type     = "internal"
  #policies = ["dev", "test"]

  metadata = {
    version = "2"
  }
}



# -------- policy ----------------------
# create a policy and attach it to a user
resource "vault_policy" "emeric_policy" {
  name = "emeric.guibert"

  policy = <<EOT
path "kvV2/metadata/env/emeric.guibert/*"
{ 
capabilities = ["read","list"] 
} 
#to list and read all data of env path inside kv secret 
path "kvV2/data/env/emeric.guibert/*"
{ 
capabilities = ["read","list"] 
} 

path "kvV2/*"
{ 
capabilities = ["list"] 
}

path "kvV2/data/keycloak_emeric" {
 capabilities = ["read"]
}

EOT
depends_on = [
  vault_generic_secret.keycloak_emeric
]
}

# create a policy and attach it to a group
resource "vault_policy" "devops_policy" {
  name = "devops"

  policy = <<EOT
path "kvV2/metadata/env/devops/*"
{ 
capabilities = ["read","list"] 
} 
#to list and read all data of env path inside kv secret 
path "kvV2/data/env/devops/*"
{ 
capabilities = ["read","list"] 
} 
# to list and read the secrets 
path "kvV2/*"
{ 
capabilities = ["list"] 
}

EOT
}
resource "vault_identity_group_policies" "policies" {
  policies = [
    "devops"
  ]

  exclusive = true

  group_id = vault_identity_group.internal.id
}

# --------  ldap  ----------------------
resource "vault_ldap_auth_backend" "ldap" {
    path        = "ldapTerraform"
    url         = "ldap://bt-ads01eu.btgroup.io"
    starttls    = false
    insecure_tls = true
    binddn      = "CN=svc-fr-grafana,OU=Service Accounts,OU=BT_Users,DC=btgroup,DC=io"
    bindpass    = "$totowdm12"
    #userdn      = "CN=auth_ldap,CN=Users,DC=france,DC=mktg"
    userattr    = "sAMAccountName"
    userfilter  = "sAMAccountName=%s"
    # upndomain   = "EXAMPLE.ORG"
    discoverdn  = false
    groupdn     = "CN=BT-grafana-viewers,OU=BT_Groups,DC=btgroup,DC=io"
    # groupfilter = "(&(objectClass=group)(member:1.2.840.113556.1.4.1941:={{.UserDN}}))"
}

resource "vault_ldap_auth_backend_user" "user" {
    username = "emeric.guibert"
    policies = ["qa"]
    backend  = vault_ldap_auth_backend.ldap.path
}