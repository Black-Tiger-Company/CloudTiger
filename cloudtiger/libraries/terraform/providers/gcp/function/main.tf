############
# Function (Cloud Function for GCP)
############

variable "storage_depends_on" {
  type    = any
  default = []
}

resource "google_storage_bucket_object" "function-zip" {
  name   = var.function.source_archive_object.name
  bucket = var.function.source_archive_object.bucket
  source = var.function.filename
}

resource "google_cloudfunctions_function" "function" {
  name        = var.function.name
  description = var.function.description
  runtime     = var.function.runtime

  available_memory_mb   = 128
  source_archive_bucket = var.function.source_archive_object.bucket
  source_archive_object = google_storage_bucket_object.function-zip.name
  entry_point           = var.function.entry_point

  dynamic "event_trigger" {
    for_each = var.function.event_trigger != null ? [var.function.event_trigger] : []
    content {
      event_type = event_trigger.value["event_type"]
      resource = event_trigger.value["resource"]
    }
  }

  depends_on = [var.storage_depends_on]
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

data "google_storage_project_service_account" "gcs_account" {
}