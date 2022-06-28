variable "role" {
  type = map(object({
    custom_policies  = list(string),
    default_policies = list(string)
    services         = list(string),
  }))
  description = "Role for tasks execution"
}

variable "policy" {
  type = map(object({
    actions   = list(string),
    effect    = string,
    resources = list(string)
  }))
  description = "Policy to be attached to roles, allowing actions"
}

variable "profile" {
  type = map(object({
    role_name = string
  }))
  description = "Specific roles attached to VMs"
}

variable "common_labels" {
  type        = map(string)
  description = "description"
}

variable "common_prefix" {
  type        = string
  default     = ""
  description = "description"
}

variable "region" {
  default = ""
}