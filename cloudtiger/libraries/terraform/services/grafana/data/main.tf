terraform {
  required_providers {
    grafana = {
      source = "grafana/grafana"
      version = "1.36.1"
    }
  }
}

data "grafana_folder" "all_folders" {
    for_each = toset(var.grafana_config.folders)
    title = each.value
}

data "grafana_dashboards" "all_dashboards" {
    for_each = data.grafana_folder.all_folders
    folder_ids = [each.value.id]
}

locals {
  dashboards_list = flatten([
    for folder, dashboards in data.grafana_dashboards.all_dashboards : [
      for  dashboard in dashboards["dashboards"] : {
        folder_title = folder
        title = dashboard["title"]
        uid = dashboard["uid"]
      }
    ]
  ])
  dashboards_uids = toset([
    for dashboard in local.dashboards_list:
    dashboard.uid
  ])
}

data "grafana_dashboard" "from_id" {
  for_each = local.dashboards_uids
  uid = each.value
}

locals {
  dashboards_list_clean = flatten([
    for uid, dashboard in data.grafana_dashboard.from_id : 
        dashboard
  ])

}