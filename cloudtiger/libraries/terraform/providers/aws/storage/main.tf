############
# Storage (S3 for AWS)
############

resource "aws_s3_bucket" "storage" {
    bucket = var.storage.name
    tags = merge(
    var.storage.module_labels,
    {
      "Name" = format("%s%s_storage", var.storage.module_prefix, var.storage.name)
    }
  )
}

resource "aws_s3_bucket_acl" "storage_acl" {
  bucket = aws_s3_bucket.storage.id
  acl    = var.storage.access_control
}