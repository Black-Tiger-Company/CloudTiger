output "kubernetes_parameters" {
  value = {
    kubernetes_cluster_full_name = nutanix_karbon_cluster.k8s_cluster.name
  }
  sensitive   = false
  description = "Map of kubernetes clusters parameters"
  depends_on  = []
}

output "desired_k8s_clusters" {
  value = var.k8s_cluster
}

output "k8s_dedicated_volumes_ids" {
  value = "none"
}