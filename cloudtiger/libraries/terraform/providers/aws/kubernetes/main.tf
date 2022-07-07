############
# Security Group / Firewall group
############

resource "aws_security_group_rule" "example" {
  for_each          = var.k8s_cluster.ingress_rules
  type              = "ingress"
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  cidr_blocks       = each.value.cidr
  security_group_id = aws_eks_cluster.k8s_cluster.vpc_config[0].cluster_security_group_id
}

############
# Kubernetes Cluster
############

resource "aws_eks_cluster" "k8s_cluster" {

  name = format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)

  role_arn = aws_iam_role.k8s_role.arn

  vpc_config {
    subnet_ids              = [for private_subnet in var.k8s_cluster.subnetworks : var.network["private_subnets"][private_subnet].id]
    endpoint_private_access = true
  }

  tags = merge(
    var.k8s_cluster.module_labels,
    {
      "name" = format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)
    }
  )

}

############
# Node groups
############

resource "aws_eks_node_group" "k8s_node_groups" {

  for_each = var.k8s_cluster.k8s_node_groups

  cluster_name    = format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)
  node_group_name = format("%s_%s_%s_k8s_node_group", var.k8s_cluster.module_prefix, each.key, var.k8s_cluster.cluster_name)
  node_role_arn   = aws_iam_role.k8s_role_node_group[each.key].arn
  subnet_ids      = [var.network["private_subnets"][each.value.subnetwork].id]
  remote_access {
    ec2_ssh_key = var.k8s_cluster.ssh_public_key
  }

  scaling_config {
    desired_size = each.value.desired_size
    max_size     = each.value.max_size
    min_size     = each.value.min_size
  }

  depends_on = [aws_eks_cluster.k8s_cluster]

  ami_type       = var.k8s_cluster.system_image
  instance_types = [var.k8s_cluster.instance_type.type]
  disk_size      = each.value.disk_size

  tags = merge(
    var.k8s_cluster.module_labels,
    {
      "name" = format("%s_%s_%s_k8s_node_group", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name, each.key)
    }
  )

}

############
# Role for K8s cluster
############

resource "aws_iam_role" "k8s_role" {

  name = format("%s_%s_k8s_cluster_role", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)

  assume_role_policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "eks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
POLICY
}

############
# Role for K8s cluster node groupe
############

resource "aws_iam_role" "k8s_role_node_group" {

  for_each = var.k8s_cluster.k8s_node_groups

  name = format("%s_%s_%s_k8s_node_group_role", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name, each.key)

  assume_role_policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
POLICY
}

############
# Role policies
############

resource "aws_iam_role_policy_attachment" "k8s_cluster_policy" {

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.k8s_role.name
}

resource "aws_iam_role_policy_attachment" "k8s_service_policy" {

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.k8s_role.name
}

resource "aws_iam_role_policy_attachment" "k8s_worker_node_policy" {

  for_each = var.k8s_cluster.k8s_node_groups

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.k8s_role_node_group[each.key].name
}

resource "aws_iam_role_policy_attachment" "k8s_cni_policy" {

  for_each = var.k8s_cluster.k8s_node_groups

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.k8s_role_node_group[each.key].name
}

resource "aws_iam_role_policy_attachment" "k8s_container_registry_policy" {

  for_each = var.k8s_cluster.k8s_node_groups

  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.k8s_role_node_group[each.key].name
}
