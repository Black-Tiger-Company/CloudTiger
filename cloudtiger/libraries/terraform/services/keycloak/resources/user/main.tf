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

# This resource was created primarily to enable the acceptance tests for the keycloak_group resource. Creating users within Keycloak is not recommended.
# Instead, users should be federated from external sources by configuring user federation providers or identity providers.


data "keycloak_realm" "realm" {
    realm = "master"
}

resource "keycloak_user" "user_with_initial_password" {
  realm_id   = data.keycloak_realm.realm.id
  username   = lookup(var.user_config, "username", null)
  enabled    = lookup(var.user_config, "enabled", true)

  email      = lookup(var.user_config, "email", null)
  first_name = lookup(var.user_config, "first_name", null)
  last_name  = lookup(var.user_config, "last_name", null)

  # attributes = {
  #   foo = "bar"
  #   multivalue = "value1##value2"
  # }

  initial_password {
    value     = "panpan"
    temporary = true
  }
}

# resource "vault_mount" "kvv2" {
#   path        = "kvv2"
#   type        = "kv"
#   options     = { version = "2" }
#   description = "KV Version 2 secret engine mount"
# }

resource "vault_kv_secret_v2" "example" {
  mount                      = "kvV2"
  name                       = "secret"
  cas                        = 1
  delete_all_versions        = true
  data_json                  = jsonencode(
  {
    keycloak_pass       = keycloak_user.user_with_initial_password.initial_password[0].value
  }
  )
  custom_metadata {
    max_versions = 5
    data = {
      keycloak_user = lookup(var.user_config, "username", null)
    }
  }
} 