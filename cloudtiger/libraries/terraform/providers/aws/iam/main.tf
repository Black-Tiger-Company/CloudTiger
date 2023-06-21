########################
# Policy
########################

data "aws_iam_policy_document" "policy_document" {
  for_each = var.policy
  statement {
    actions   = each.value.actions
    resources = each.value.resources
    effect    = each.value.effect
  }
}

# resource "aws_iam_policy" "iam_policy" {
#   for_each = var.policy
#   policy   = data.aws_iam_policy_document.policy_document[each.key].json
#   name     = format("%s_%s_iam_policy", var.common_prefix, each.key)
# }

#############################
# Role
#############################

data "aws_iam_policy_document" "assume_role_document" {
  for_each = var.role
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = each.value.services
    }
    effect = "Allow"
  }
}

resource "aws_iam_role" "iam_role" {
  for_each = var.role
  name     = format("%s_%s_iam_role", var.common_prefix, each.key)

  assume_role_policy    = data.aws_iam_policy_document.assume_role_document[each.key].json
  force_detach_policies = true

  tags = merge(
    var.common_labels,
    {
      "Name" = format("%s_%s_iam_role", var.common_prefix, each.key)
    }
  )
}

###################
# Policy attachments
###################

data "aws_caller_identity" "current" {}

locals {
  roles_policies = [
    for iam_role_name, iam_role in var.role : [
      for policy in iam_role.custom_policies :
      {
        role_name   = iam_role_name,
        policy_name = policy
      }
    ]
  ]
  roles_custom_policies_flatten = flatten(local.roles_policies)
  formatted_roles_custom_policies = { for role in local.roles_custom_policies_flatten :
    role.role_name => role.policy_name
  }

  ### CLOUD POLICIES
  roles_default_policies = [
    for iam_role_name, iam_role in var.role : [
      for default_policy in iam_role.default_policies :
      {
        role_name   = iam_role_name,
        policy_name = default_policy
      }
    ]
  ]
  roles_default_policies_flatten = flatten(local.roles_default_policies)
  formatted_roles_default_policies = { for role in local.roles_default_policies_flatten :
    role.role_name => role.policy_name
  }

}

# resource "aws_iam_role_policy_attachment" "role_custom_policy_attachment" {
#   for_each   = local.formatted_roles_custom_policies
#   role       = format("%s_%s_iam_role", var.common_prefix, each.key)
#   policy_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${format("%s_%s_iam_policy", var.common_prefix, each.value)}"
#   depends_on = [
#     aws_iam_role.iam_role,
#     aws_iam_policy.iam_policy
#   ]
# }

resource "aws_iam_role_policy_attachment" "role_default_policy_attachment" {
  for_each   = local.formatted_roles_default_policies
  role       = format("%s_%s_iam_role", var.common_prefix, each.key)
  policy_arn = "arn:aws:iam::aws:policy/${each.value}"
  depends_on = [
    aws_iam_role.iam_role
  ]
}

#########################
# Instance profile
#########################

resource "aws_iam_instance_profile" "iam_instance_profile" {
  for_each = var.profile
  name     = format("%s_%s_iam_instance_profile", var.common_prefix, each.key)
  role     = format("%s_%s_iam_role", var.common_prefix, each.value.role_name)
  depends_on = [
    aws_iam_role.iam_role
  ]
}