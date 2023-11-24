# ############
# # Security Group / Firewall group
# ############

locals {
  network_prefix = lookup(var.network[var.vm.network_name], "prefix", "")
}

resource "google_compute_firewall" "security_group_vm" {

  name = lower(substr(
    replace(
      replace(
        format("%s%s_sg", var.vm.module_prefix, var.vm.vm_name),
        "_",
      "-"),
      ".",
    "-"),
    0,
  61))

  network = substr(replace(format("%s%s_network", local.network_prefix, var.vm.network_name), "_", "-"), 0, 61)
  # network = var.vm.network_name
  direction = "INGRESS"

  # allow {
  # 	protocol = "icmp"
  # }

  allow {
    protocol = "icmp"
    # ports    = [for rule in var.vm.ingress_rules : format("%s-%s", rule.from_port, rule.to_port) if contains(["icmp", "-1"], rule.protocol)]
  }

  allow {
    protocol = "tcp"
    ports    = [for rule in var.vm.ingress_rules : replace(format("%s-%s", rule.from_port, rule.to_port), "0-0", "0-65534") if contains(["tcp", "-1"], rule.protocol)]
  }

  allow {
    protocol = "udp"
    ports    = [for rule in var.vm.ingress_rules : replace(format("%s-%s", rule.from_port, rule.to_port), "0-0", "0-65534") if contains(["udp", "-1"], rule.protocol)]
  }

  # allow {
  #   protocol = "tcp"
  #   ports    = [for rule in var.vm.ingress_rules : rule.to_port if rule.protocol != "icmp"]
  #   # ports    = [for rule in var.vm.ingress_rules : rule.to_port]
  # }

  # allow {
  #   protocol = "udp"
  #   ports    = [for rule in var.vm.ingress_rules : rule.to_port if rule.protocol != "icmp"]
  #   # ports    = [for rule in var.vm.ingress_rules : rule.to_port]
  # }

  # allow {
  #   protocol = "icmp"
  #   # ports    = [for rule in var.vm.ingress_rules : rule.to_port if rule.protocol != "icmp"]
  #   ports    = [for rule in var.vm.ingress_rules : rule.to_port]
  # }

  source_ranges = [for rule in var.vm.ingress_rules : rule.cidr[0]]
}

############
# Virtual Machine
############
# data "google_compute_image" "vm_image" {
# #   family  = var.vm.system_image
#   name = var.vm.system_image
# }

resource "google_compute_instance" "virtual_machine" {

  depends_on = [google_compute_firewall.security_group_vm]

  name = lower(substr(
    replace(
      replace(
        format("%s%s_vm", var.vm.module_prefix, var.vm.vm_name),
        "_",
      "-"),
      ".",
    "-"),
    0,
  61))

  # name = substr(replace(format("%s%s_vm", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
  machine_type = var.vm.instance_type.type
  zone         = var.vm.availability_zone

  boot_disk {
    initialize_params {
      image = var.vm.system_image
      # image = data.google_compute_image.vm_image.name
      size = lookup(var.vm.root_volume, "size", var.vm.default_root_volume_size)
      type = lookup(var.vm.root_volume, "type", lookup(var.vm.generic_volume_parameters, lookup(var.vm.root_volume, "type", "small_root"), "pd-standard"))
    }
  }

  network_interface {
    network    = substr(replace(format("%s%s_network", local.network_prefix, var.vm.network_name), "_", "-"), 0, 61)
    subnetwork = substr(replace(format("%s%s_%s_%s_subnet", local.network_prefix, var.vm.network_name, var.vm.subnet_name, var.vm.subnet_type), "_", "-"), 0, 61)
    network_ip = var.vm.private_ip

    ### dynamic creation of public IPs
    dynamic "access_config" {
      for_each = google_compute_address.elastic_ip

      content {
        nat_ip = access_config.value.address
      }
    }
  }

  # ### dynamic creation of public IPs
  # dynamic "network_interface" {
  # 	for_each = google_compute_address.elastic_ip

  # 	content {
  # 		subnetwork = substr(replace(format("%s%s_%s_%s_subnet", local.network_prefix, var.vm.network_name, var.vm.subnet_name, var.vm.subnet_type), "_", "-"), 0, 61)
  # 		access_config {
  # 			nat_ip = network_interface.value.address
  # 		}
  # 	}
  # }

  # root_block_device {
  # 	type = var.vm.root_volume.type
  # 	size = var.vm.root_volume.size
  # 	auto_delete = true
  # }

  lifecycle {
    ignore_changes = [attached_disk]
  }

  service_account {
    scopes = ["storage-rw"]
  }

  allow_stopping_for_update = true

  labels = merge(
    var.vm.module_labels,
    {
      "name" = lower(substr(
        replace(
          replace(
            format("%s%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name),
            "_",
          "-"),
          ".",
        "-"),
        0,
      61))
      # "name" = substr(replace(format("%s%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
      # "group" = var.vm.group,
      # "ssh_key" = format("%s", var.vm.module_prefix)
    }
  )

  metadata = {
    ssh-keys = "${var.vm.user}:${file(var.vm.ssh_public_key_path)}"
  }

}

############
# Data Volume
############

locals {
  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }
}

resource "google_compute_disk" "vm_data_volume" {

  for_each = local.non_empty_data_volumes

  name = substr(replace(format("%s%s_data_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)

  size = lookup(each.value, "size", var.vm.default_data_volume_size)
  type = lookup(each.value, "type", 
  lookup(
    lookup(var.vm.generic_volume_parameters, lookup(each.value, "type", "small_root"), {"type":"pd-standard"}),
    "type",
    "pd-standard")
  )

  labels = merge(
    var.vm.module_labels,
    {
      "name" = lower(substr(
        replace(
          replace(
            format("%s%s_data_volume", var.vm.module_prefix, var.vm.vm_name),
            "_",
          "-"),
          ".",
        "-"),
        0,
      61))
      # "name" = substr(replace(format("%s%s_data_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
    }
  )

  zone = var.vm.availability_zone

}

resource "google_compute_attached_disk" "default" {

  # count = (var.vm.data_volume.size > 0 ? 1 : 0)
  for_each = local.non_empty_data_volumes

  disk     = google_compute_disk.vm_data_volume[each.key].id
  instance = google_compute_instance.virtual_machine.id

  zone = google_compute_disk.vm_data_volume[each.key].zone

}

############
# Static public IP
############

resource "google_compute_address" "elastic_ip" {

  count = (var.vm.subnet_type == "public" ? 1 : 0)

  name = substr(replace(format("%s%s_elastic_ip", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)

  # labels = merge(
  #     var.vm.module_labels,
  #     {
  #         "name" = substr(replace(format("%s%s_elastic_ip", var.vm.module_prefix, var.vm.vm_name)
  #     }
  # )

}