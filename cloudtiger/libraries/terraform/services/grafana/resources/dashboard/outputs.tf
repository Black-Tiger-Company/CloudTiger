output grafana_dashboards {
  value       = local.dashboards
  sensitive   = false
  description = "description"
  depends_on  = []
}

output grafana_folders {
  value       = local.dict_folders
  sensitive   = false
  description = "description"
  depends_on  = []
}