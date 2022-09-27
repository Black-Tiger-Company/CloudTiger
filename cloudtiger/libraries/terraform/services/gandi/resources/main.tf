
resource "gandi_livedns_record" "livedns_record" {
    count = len(var.gandi_config.dns_records) # for_each
    zone = var.gandi_config.dns_records[count.index].zone #"example.com"
    name = var.gandi_config.dns_records[count.index].name
    type = var.gandi_config.dns_records[count.index].type
    ttl = 3600
    values = var.gandi_config.dns_records[count.index].ips
  }