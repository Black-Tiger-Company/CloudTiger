# ############
# # YARN (dataproc for GCP)
# ############

resource "google_dataproc_cluster" "yarn" {
  name   = var.yarn.name
  region = var.yarn.region

   cluster_config {
    #staging_bucket = "dataproc-staging-bucket-eg-12342"

    master_config {
      num_instances = var.yarn.master_instance_number
      machine_type  = var.yarn.master_instance_type
      disk_config {
        boot_disk_type    = "pd-ssd" # pd-ssd or pd-standard
        boot_disk_size_gb = 30       # min 10G, default 500G
      }
    }

    worker_config {
      num_instances    = var.yarn.worker_instance_number
      machine_type     = var.yarn.worker_instance_type
      disk_config {
        boot_disk_size_gb = 30
        num_local_ssds    = 1
      }
    }

    # gce_cluster_config {
    #     #tags = [format("%s%s_yarn", var.yarn.module_prefix, var.yarn.name)]
    #     #subnetwork = var.yarn.subnetworks[0] # only one subnet :(
    # }

    autoscaling_config {
      policy_uri = google_dataproc_autoscaling_policy.dataproc_autoscaling_policy.name
    }

  }

  labels = {
       name = var.yarn.name
  }

}

resource "google_dataproc_autoscaling_policy" "dataproc_autoscaling_policy" {
  policy_id = "dataproc-policy"
  location  = var.yarn.region

  worker_config {
    max_instances = 3
  }

  basic_algorithm {
    yarn_config {
      graceful_decommission_timeout = "30s"

      scale_up_factor   = 0.5
      scale_down_factor = 0.5
    }
  }
}

# # Soumettre un exemple de tâche pyspark à un cluster dataproc
# resource "google_dataproc_job" "pyspark" {
#     region       = "${google_dataproc_cluster.yarn.region}"
#     force_delete = true
#     placement {
#         cluster_name = "${google_dataproc_cluster.yarn.name}"
#     }

#     pyspark_config {
#         main_python_file_uri = "gs://eg-blacktiger/pyspark/wordcount.py"
#         properties = {
#             "spark.logConf" = "true"
#         }
#     }
# }

resource "google_dataproc_workflow_template" "workflow_template" {
  name = "cluster-demo-cloudtiger"
  location = var.yarn.region
  placement {
    cluster_selector {
      cluster_labels = {
         name = var.yarn.name
      }
    }
  }
  jobs {
    step_id = var.yarn.jobs[0].step_id
    pyspark_job {
      main_python_file_uri = var.yarn.jobs[0].main_file_uri
    }
  }
}


# resource "google_dataproc_workflow_template" "template" {
#   name = "workflow_template-eg"
#   location = var.yarn.region
#   placement {
#     managed_cluster {
#       cluster_name = "cluster-workflow-template"
#       config {
#         master_config {
#           num_instances = 1
#           machine_type = "n1-standard-2"
#           disk_config {
#             boot_disk_type = "pd-ssd"
#             boot_disk_size_gb = 30
#           }
#         }
#         worker_config {
#           num_instances = 2
#           machine_type = "n1-standard-2"
#           disk_config {
#             boot_disk_size_gb = 30
#             num_local_ssds = 2
#           }
#         }
#       }
#     }
#   }
#   jobs {
#     step_id = "wordCount"
#     pyspark_job {
#       main_python_file_uri = "gs://eg-blacktiger/pyspark/wordcount.py"
#     }
#   }
# }


# test dataflow

# resource "google_dataflow_job" "big_data_job" {
#   name              = "dataflow-job"
#   template_gcs_path = "gs://eg-blacktiger/test.py"
#   temp_gcs_location = "gs://dataflow/tmp_dir"
# }
