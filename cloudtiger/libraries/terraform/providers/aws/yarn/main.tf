############
# YARN (EMR for AWS)
############


# IAM role for EMR Service
resource "aws_iam_role" "iam_emr_service_role" {
  name = "iam_emr_service_role"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "elasticmapreduce.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "iam_emr_service_policy" {
  name = "iam_emr_service_policy"
  role = aws_iam_role.iam_emr_service_role.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Resource": "*",
        "Action": [
            "ec2:AuthorizeSecurityGroupEgress",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:CancelSpotInstanceRequests",
            "ec2:CreateNetworkInterface",
            "ec2:CreateSecurityGroup",
            "ec2:CreateTags",
            "ec2:DeleteNetworkInterface",
            "ec2:DeleteSecurityGroup",
            "ec2:DeleteTags",
            "ec2:DescribeAvailabilityZones",
            "ec2:DescribeAccountAttributes",
            "ec2:DescribeDhcpOptions",
            "ec2:DescribeInstanceStatus",
            "ec2:DescribeInstances",
            "ec2:DescribeKeyPairs",
            "ec2:DescribeNetworkAcls",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DescribePrefixLists",
            "ec2:DescribeRouteTables",
            "ec2:DescribeSecurityGroups",
            "ec2:DescribeSpotInstanceRequests",
            "ec2:DescribeSpotPriceHistory",
            "ec2:DescribeSubnets",
            "ec2:DescribeVpcAttribute",
            "ec2:DescribeVpcEndpoints",
            "ec2:DescribeVpcEndpointServices",
            "ec2:DescribeVpcs",
            "ec2:DetachNetworkInterface",
            "ec2:ModifyImageAttribute",
            "ec2:ModifyInstanceAttribute",
            "ec2:RequestSpotInstances",
            "ec2:RevokeSecurityGroupEgress",
            "ec2:RunInstances",
            "ec2:TerminateInstances",
            "ec2:DeleteVolume",
            "ec2:DescribeVolumeStatus",
            "ec2:DescribeVolumes",
            "ec2:DetachVolume",
            "iam:GetRole",
            "iam:GetRolePolicy",
            "iam:ListInstanceProfiles",
            "iam:ListRolePolicies",
            "iam:PassRole",
            "s3:CreateBucket",
            "s3:Get*",
            "s3:List*",
            "s3:*Object*", 
            "sdb:BatchPutAttributes",
            "sdb:Select",
            "sqs:CreateQueue",
            "sqs:Delete*",
            "sqs:GetQueue*",
            "sqs:PurgeQueue",
            "sqs:ReceiveMessage"
        ]
    }]
}
EOF
}

# IAM Role for EC2 Instance Profile
resource "aws_iam_role" "iam_emr_profile_role" {
  name = "iam_emr_profile_role"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_instance_profile" "emr_profile" {
  name = "emr_profile"
  role = aws_iam_role.iam_emr_profile_role.name
}

resource "aws_iam_policy" "emr_ec2_policy" {
  name        = "emr_ec2_policy"
  description = "Policy for ec2 composing EMR cluster"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
          "s3:CreateBucket",
          "s3:Get*",
          "s3:List*",
          "s3:*Object*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "policy-attach" {
  name       = "policy-attachment"
  roles      = [aws_iam_role.iam_emr_profile_role.name]
  policy_arn = aws_iam_policy.emr_ec2_policy.arn
}

resource "aws_emr_cluster" "yarn" {
  name          = var.yarn.name
  release_label = "emr-4.6.0" 
  applications  = var.yarn.applications # https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-app-versions-6.x.html

  termination_protection            = var.yarn.termination_protection
  keep_job_flow_alive_when_no_steps = true

  ec2_attributes {
    #subnet_ids                         = var.yarn.subnetworks #EMR Job Flow: ValidationException: The supplied ec2SubnetId is not valid
    # emr_managed_master_security_group = aws_security_group.sg.id #todo: add security group
    # emr_managed_slave_security_group  = aws_security_group.sg.id
    instance_profile                  = aws_iam_instance_profile.emr_profile.arn
  }

  master_instance_group {
    instance_type = var.yarn.master_instance_type
  }

  core_instance_group {
    instance_type = var.yarn.worker_instance_type
    instance_count = var.yarn.worker_instance_number
  }

  ebs_root_volume_size = 100

  service_role = aws_iam_role.iam_emr_service_role.arn

  tags = merge(
    var.yarn.module_labels,
    {
        "Name" = format("%s%s_yarn", var.yarn.module_prefix, var.yarn.name)
    }
  )
}
