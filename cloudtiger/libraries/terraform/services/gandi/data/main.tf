terraform {
  required_providers {
    gandi = {
      version = "2.1.0"
      source   = "go-gandi/gandi"
    }
  }
}

 
 resource "gandi_livedns_domain" "livedns_domain" {
      name = var.gandi_config.domains[0].name
}