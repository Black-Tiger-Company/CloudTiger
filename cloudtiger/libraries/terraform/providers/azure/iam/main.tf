
resource "azurerm_resource_group" "iam_rg" {
  name     = format("%siam_rg", var.common_prefix)
  location = var.region
}

#########################
# Managed identity / Instance profile
#########################

resource "azurerm_user_assigned_identity" "uai" {
  for_each            = var.profile
  resource_group_name = azurerm_resource_group.iam_rg.name
  location            = azurerm_resource_group.iam_rg.location

  name = each.key
}

##########################
# Roles
##########################

data "azurerm_subscription" "primary" {
}

data "azurerm_client_config" "client_config" {
}

locals {
  custom_role = {
    for role_name, role in var.role :
    role_name => role if length(role["custom_policies"]) > 0
  }
}

resource "azurerm_role_definition" "iam_role" {
  for_each = local.custom_role
  name     = format("%s%siam_role", var.common_prefix, each.key)
  scope    = data.azurerm_subscription.primary.id

  permissions {
    actions     = length(each.value["custom_policies"]) > 0 ? var.policy[each.value["custom_policies"][0]].actions : []
    not_actions = []
  }

  assignable_scopes = [
    data.azurerm_subscription.primary.id,
  ]
}

locals {
  defined_role_assignment = {
    for profile_name, profile in var.profile :
    profile_name => profile if(length(var.role[profile["role_name"]]["default_policies"]) > 0)
  }
  custom_role_assignment = {
    for profile_name, profile in var.profile :
    profile_name => profile if(length(var.role[profile["role_name"]]["custom_policies"]) > 0)
  }
}

resource "azurerm_role_assignment" "defined_role_assignment" {
  for_each             = local.defined_role_assignment
  scope                = data.azurerm_subscription.primary.id
  role_definition_name = var.role[each.value["role_name"]]["default_policies"][0]
  principal_id         = azurerm_user_assigned_identity.uai[each.key].principal_id
}

resource "azurerm_role_assignment" "custom_role_assignment" {
  for_each           = local.custom_role_assignment
  scope              = data.azurerm_subscription.primary.id
  role_definition_id = azurerm_role_definition.iam_role[var.role[each.value]["role_name"]["custom_policies"][0]]
  principal_id       = azurerm_user_assigned_identity.uai[each.key].principal_id
}