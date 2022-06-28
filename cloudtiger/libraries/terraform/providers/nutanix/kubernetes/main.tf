terraform {
  required_providers {
    nutanix = {
      source  = "nutanix/nutanix"
      version = "1.2.0"
    }
  }
}

data "nutanix_clusters" "clusters" {}

data "nutanix_subnet" "subnets" {
  subnet_name = var.k8s_cluster.subnetworks[0]
}

locals {
  cluster_map = { for cluster in data.nutanix_clusters.clusters.entities :
    cluster.name => cluster
  }
}

resource "nutanix_karbon_cluster" "k8s_cluster" {

  name = replace(trim(substr(format("%s", var.k8s_cluster.cluster_name), 0, 15), " _-"), "_", "-")

  version = "1.19.8-0"

  cni_config {
    node_cidr_mask_size = var.k8s_cluster.nutanix_custom_parameters.node_cidr_mask_size
    pod_ipv4_cidr       = var.k8s_cluster.nutanix_custom_parameters.pod_cidr_range
    service_ipv4_cidr   = var.k8s_cluster.nutanix_custom_parameters.service_cidr_range
  }

  storage_class_config {
    name = "default-storageclass"
    volumes_config {
      file_system                = "ext4"
      username                   = var.nutanix_username
      password                   = var.nutanix_password
      prism_element_cluster_uuid = local.cluster_map[var.k8s_cluster.zones[0]].metadata.uuid
      storage_container          = var.k8s_cluster.dedicated_volumes.storage_container.name
    }
    reclaim_policy = var.k8s_cluster.nutanix_custom_parameters.reclaim_policy
  }

  master_node_pool {
    name            = replace(trim(substr(format("k8s-%s-masterpool", var.k8s_cluster.cluster_name), 0, 15), " _-"), "_", "-")
    node_os_version = var.k8s_cluster.system_image
    num_instances   = var.k8s_cluster.k8s_node_groups.master_node_pool.desired_size
    ahv_config {
      cpu                        = var.k8s_cluster.k8s_instance_types["master_node_pool"].nb_vcpu_per_socket
      disk_mib                   = var.k8s_cluster.k8s_node_groups.master_node_pool.disk_size * 1024
      memory_mib                 = var.k8s_cluster.k8s_instance_types["master_node_pool"].memory
      prism_element_cluster_uuid = local.cluster_map[var.k8s_cluster.zones[0]].metadata.uuid
      network_uuid               = data.nutanix_subnet.subnets.metadata.uuid
    }
  }

  etcd_node_pool {
    name            = replace(trim(substr(format("k8s-%s-etcdpool", var.k8s_cluster.cluster_name), 0, 15), " _-"), "_", "-")
    node_os_version = var.k8s_cluster.system_image
    num_instances   = var.k8s_cluster.k8s_node_groups.etcd_node_pool.desired_size
    ahv_config {
      cpu                        = var.k8s_cluster.k8s_instance_types["etcd_node_pool"].nb_vcpu_per_socket
      disk_mib                   = var.k8s_cluster.k8s_node_groups.etcd_node_pool.disk_size * 1024
      memory_mib                 = var.k8s_cluster.k8s_instance_types["etcd_node_pool"].memory
      prism_element_cluster_uuid = local.cluster_map[var.k8s_cluster.zones[0]].metadata.uuid
      network_uuid               = data.nutanix_subnet.subnets.metadata.uuid
    }
  }

  worker_node_pool {
    name            = replace(trim(substr(format("k8s-%s-workerpool", var.k8s_cluster.cluster_name), 0, 15), " _-"), "_", "-")
    node_os_version = var.k8s_cluster.system_image
    num_instances   = var.k8s_cluster.k8s_node_groups.worker_node_pool.desired_size
    ahv_config {
      cpu                        = var.k8s_cluster.k8s_instance_types["worker_node_pool"].nb_vcpu_per_socket
      disk_mib                   = var.k8s_cluster.k8s_node_groups.worker_node_pool.disk_size * 1024
      memory_mib                 = var.k8s_cluster.k8s_instance_types["worker_node_pool"].memory
      prism_element_cluster_uuid = local.cluster_map[var.k8s_cluster.zones[0]].metadata.uuid
      network_uuid               = data.nutanix_subnet.subnets.metadata.uuid
    }
  }

}