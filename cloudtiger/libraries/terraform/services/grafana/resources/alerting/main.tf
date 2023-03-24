terraform {
  required_providers {
    grafana = {
      source = "grafana/grafana"
      version = "1.36.1"
    }
  }
}


# resource "grafana_folder" "rule_folder" {
#   title = "My Alert Rule Folder"
# }

# data "local_file" "input_folders" {
#   filename = var.alerting_config.folders
# }

data "local_file" "input_alerts" {
  filename = var.alerting_config.file_configuration
}

locals {
    folder_uid = "uerLJ5-Gz"
    #folders= yamldecode(data.local_file.input_folders.content)["grafana_folders_dump"].value
    alerts_json = jsondecode(data.local_file.input_alerts.content)
    alerts = {
      for alert_rule in local.alerts_json["grafana_alert-rules"]:
          alert_rule.rule_group => alert_rule
    }
}

resource "grafana_rule_group" "my_alert_rule" {
  for_each = local.alerts 
  name             = each.value.rule_group
 # uid              = each.value.uid
  org_id           = each.value.orgId
  folder_uid       = local.folder_uid # grafana_folder.rule_folder.uid
  interval_seconds = each.value.intervalSeconds

  rule {
	name = each.value.title
    condition = each.value.condition
    no_data_state = each.value.no_data_state
    exec_err_state = each.value.exec_err_state
    annotations = lookup(each.value, "annotations", null)
    for = lookup(each.value, "for", null)
    labels = lookup(each.value, "labels", null)
            
    dynamic "data" {
        for_each =  each.value.data
        iterator = rule
        content {
            datasource_uid = rule.value.datasourceUid
            model = jsonencode(rule.value.model)
            ref_id = rule.value.refId
            relative_time_range {
                from = rule.value.relativeTimeRange.from
                to = rule.value.relativeTimeRange.to
            }
        }
        }
    }


#   rule {
#     name           = "My Alert Rule 1"
#     for            = "2m"
#     condition      = "B"
#     no_data_state  = "NoData"
#     exec_err_state = "Alerting"
#     annotations = {
#       "a" = "b"
#       "c" = "d"
#     }
#     labels = {
#       "e" = "f"
#       "g" = "h"
#     }
#     is_paused = false
#     data {
#       ref_id     = "A"
#       query_type = ""
#       relative_time_range {
#         from = 600
#         to   = 0
#       }
#       datasource_uid = "PD8C576611E62080A"
#       model = jsonencode({
#         hide          = false
#         intervalMs    = 1000
#         maxDataPoints = 43200
#         refId         = "A"
#       })
#     }
#     data {
#       ref_id     = "B"
#       query_type = ""
#       relative_time_range {
#         from = 0
#         to   = 0
#       }
#       datasource_uid = "-100"
#       model          = <<EOT
# {
#     "conditions": [
#         {
#         "evaluator": {
#             "params": [
#             3
#             ],
#             "type": "gt"
#         },
#         "operator": {
#             "type": "and"
#         },
#         "query": {
#             "params": [
#             "A"
#             ]
#         },
#         "reducer": {
#             "params": [],
#             "type": "last"
#         },
#         "type": "query"
#         }
#     ],
#     "datasource": {
#         "type": "__expr__",
#         "uid": "-100"
#     },
#     "hide": false,
#     "intervalMs": 1000,
#     "maxDataPoints": 43200,
#     "refId": "B",
#     "type": "classic_conditions"
# }
# EOT
#     }
#   }
}