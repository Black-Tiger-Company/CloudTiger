# variable vm {
# 	description = "Map of parameters for virtual machine"
# 	type = object({
# 		vm_name = string,
# 		user = string,
# 		network_name = string,
# 		network_prefix = string,
# 		module_labels = map(string),
# 		module_prefix = string,
# 		group = string,
# 		instance_type = string,
# 		availability_zone = string,
# 		system_image = string,
# 		subnet_name = string,
# 		subnet_type = string,
# 		private_ip = string,
# 		root_volume = object({
# 			size = string,
# 			type = string
# 		}),
# 		data_volume = object({
# 			size = string,
# 			type = string
# 		}),
# 		ssh_public_key_path = string,
# 		ingress_rules = map(any)
# 		egress_rules = map(any)
# 	})
# }

# ingress_rules = map(object({
# 	description = string,
# 	from_port = string,
# 	to_port = string,
# 	protocol = string,
# 	cidr = string
# })),

variable "vm" {
}

variable "network" {

}