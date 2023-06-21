terraform {
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = ">= 0.13.0"
    }
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.42.0"
    }
  }
}


######################
# SSH Keys
######################

resource "openstack_compute_keypair_v2" "test_keypair" {
  # provider   = openstack.ovh
  name       = var.key.key_name
  public_key = var.key.public_key
}
