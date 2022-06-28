output "kubernetes_parameters" {
  value = {
    kubernetes_cluster_full_name = azurerm_kubernetes_cluster.k8s_cluster.tags.name

    kubeconfig = azurerm_kubernetes_cluster.k8s_cluster.kube_config_raw
  }
}

output "k8s_dedicated_volumes_ids" {
  value = {
    "blank" : "blank"
  }
}