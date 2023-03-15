resource "grafana_folder" "data_source_dashboards" {

    for_each = var.dashboard_config.folders
    title = each.value.title
}

resource "grafana_dashboard" "test" {

    depends_on = [grafana_folder.data_source_dashboards]

    for_each = var.dashboard_config.dashboards
    config_json = jsonencode(each.value.config)
    folder = grafana_folder.data_source_dashboards[each.value.folder].id

}