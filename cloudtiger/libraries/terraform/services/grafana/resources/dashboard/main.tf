terraform {
  required_providers {
    grafana = {
      source = "grafana/grafana"
      version = "1.36.1"
    }
  }
}


data "local_file" "input" {
  filename = var.dashboard_config.file_configuration
}

locals {
    folders= yamldecode(data.local_file.input.content)["grafana_folders_dump"].value
    dashboards= {
      for dashboard in yamldecode(data.local_file.input.content)["grafana_dashboard_dump"].value: 
          dashboard.dashboard_id => { 
          id=dashboard.dashboard_id
          config=dashboard.config_json
          title=dashboard.title
          uid=dashboard.uid
          folder=dashboard.folder
          url=dashboard.url
        }
    }
}

resource "grafana_folder" "folders" {

    for_each = local.folders
    title = each.value.title
    uid = lookup(each.value, "uid", null)
    #id = each.value.id
}

locals {
  // use id in key to find mapping with folder_id in dashboard
  dict_folders = { for folder in local.folders :
    folder.id => folder
  }
}

resource "grafana_dashboard" "dashboards" {

    depends_on = [grafana_folder.folders]

    for_each = local.dashboards
    config_json = each.value.config
    #title = each.value.title
    #uid = each.value.uid
    folder = grafana_folder.folders[local.dict_folders[tostring(each.value.folder)].title].id

}