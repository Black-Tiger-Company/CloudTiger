output "kubernetes_parameters" {
  value = {
    kubernetes_cluster_endpoint              = google_container_cluster.k8s_cluster.endpoint
    kubernetes_cluster_id                    = google_container_cluster.k8s_cluster.id
    kubernetes_cluster_certificate_authority = google_container_cluster.k8s_cluster.master_auth.0.cluster_ca_certificate
    kubernetes_cluster_full_name             = google_container_cluster.k8s_cluster.name
  }
  sensitive   = true
  description = "Map of kubernetes clusters parameters"
  depends_on  = []
}

output "desired_k8s_clusters" {
  value = var.k8s_cluster
}

output "k8s_dedicated_volumes_ids" {
  value = {
    for volume_name, volume in google_compute_disk.k8s_dedicated_volume :
    volume_name => volume.name
  }
}