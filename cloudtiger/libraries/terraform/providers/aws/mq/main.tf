############
# MQ (SQS for AWS)
############

resource "aws_sqs_queue" "mq" {
  name                      = var.mq.name
  delay_seconds             = var.mq.delay_seconds
  max_message_size          = var.mq.max_message_size
  message_retention_seconds = var.mq.message_retention_seconds
  receive_wait_time_seconds = var.mq.receive_wait_time_seconds
  # redrive_policy = jsonencode({
  #   deadLetterTargetArn = aws_sqs_queue.terraform_queue_deadletter.arn
  #   maxReceiveCount     = 4
  # })

  tags = merge(
    var.mq.module_labels,
    {
        "Name" = format("%s%s_mq", var.mq.module_prefix, var.mq.name)
    }
  )
}

# resource "aws_sqs_queue" "terraform_queue_deadletter" {
#   name = "terraform-example-deadletter-queue"
#   redrive_allow_policy = jsonencode({
#     redrivePermission = "byQueue",
#     sourceQueueArns   = [aws_sqs_queue.terraform_queue.arn]
#   })
# }