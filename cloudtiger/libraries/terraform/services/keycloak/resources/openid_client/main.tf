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

resource "keycloak_openid_client" "openid_client" {
  realm_id            = data.keycloak_realm.realm.id
  client_id           = lookup(var.client_config, "client_id",  lookup(var.client_config, "name", null))

  name                = lookup(var.client_config, "name", null)
  enabled             = lookup(var.client_config, "enabled", true)

  access_type         = lookup(var.client_config, "access_type", "CONFIDENTIAL")
  valid_redirect_uris = lookup(var.client_config, "valid_redirect_uris", ["https://*","http://*"]) # "http://localhost:8080/openid-callback"
 

  login_theme = lookup(var.client_config, "login_theme", "keycloak")

  standard_flow_enabled = true

}

resource keycloak_openid_client_authorization_scope scope {
    resource_server_id = keycloak_openid_client.openid_client.id
    name               = "scope_name"
    realm_id           = data.keycloak_realm.realm.id
}


resource keycloak_openid_client_authorization_resource resource {
    resource_server_id = keycloak_openid_client.openid_client.id
    name               = "resource_name"
    realm_id           = data.keycloak_realm.realm.id
    # scopes
    uris = [
        "/endpoint/*"
    ]
}

data keycloak_openid_client_authorization_policy policy {
    realm_id           = data.keycloak_realm.realm.id
    resource_server_id = keycloak_openid_client.openid_client.id
    name               = "terraform_policy"
    # role { id /required}   # required
   # type               = "role" # required
    # policies           = #[keycloak_openid_client_authorization_policy.policy.id]
    # resources
    # scopes
}

resource keycloak_openid_client_authorization_permission permission {
    resource_server_id = keycloak_openid_client.openid_client.id
    realm_id           = data.keycloak_realm.realm.id
    name               = "permission_name"
    policies           = [data.keycloak_openid_client_authorization_policy.policy.id]
    resources          = [keycloak_openid_client_authorization_resource.resource.id]
}