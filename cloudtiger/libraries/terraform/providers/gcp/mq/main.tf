############
# MQ (PUB/SUB for GCP)
############

# resource: google_pubsub_schema: Settings for validating messages published against a schem

resource "google_pubsub_topic" "mq" {
  name                      = var.mq.name
  message_retention_duration = format("%s%s",var.mq.message_retention_seconds, "s")

  labels = merge(
    var.mq.module_labels,
    {
        "name" = format("%s%s_mq", var.mq.module_prefix, var.mq.name)
    }
  )
}

resource "google_pubsub_subscription" "mq_subscription" {
  name  = "mq-subscription"
  topic = google_pubsub_topic.mq.name

}