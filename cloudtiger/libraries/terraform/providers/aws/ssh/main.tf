######################
# SSH Keys
######################

resource "aws_key_pair" "public_key_import" {
  key_name   = var.key.key_name
  public_key = var.key.public_key
}