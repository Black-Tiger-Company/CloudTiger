############
# AWS AMI ID
############

locals {
  ami = {
    "debian_10" = {
      "owner" : "136693071363",
      "query" : "debian-10-amd64-20*"
    }
    "ubuntu_server_2004" = {
      "owner" : "099720109477",
      "query" : "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
    }
    "ubuntu_server_2204" = {
      "owner" : "099720109477",
      "query" : "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
    }
  }

  volume_device_name = {
      "1" : "/dev/sdf",
      "2" : "/dev/sdg",
      "3" : "/dev/sdh",
      "4" : "/dev/sdi",
      "5" : "/dev/sdj",
      "6" : "/dev/sdk",
      "7" : "/dev/sdl",
      "8" : "/dev/sdm",
      "9" : "/dev/sdn",
      "10" : "/dev/sdo",
  }

}

data "aws_ami" "ami" {
  owners      = [local.ami[var.vm.system_image]["owner"]]
  most_recent = true

  filter {
    name   = "name"
    values = [local.ami[var.vm.system_image]["query"]]
  }
}

############
# Security Group / Firewall group
############

data "aws_vpc" "vm_vpc" {
  filter {
    name   = "cidr"
    values = [var.network[var.vm.network_name]["network_cidr"]]
  }
}

resource "aws_security_group" "security_group_vm" {

  name                   = format("%s_%s_sg", var.vm.module_prefix, var.vm.vm_name)
  description            = "Description VM"
  vpc_id                 = data.aws_vpc.vm_vpc.id
  revoke_rules_on_delete = true

  dynamic "ingress" {
    for_each = var.vm.ingress_rules

    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr
    }
  }

  dynamic "egress" {
    for_each = var.vm.egress_rules

    content {
      description = egress.value.description
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr
    }
  }

  tags = merge(
    var.vm.module_labels,
    {
      "Name" = format("%s%s_firewall", var.vm.module_prefix, var.vm.vm_name)
    }
  )
}

############
# Virtual Machine
############

data "aws_subnet" "vm_subnet" {
  filter {
    name   = "cidr-block"
    values = [var.network[var.vm.network_name]["subnets"][var.vm.subnet_name]["cidr_block"]]
  }
}

resource "aws_instance" "virtual_machine" {

  depends_on             = [aws_security_group.security_group_vm]
  ami                    = data.aws_ami.ami.id
  instance_type          = var.vm.instance_type.type
  vpc_security_group_ids = [aws_security_group.security_group_vm.id]

  availability_zone           = var.vm.availability_zone
  key_name                    = var.vm.ssh_public_key
  subnet_id                   = data.aws_subnet.vm_subnet.id
  associate_public_ip_address = (var.vm.subnet_type == "public" ? true : false)
  private_ip                  = var.vm.private_ip
  source_dest_check           = true

  root_block_device {
    volume_type           = lookup(var.vm.root_volume, "type", lookup(var.vm.generic_volume_parameters, lookup(var.vm.root_volume, "type", "small_root"), "gp2"))
    volume_size           = lookup(var.vm.root_volume, "size", var.vm.default_root_volume_size)
    delete_on_termination = true
  }

  tags = merge(
    var.vm.module_labels,
    {
      "Name"  = format("%s%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name),
      "group" = var.vm.group
    }
  )

  volume_tags = merge(
    var.vm.module_labels,
    {
      "Name" = format("%s%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name)
    }
  )

  lifecycle {
    ignore_changes = [
      ami
    ]
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

resource "aws_ebs_volume" "vm_data_volume" {

  for_each = local.non_empty_data_volumes

  size = lookup(each.value, "size", var.vm.default_data_volume_size)
  type = lookup(each.value, "type", 
  lookup(
    lookup(var.vm.generic_volume_parameters, lookup(each.value, "type", "small_root"), {"type":"gp2"}),
    "type",
    "gp2")
  )

  tags = merge(
    var.vm.module_labels,
    {
      "Name" = format("%s%s_data_volume", var.vm.module_prefix, var.vm.vm_name)
    }
  )

  availability_zone = var.vm.availability_zone

}

resource "aws_volume_attachment" "vm_data_volume_attachment" {

  for_each = local.non_empty_data_volumes

  device_name = local.volume_device_name[tostring(each.value.index)]
  volume_id   = aws_ebs_volume.vm_data_volume[each.key].id
  instance_id = aws_instance.virtual_machine.id

}

############
# Static public IP
############

resource "aws_eip" "elastic_ip" {

  count = (var.vm.subnet_type == "public" ? 1 : 0)

  depends_on = [aws_instance.virtual_machine]
  instance   = aws_instance.virtual_machine.id

  tags = merge(
    var.vm.module_labels,
    {
      "Name" = format("%s%s_elastic_ip", var.vm.module_prefix, var.vm.vm_name)
    }
  )

}