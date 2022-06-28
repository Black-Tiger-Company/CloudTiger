############
# Kubernetes Cluster
############

resource "google_container_cluster" "k8s_cluster" {
  name     = substr(replace(format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name), "_", "-"), 0, 40)
  location = var.k8s_cluster.zones[0]

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = substr(replace(format("%s_%s_network", var.k8s_cluster.module_prefix, var.k8s_cluster.network), "_", "-"), 0, 61)
  subnetwork = substr(replace(format("%s_%s_%s_private_subnet", var.k8s_cluster.module_prefix, var.k8s_cluster.network, var.k8s_cluster.subnetworks[0]), "_", "-"), 0, 61)

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

}

############
# Node pool
############

resource "google_container_node_pool" "k8s_node_groups" {

  for_each = var.k8s_cluster.k8s_node_groups

  name       = substr(replace(format("%s_%s_%s_k8s_nd_grp", var.k8s_cluster.module_prefix, each.key, var.k8s_cluster.cluster_name), "_", "-"), 0, 40)
  location   = var.k8s_cluster.zones[0]
  cluster    = google_container_cluster.k8s_cluster.name
  node_count = each.value.desired_size

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = merge(
      var.k8s_cluster.module_labels,
      {
        "name" = substr(replace(format("%s_%s_%s_k8s_node_group", var.k8s_cluster.module_prefix, each.key, var.k8s_cluster.cluster_name), "_", "-"), 0, 40)
      },
      {
        "disable-legacy-endpoints" = "true"
      }
    )

    machine_type = var.k8s_cluster.instance_type
  }
}

resource "google_compute_disk" "k8s_dedicated_volume" {
  for_each = var.k8s_cluster.dedicated_volumes
  name     = substr(replace(format("%s_%s_volume", var.k8s_cluster.module_prefix, each.value.name), "_", "-"), 0, 40)
  type     = "pd-standard"
  zone     = each.value.zone
  labels = merge(
    var.k8s_cluster.module_labels,
    {
      "name" = substr(replace(format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, each.value.name), "_", "-"), 0, 40)
    }
  )
  size = each.value.size
}
