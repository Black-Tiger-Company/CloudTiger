############
# Network (VPC for GCP)
############

resource "google_compute_network" "network" {

  name = substr(replace(format("%s%s_network", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)

}

############
# Private subnets
# isolated from Internet in ingress
############

resource "google_compute_subnetwork" "private_subnets" {

  for_each = var.network.private_subnets

  name = substr(replace(format("%s%s_%s_private_subnet", var.network.module_prefix, var.network.network_name, each.key), "_", "-"), 0, 61)

  network       = google_compute_network.network.name
  ip_cidr_range = each.value.cidr_block

}

############
# Public subnets
# accessible from Internet in ingress
############

resource "google_compute_subnetwork" "public_subnets" {

  for_each = var.network.public_subnets

  name = substr(replace(format("%s%s_%s_public_subnet", var.network.module_prefix, var.network.network_name, each.key), "_", "-"), 0, 61)

  network       = google_compute_network.network.name
  ip_cidr_range = each.value.cidr_block

}

# ############
# # Internet Gateway
# # allows communication between network and Internet
# ############

# resource "aws_internet_gateway" "internet_gateway" {

#     vpc_id = aws_vpc.network.vpc_id

#     tags = merge(
#         var.network.module_labels,
#         {
#             "name" = substr(replace(format("%s_%s_internet_gateway", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)
#         }
#     )

# }

############
# elastic IP for the NAT Gateway
############
resource "google_compute_address" "elastic_ip" {

  name = substr(replace(format("%s%s_elastic_ip", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)

  # labels = merge(
  #     var.network.module_labels,
  #     {
  #         "name" = substr(replace(format("%s_%s_elastic_ip", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)
  #     }
  # )

}


# resource "aws_eip" "elastic_ip" {

#     vpc = true
#     depends_on = [aws_internet_gateway.internet_gateway]

#     tags = merge(
#         var.network.module_labels,
#         {
#             "name" = substr(replace(format("%s_%s_elastic_ip", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)
#         }
#     )
# }

############
# NAT Gateway
# allows communication from VMs without a public IP to the public Internet
# used with an elastic IP
############

resource "google_compute_router" "router" {

  name = substr(replace(format("%s%s_router", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)

  network = google_compute_network.network.id
}

resource "google_compute_router_nat" "nat" {

  name = substr(replace(format("%s%s_nat_gateway", var.network.module_prefix, var.network.network_name), "_", "-"), 0, 61)

  router = google_compute_router.router.name

  nat_ip_allocate_option             = "MANUAL_ONLY"
  nat_ips                            = google_compute_address.elastic_ip.*.self_link
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  ### dynamic listing of all private subnets
  dynamic "subnetwork" {
    for_each = google_compute_subnetwork.private_subnets

    content {
      name                    = subnetwork.value.name
      source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
    }
  }
}

# resource "aws_nat_gateway" "nat_gateway" {

#     for_each = var.network.public_subnets

#     allocation_id = aws_eip.elastic_ip.id
#     subnet_id = aws_subnet.public_subnets[each.key].id

#     tags = merge(
#         var.network.module_labels,
#         {
#             "name" = substr(replace(format("%s_%s_%s_nat_gateway", var.network.module_prefix, var.network.network_name, each.value.public_subnet_name), "_", "-"), 0, 61)
#         }
#     )

# }

############
# Private route tables
# allow resources to reach other resources on networks
############

resource "google_compute_route" "private_route_tables" {

  for_each = var.network.private_subnets

  name = substr(replace(format("%s%s_%s_private_rt", var.network.module_prefix, var.network.network_name, each.key), "_", "-"), 0, 61)

  network          = google_compute_network.network.name
  dest_range       = "0.0.0.0/0"
  next_hop_gateway = "default-internet-gateway"

}

# resource "aws_route_table_association" "private_rta" {

#     for_each = var.network.private_subnets

#     subnet_id = aws_subnet.private_subnets[each.value].id
#     route_table_id = aws_route_table.private_subnets[each.value].id
# }

############
# Public route tables
# allow resources to reach other resources on networks
############

resource "google_compute_route" "public_route_tables" {

  for_each = var.network.public_subnets

  name = substr(replace(format("%s%s_%s_public_rt", var.network.module_prefix, var.network.network_name, each.key), "_", "-"), 0, 61)

  network          = google_compute_network.network.name
  dest_range       = "0.0.0.0/0"
  next_hop_gateway = "default-internet-gateway"

}


# resource "aws_route_table" "public_route_tables" {

#     for_each = var.network.private_subnets

#     vpc_id = aws_vpc.network.vpc_id
#     route {
#         cidr_block = "0.0.0.0/0"
#         gateway_id = aws_internet_gateway.internet_gateway.id
#     }
# }

# resource "aws_route_table_association" "public_rta" {

#     for_each = var.network.public_subnets

#     subnet_id = aws_subnet.public_subnets[each.value].id
#     route_table_id = aws_route_table.public_subnets[each.value].id
# }