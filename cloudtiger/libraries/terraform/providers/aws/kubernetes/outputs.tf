output "kubernetes_parameters" {
  value = {
    kubernetes_cluster_endpoint              = aws_eks_cluster.k8s_cluster.endpoint
    kubernetes_cluster_id                    = aws_eks_cluster.k8s_cluster.arn
    kubernetes_cluster_certificate_authority = aws_eks_cluster.k8s_cluster.certificate_authority
    kubernetes_cluster_full_name             = aws_eks_cluster.k8s_cluster.tags.name
    #   kubernetes_cluster_certificate = google_container_cluster.k8s_cluster.master_auth.0.client_certificate 
    #   kubernetes_cluster_client_key = google_container_cluster.k8s_cluster.master_auth.0.client_key 
    #   kubernetes_cluster_cluster_ca_certificate = google_container_cluster.k8s_cluster.master_auth.0.cluster_ca_certificate
  }
  sensitive   = true
  description = "Map of kubernetes clusters parameters"
  depends_on  = []
}
