### provider
variable cloud_provider {
	description = "Provider name"
	type        = string
}

### project variables
variable labels {
	description = "Map of labels"
	type        = map
	default     = {}
}

### common prefix
variable prefix {
	description = "Common prefix for all resources"
	default     = ""
}

variable region {
	description = "Cloud region/datacenter name"
	default     = "no_region_specified"
}

### provider-specific parameters
variable system_images {
  description = "description"
}

variable generic_volume_parameters {
  description = "description"
}

variable ingress_rules {
  description = "description"
}

variable egress_rules {
  description = "description"
}

### IAM variables
variable policy {
  type        = map(object({
	  actions = list(string),
	  effect = string,
	  resources = list(string)
  }))
  description = "Map of all IAM policies"
  default     = {}
}

variable role {
  type        = map(object({
	  custom_policies = list(string),
	  default_policies = list(string)
	  services = list(string),
  }))
  description = "Map of all IAM roles"
  default     = {}
}

variable profile {
  type        = map(object({
	  role_name = string
  }))
  description = "Map of all instance profiles"
  default     = {}
}

### network variables
variable network {
	description = "Map of all networks and subnets"
}

### vm variables
variable vm {
  description = "description"
  default = {}
}

variable vm_types {
  description = "description"
}

variable default_password {
	description = "Default password at VM startup"
}

variable domain_ldap {
	description = "LDAP or AD Domain to join"
}

variable ou_ldap {
	description = "LDAP or AD OU to join computer"
}

variable user_ldap_join {
	description = "User to join computer to LDAP or AD"
}

variable password_user_ldap_join {
	description = "Password of User to join computer to LDAP or AD"
}

variable ldap_user_search_base {
	description = "Search base to lookup User on LDAP or AD"
}

variable ldap_sudo_search_base {
	description = "Search base to lookup Sudo command on LDAP or AD"
}

variable scope_folder {
	description = "Folder of the VM - used by vSphere provider"
	default = "."
}

### SSH keys
variable ssh_public_key {
  description = "path to public SSH key or name of SSH public key on public cloud account"
  default = "no_default_public_key"
}

### OS user
variable default_os_user {
	description = "name of the user for VMs"
	type = map(any)
	default     = {}
}

### List of default admins
variable users_list {
	description = "list of default admins for VMs"
	default = []
}

### kubernetes clusters
variable kubernetes {
	description = "Map of all managed kubernetes clusters"
	type = map(any)
	default     = {}
}

### independent
variable independent_volumes {
	description = "Volume for Kubernetes clusters"
	default     = {}
}

### container registry
variable container_registry {
	description = "A Docker registry for the whole project"
	type = string
	default = "dockerhub.com"
}

### default images per OS
variable default_os_images {
	description = "default VM images per OS"
	type = map(any)
	default = {}
}

### Map of root volume size per provider 
variable root_volume_size {
	description = "Map of root volume size per provider"
	type = map(string)
}

### Map of managed identities
variable managed_identity {
	default = {}
}

### List of vm types
variable list_vm_types {
	default = []
}

### Map of VM types aliases
variable vm_types_aliases {
	default = {}
}

### Map of services
variable services {
	default = {}
}

### Map of firewall
variable firewall {
	default = {}
}

### List of customers
variable customers {
	default = []
}

### Map of customers_aliases
variable customers_aliases {
	default = {}
}

### Map of color_aliases
variable color_aliases {
	default = {}
}

### Map of environment_status
variable environment_status {
	default = {}
}

### Map of vm_metadata
variable vm_metadata {
	default = {}
}