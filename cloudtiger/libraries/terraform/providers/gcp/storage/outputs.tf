output "bucket_dependency" {
  # Again, the value is not important because we're just
  # using this for its dependencies.
  value = {"name": google_storage_bucket.storage.name}

  # Anything that refers to this output must wait until
  # the actions for azurerm_monitor_diagnostic_setting.example
  # to have completed first.
  depends_on = [google_storage_bucket.storage]
}