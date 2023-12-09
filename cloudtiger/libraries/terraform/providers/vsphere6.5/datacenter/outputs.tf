output "datacenter" {
  value = {
    #   datacenter_id = data.vsphere_datacenter.datacenter.id
    datacenter_id = local.current_datacenter.id
    cluster_id = merge({
      for cluster in data.vsphere_compute_cluster.cluster :
      cluster.name => cluster.id
      },
      {
        for cluster in vsphere_compute_cluster.cluster :
        cluster.name => cluster.id
    })
    resource_pool_id = merge({
      for cluster in data.vsphere_compute_cluster.cluster :
      cluster.name => cluster.resource_pool_id
      },
      {
        for cluster in vsphere_compute_cluster.cluster :
        cluster.name => cluster.resource_pool_id
    })
    #   data.vsphere_compute_cluster.cluster.id
    templates_list = {
      for template in data.vsphere_virtual_machine.packer_template.* :
      template.name => template
    }
  }
  sensitive   = true
  description = "description"
  depends_on  = []
}

output "requested_datacenter" {
  value = var.datacenter
}