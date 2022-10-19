terraform {
  required_providers {
    nexus = {
      source  = "datadrivers/nexus"
      version = "1.21.0"
    }
  }
}

# Nexus privileges
resource "nexus_privilege" "privileges" {
  for_each         = var.nexus_config.privileges
  name             = each.key
  actions          = each.value.actions
  type             = each.value.type
  content_selector = lookup(each.value, "content_selector", null)
  description      = lookup(each.value, "description", "No description")
  domain           = lookup(each.value, "domain", null)
  format           = lookup(each.value, "format", null)
  pattern          = lookup(each.value, "pattern", null)
  repository       = lookup(each.value, "repository", null)
  script_name      = lookup(each.value, "script_name", null)

  depends_on = ["nexus_repository.repositories"]
}

# Nexus roles
resource "nexus_role" "roles" {
  for_each    = var.nexus_config.roles
  roleid      = each.value.id
  name        = each.key
  description = lookup(each.value, "description", "Standard Nexus role")
  privileges  = lookup(each.value, "privileges", [])
  roles       = lookup(each.value, "roles", [])

  depends_on = [nexus_privilege.privileges]
}

# Nexus users
resource "nexus_security_user" "users" {
  for_each  = var.nexus_config.users

  lifecycle {
    ignore_changes = [password]
  }

  userid    = each.key
  firstname = each.value.firstname
  lastname  = each.value.lastname
  email     = each.value.email
  password  = each.value.password
  roles     = each.value.roles
  status    = each.value.status

  depends_on = [nexus_role.roles]
}

locals {
  repo_types = distinct([for repo in var.nexus_config.repositories : repo.format])
  repo_types_dict = {
    for repo_type in local.repo_types :
    repo_type => 1
  }

  filtered_repositories = {
    for k, v in var.nexus_config.repositories :
    k => v
    if v["type"] != "proxy"
  }
}
# # Blob store for repositories by format
# resource "nexus_blobstore" "blobstore" {
#   for_each = local.filtered_repositories
#   name     = format("blob-store-%s", each.key)
#   type     = "File"
#   path     = format("%s/blob-store-%s", lookup(each.value, "path", "/data"), each.key)

#   soft_quota {
#     limit = 100000000
#     type  = "spaceRemainingQuota"
#   }
# }

# Blob store for repositories by format
resource "nexus_blobstore_file" "blobstore" {
  for_each = local.filtered_repositories
  name     = format("blob-store-%s", each.key)
  path     = format("%s/blob-store-%s", lookup(each.value, "path", "/data"), each.key)

  soft_quota {
    limit = 100000000
    type  = "spaceRemainingQuota"
  }
}

# Repository
resource "nexus_repository" "repositories" {
  for_each = var.nexus_config.repositories
  name     = each.key
  format   = each.value.format
  type     = each.value.type

  lifecycle {
    ignore_changes = [storage[0].write_policy]
  }

  depends_on = ["nexus_blobstore_file.blobstore"]

  storage {
    blob_store_name                = format("blob-store-%s", each.key)
    strict_content_type_validation = true
    write_policy                   = "ALLOW"
  }

  dynamic "apt" {
    for_each = each.value.format == "apt" ? [1] : []
    content {
      distribution = apt.value.distribution
      flat         = apt.value.flat
    }
  }

  dynamic "apt_signing" {
    for_each = each.value.format == "apt_signing" ? [1] : []
    content {
      keypair    = apt_signing.value.keypair
      passphrase = apt_signing.value.passphrase
    }
  }

  dynamic "bower" {
    for_each = each.value.format == "bower" ? [1] : []
    content {
      rewrite_package_urls = bower.value.rewrite_package_urls
    }
  }

  dynamic "cleanup" {
    for_each = each.value.format == "cleanup" ? [1] : []
    content {
      policy_names = cleanup.value.policy_names
    }
  }

  dynamic "docker" {
    for_each = each.value.format == "docker" ? [1] : []
    content {
      force_basic_auth = each.value.force_basic_auth
      http_port        = each.value.http_port
      https_port       = each.value.https_port
      v1enabled        = lookup(each.value, "vlenabled", false)
    }
  }

  dynamic "docker_proxy" {
    for_each = each.value.type == "proxy" ? [1] : []
    content {
      index_type = each.value.index_type
    }
  }

  dynamic "group" {
    for_each = each.value.format == "group" ? [1] : []
    content {
      member_names = group.value.member_names
    }
  }

  dynamic "http_client" {
    for_each = each.value.type == "proxy" ? [1] : []
    content {
      auto_block = lookup(each.value, "auto_block", true)
      blocked    = lookup(each.value, "blocked", false)
    }
  }

  dynamic "maven" {
    for_each = each.value.format == "maven2" ? [1] : []
    content {
      layout_policy  = each.value.layout_policy
      version_policy = each.value.version_policy
    }
  }

  dynamic "negative_cache" {
    for_each = each.value.type == "proxy" ? [1] : []
    content {
      enabled = lookup(each.value, "enabled", true)
      ttl     = lookup(each.value, "ttl", 1440)
    }
  }

  dynamic "nuget_proxy" {
    for_each = each.value.format == "nuget_proxy" ? [1] : []
    content {
      query_cache_item_max_age = each.value.query_cache_item_max_age
    }
  }

  dynamic "proxy" {
    for_each = each.value.type == "proxy" ? [1] : []
    content {
      content_max_age  = lookup(each.value, "content_max_age", 1440)
      metadata_max_age = lookup(each.value, "metadata_max_age", 1440)
      remote_url       = each.value.remote_url
    }
  }

  dynamic "storage" {
    for_each = each.value.format == "storage" ? [1] : []
    content {
      blob_store_name                = each.value.blob_store_name
      strict_content_type_validation = each.value.strict_content_type_validation
      write_policy                   = each.value.write_policy
    }
  }

  dynamic "yum" {
    for_each = each.value.format == "yum" ? [1] : []
    content {
      deploy_policy  = each.value.deploy_policy
      repodata_depth = each.value.repodata_depth
    }
  }

}