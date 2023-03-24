terraform {
  required_providers {
    grafana = {
      source = "grafana/grafana"
      version = "1.36.1"
    }
  }
}

resource "grafana_data_source" "prometheus" {
  type                = var.data_source_config.type
  name                = var.data_source_config.name
  is_default          = lookup(var.data_source_config, "is_default", false)
  uid                 = lookup(var.data_source_config, "uid", null)
  url                 = var.data_source_config.url
  basic_auth_enabled  = var.data_source_config.basic_auth_enabled
  basic_auth_username = ""

  json_data_encoded = lookup(var.data_source_config, "json_data_encoded", null)

}