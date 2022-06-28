variable "key" {
  type = object({
    key_name   = string
    public_key = string
  })
  description = "Public SSH Key for VM ssh access"
}
