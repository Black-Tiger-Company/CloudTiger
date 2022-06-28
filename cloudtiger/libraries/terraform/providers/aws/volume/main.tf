resource "aws_ebs_volume" "indep_volume" {
  availability_zone = var.volume.zone
  size              = var.volume.size

  tags = merge(
    var.volume.module_labels,
    {
      "name" = format("%s_%s_k8s_cluster", var.volume.module_prefix, var.volume.name)
    }
  )
}