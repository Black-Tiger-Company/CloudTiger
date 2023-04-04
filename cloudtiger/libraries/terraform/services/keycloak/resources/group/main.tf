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

resource "keycloak_group" "group" {
  realm_id = data.keycloak_realm.realm.id
  name     = var.group_config.name
}

resource "keycloak_group_roles" "group_roles" {
  realm_id = data.keycloak_realm.realm.id
  group_id = keycloak_group.group.id

  role_ids = [
    # keycloak_role.realm_role.id,
    # keycloak_role.client_role.id,
  ]
}