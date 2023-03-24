# output all_grafana_folders {
#   value       = data.grafana_folders.all_folders
#   sensitive   = true
#   description = "Dump of all Grafana folders"
# }

# output all_grafana_dashboards {
#   value       = data.grafana_dashboards.all_dashboards
#   sensitive   = true
#   description = "Dump of all Grafana dashboards"
# }



output grafana_folder {
  value       = data.grafana_folder.all_folders
  sensitive   = false
  description = "description"
  depends_on  = []
}

output grafana_dashboards_list {
  value       = local.dashboards_list
  sensitive   = false
  description = "description"
  depends_on  = []
}

output grafana_dashboards {
  value       = local.dashboards_list_clean
  sensitive   = false
  description = "description"
  depends_on  = []
}

