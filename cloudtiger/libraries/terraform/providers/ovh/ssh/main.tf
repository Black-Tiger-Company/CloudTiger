######################
# SSH Keys
######################

resource "openstack_compute_keypair_v2" "test_keypair" {
  provider   = openstack.ovh
  name       = var.key.key_name
  public_key = var.key.public_key
}
