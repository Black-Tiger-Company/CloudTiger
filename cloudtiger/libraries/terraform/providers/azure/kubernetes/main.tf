locals {
  is_main_k8s_node_group  = { for node_group_name, node_group_content in var.k8s_cluster.k8s_node_groups : node_group_name => node_group_content if node_group_content.is_default_node_pool == true }
  k8s_node_groups_workers = { for node_group_name, node_group_content in var.k8s_cluster.k8s_node_groups : node_group_name => node_group_content if node_group_content.is_default_node_pool == false }
}


resource "azurerm_resource_group" "k8s_rg" {
  name     = format("%s_k8s_rg", var.k8s_cluster.cluster_name)
  location = var.k8s_cluster.location
}

############
# Kubernetes Cluster
############

resource "azurerm_kubernetes_cluster" "k8s_cluster" {

  name                = var.k8s_cluster.cluster_name
  location            = azurerm_resource_group.k8s_rg.location
  resource_group_name = azurerm_resource_group.k8s_rg.name
  dns_prefix          = var.k8s_cluster.az_custom_parameters.dns_prefix
  kubernetes_version  = var.k8s_cluster.az_custom_parameters.kubernetes_version

  linux_profile {
    admin_username = var.k8s_cluster.username

    ssh_key {
    #   key_data = file(format("%s/%s.pub", var.ssh_public_key_path, var.k8s_cluster.module_prefix))
	  key_data = file(var.k8s_cluster.ssh_public_key_path)
    }
  }

  dynamic "default_node_pool" {
    for_each = local.is_main_k8s_node_group
    content {
      name                 = default_node_pool.key
      node_count           = default_node_pool.value["desired_size"]
      vm_size              = var.k8s_cluster.az_custom_parameters.vm_size
      type                 = "AvailabilitySet"
      vnet_subnet_id       = var.network["private_subnets"][var.k8s_cluster.subnetworks[0]].id
      orchestrator_version = var.k8s_cluster.az_custom_parameters.kubernetes_version
    }
  }



  service_principal {
    client_id     = var.client_id
    client_secret = var.client_secret
  }

#   addon_profile {
#     kube_dashboard {
#       enabled = true
#     }
#   }

  network_profile {
    load_balancer_sku  = "standard"
    network_plugin     = "azure"
    service_cidr       = "10.10.0.0/16"
    docker_bridge_cidr = "172.17.0.1/16"
    dns_service_ip     = "10.10.0.10"
  }

  tags = {
    name = format("%s", var.k8s_cluster.cluster_name)
  }
}

############
# Node groups
############

resource "azurerm_kubernetes_cluster_node_pool" "k8s_node_groups" {
  for_each              = local.k8s_node_groups_workers
  name                  = each.key
  kubernetes_cluster_id = azurerm_kubernetes_cluster.k8s_cluster.id
  vm_size               = "Standard_DS2_v2"
  node_count            = each.value.desired_size
  max_count             = each.value.max_size
  min_count             = each.value.min_size
  vnet_subnet_id        = var.network["private_subnets"][each.value.subnetwork].id
  orchestrator_version  = var.k8s_cluster.az_custom_parameters.kubernetes_version
  enable_auto_scaling   = true

  tags = {
    Environment = "Production"
  }
}

resource "azurerm_container_registry" "acr" {
  name                = "BTcontainerRegistry1"
  location            = azurerm_resource_group.k8s_rg.location
  resource_group_name = azurerm_resource_group.k8s_rg.name
  sku                 = "Standard"
}