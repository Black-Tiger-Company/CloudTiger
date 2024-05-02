# Configuration options

__WORK IN PROGRESS__

This document lists all currently available values for the options in the `config.yml` files.

## Base variables

| Variable Name | Available values | Description |
|-----------|-----------|-----------|
| provider | aws, azure, gcp, nutanix, vsphere | Cloud provider for the scope |
| region | [aws](https://awsregion.info/), [azure](https://github.com/claranet/terraform-azurerm-regions/blob/master/REGIONS.md), [gcp](https://cloud.google.com/compute/docs/regions-zones/), (nutanix, vsphere : not necessary) | available regions for each cloud |

## Network

The `network` key should have the following structure :

```yaml
network:
  <NETWORK_NAME>:
    datacenter: <DATACENTER> # for vsphere provider only - name of the vSphere datacenter
    subnets:
      <VLAN_NAME>:
        cidr_block : # CIDR range of the VLAN - should have format 192.168.0.0/24
        gateway_ip_address : # IP address of the VLAN's gateway - should be an IPV4 address
        managed_ips : # Boolean - True if the VLAN has DHCP activated, False otherwise
        name : # Full name of the VLAN
        unmanaged : # Boolean - True if the VLAN is managed by Terraform in the current scope, False otherwise
        vlan_id : # for vsphere and nutanix only - ID of the VLAN
        nameservers: # list of IP addresses of the nameservers for this VLAN
        - xxx
        - yyy
        search: # DNS search domain configured for this VLAN
        - mydomain.com
```