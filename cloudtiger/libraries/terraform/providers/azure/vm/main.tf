
resource "azurerm_resource_group" "rg" {
  name     = format("%s%s_vm_rg", var.vm.module_prefix, var.vm.vm_name)
  location = var.vm.location
}

data "azurerm_user_assigned_identity" "uai" {

  name                = var.vm.instance_profile_name
  resource_group_name = format("%siam_rg", var.vm.common_prefix)
}

############
# Virtual Machine
############

resource "azurerm_virtual_machine" "virtual_machine" {
  name                  = var.vm.vm_name
  location              = var.vm.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.network_interface.id]
  vm_size               = var.vm.instance_type.type

  identity {
    type         = "UserAssigned"
    identity_ids = [data.azurerm_user_assigned_identity.uai.id]
  }

  storage_os_disk {
    name              = format("%s%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name)
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

  storage_image_reference {
    publisher = var.vm.system_image.publisher
    offer     = var.vm.system_image.offer
    sku       = var.vm.system_image.sku
    version   = var.vm.system_image.version
  }

  os_profile {
    computer_name  = replace(var.vm.vm_name, "_", "-")
    admin_username = var.vm.user
  }

  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      key_data = file(var.vm.ssh_public_key_path)
      path     = format("/home/%s/.ssh/authorized_keys", var.vm.user)
    }
  }

  tags = merge(
    var.vm.module_labels,
    {
      "name" = format("%s%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name)
    }
  )
}

locals {
  network_prefix = lookup(var.network[var.vm.network_name], "prefix", "")
}

data "azurerm_subnet" "vm_subnet" {

  resource_group_name = format("%s%s_network_rg", local.network_prefix, var.vm.network_name)

  virtual_network_name = var.vm.network_name

  name = var.vm.subnet_name

}

resource "azurerm_network_interface" "network_interface" {
  name                = var.vm.vm_name
  location            = var.vm.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = format("%s%s_vm_nic", var.vm.module_prefix, var.vm.vm_name)
    subnet_id                     = data.azurerm_subnet.vm_subnet.id
    private_ip_address_allocation = lookup(var.vm, "private_ip", "not_learned_yet") == "not_learned_yet" ? "Dynamic" : "Static"
    public_ip_address_id          = var.vm.subnet_type != "private" ? azurerm_public_ip.public_ip[0].id : null
    private_ip_address            = lookup(var.vm, "private_ip", "not_learned_yet") != "not_learned_yet" ? var.vm.private_ip : null
  }
}

resource "azurerm_public_ip" "public_ip" {
  count               = var.vm.subnet_type != "private" ? 1 : 0
  name                = format("%s%s_vm_public_ip", var.vm.module_prefix, var.vm.vm_name)
  location            = var.vm.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
}

# resource "azurerm_network_security_group" "vm_security_group" {
#   name                = format("%s_%s_network_sg", var.vm.module_prefix, var.vm.vm_name)
#   location            = var.vm.location
#   resource_group_name = azurerm_resource_group.rg.name
# }

data "azurerm_resource_group" "rg" {
  name = format("%s%s_network_rg", var.vm.module_prefix, var.vm.network_name)
}

data "azurerm_network_security_group" "vm_security_group" {
  name                = format("%s%s_%s_subnet_sg", var.vm.module_prefix, var.vm.network_name, var.vm.subnet_name)
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "azurerm_network_security_rule" "security_rule_ingress" {
  for_each                   = var.vm.ingress_rules
  name                       = format("%s_%s", each.value.description, var.vm.vm_name)
  ### HUGE WARNING : priority must be UNIQUE for each rule of each subnetwork
  ### right now we make the assumption that there will be maximum 100 different default rules,
  ### and we add 100 * index(vm_name) to make them different by VM (so no more than 40 VMs allowed
  ### per subnet)
  priority                   = each.value.priority + 100 * index(keys(var.vm.ingress_rules) , each.key)
  direction                  = "Inbound"
  access                     = "Allow"
  protocol                   = "Tcp"
  source_port_range          = "*"
  # source_port_range          = replace(each.value.from_port, "-1", "*")
  destination_port_range     = replace(each.value.to_port, "-1", "*")
  source_address_prefix      = each.value.cidr[0]
  destination_address_prefix = "*"

  resource_group_name         = data.azurerm_resource_group.rg.name
  network_security_group_name = data.azurerm_network_security_group.vm_security_group.name
}

############
# Data Volumes
############

locals {
  non_empty_data_volumes = {
    for volume_name, volume in var.vm.data_volumes :
    volume_name => volume if lookup(volume, "size", var.vm.default_data_volume_size) > 0
  }
}

resource "azurerm_managed_disk" "vm_data_volume" {

  for_each = local.non_empty_data_volumes

  name                 = format("%s%s_data_volume", var.vm.module_prefix, var.vm.vm_name)
  location             = var.vm.location
  resource_group_name  = azurerm_resource_group.rg.name
  storage_account_type = lookup(each.value, "type", 
  lookup(
    lookup(var.vm.generic_volume_parameters, lookup(each.value, "type", "small_root"), {"type":"pd-standard"}),
    "type",
    "Standard_LRS")
  )
  create_option        = "Empty"
  disk_size_gb         = lookup(each.value, "size", var.vm.default_data_volume_size)

  tags = merge(
    var.vm.module_labels,
    {
      "name" = format("%s%s_firewall", var.vm.module_prefix, var.vm.vm_name)
    }
  )
}

resource "azurerm_virtual_machine_data_disk_attachment" "vm_data_volume_attachment" {

  for_each = local.non_empty_data_volumes

  managed_disk_id    = azurerm_managed_disk.vm_data_volume[each.key].id
  virtual_machine_id = azurerm_virtual_machine.virtual_machine.id
  lun                = "1"
  caching            = "ReadWrite"
}
