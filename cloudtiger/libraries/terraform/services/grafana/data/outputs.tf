output all_grafana_folders {
  value       = data.grafana_folders.all_folders
  sensitive   = true
  description = "Dump of all Grafana folders"
}

output all_grafana_dashboards {
  value       = data.grafana_dashboards.all_dashboards
  sensitive   = true
  description = "Dump of all Grafana dashboards"
}
