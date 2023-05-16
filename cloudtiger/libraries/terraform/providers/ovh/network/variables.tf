variable "network" {
  #   type        = object({
  # 	network_name  = string,
  # 	module_labels = map(string),
  # 	module_prefix = string,
  # 	private_subnets = map(any),
  # 	public_subnets = map(any),
  # 	private_subnets_escape_public_subnet = string,
  # 	network_cidr = string
  #   })
  #   default     = ""
  description = "Map of parameters for network and associated subnets"
}

# variable network {

# }
# private_subnets = object({
# 	subnet_name = string,
# 	cidr_block = string,
# 	subnet_type = string
# }),
# public_subnets = object({
# 	subnet_name = string,
# 	cidr_block = string,
# 	subnet_type = string
# })

# private_subnets = map(object({
# 	subnet_name = string,
# 	cidr_block = string,
# 	subnet_type = string
# })),
# public_subnets = map(object({
# 	subnet_name = string,
# 	cidr_block = string,
# 	subnet_type = string
# }))