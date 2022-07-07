output "profile" {
  value = aws_iam_instance_profile.iam_instance_profile
}

output policy_document {
  value       = data.aws_iam_policy_document.policy_document
  sensitive   = false
  description = "description"
  depends_on  = []
}
