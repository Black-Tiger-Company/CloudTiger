terraform {
  required_providers {
    keycloak = {
      source = "mrparkers/keycloak"
      version = "4.2.0"
    }
  }
}

# Clients are applications and services that can request authentication of a user.
data "keycloak_realm" "realm" {
    realm = "master"
}

resource "keycloak_role" "client_role" {
  realm_id    = data.keycloak_realm.realm.id
  client_id   = lookup(var.role_config, "client_id", null)
  name        = var.role_config.name
  description = lookup(var.role_config, "description", null)
  # attributes = {
  #   key = "value"
  # }
}