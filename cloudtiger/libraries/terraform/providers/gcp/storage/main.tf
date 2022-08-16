############
# Storage (Cloud storage for GCP)
############


resource "google_storage_bucket" "storage" {
    name = var.storage.name
    location = "US" #upper(split(var.storage.region, "-")[0])
    force_destroy = var.storage.force_destroy
    labels = merge(
    var.storage.module_labels,
    {
      "name" = format("%s%s_storage", var.storage.module_prefix, var.storage.name)
    }
  )
}

resource "google_storage_bucket_object" "bucket_object" {
  count = "${length(var.storage.objects)}"
  name   = var.storage.objects[count.index].name
  source = var.storage.objects[count.index].path
  bucket = var.storage.name

  depends_on = [google_storage_bucket.storage]
}

# TEST Create notifation (optional) when update in storage
resource "google_storage_notification" "notification" {
  bucket         = google_storage_bucket.storage.name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.storage_topic.id
  event_types    = ["OBJECT_FINALIZE", "OBJECT_METADATA_UPDATE"]
  # object_name_prefix
  # custom_attributes = {
  #   test = "testCloudtiger"
  # }
  depends_on = [google_pubsub_topic_iam_binding.binding]
}

data "google_storage_project_service_account" "gcs_account" {
}

# try to use topic in mq service
resource "google_pubsub_topic" "storage_topic" {
  name = format("%s_%s", var.storage.name, "storage_topic")
}

resource "google_pubsub_topic_iam_binding" "binding" {
  topic   = google_pubsub_topic.storage_topic.id
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"]
}

resource "google_pubsub_subscription" "topic_subscription" {
  name  = format("%s_%s", var.storage.name, "storage-subscription")
  topic = google_pubsub_topic.storage_topic.name

}