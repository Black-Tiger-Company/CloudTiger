############
# Function (lambda for AWS)
############

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "lambda" {

  filename      = var.function.filename
  function_name = var.function.name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = var.function.handler

  source_code_hash = filebase64sha256(var.function.source_code)

  runtime = var.function.runtime

  tags = merge(
    var.function.module_labels,
    {
        "Name" = format("%s%s_function", var.function.module_prefix, var.function.name)
    }
  )
}