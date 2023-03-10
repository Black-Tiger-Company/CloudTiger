#cloud-config
hostname: ${vm_name}
password: ubuntu
chpasswd: { expire: False }
ssh_pwauth: True
keyboard:
  layout: fr

write_files:
- path: /etc/netplan/00-installer-config.yaml
  permissions: '0644'
  content: |
    network:
      version: 2
      ethernets:
        ${interface}:
          dhcp4: no
          addresses:
          - ${vm_address}/${netmask}
          gateway4: ${vm_gateway}
          nameservers:
            addresses: 
    %{ for nameserver in nameservers ~}
            - ${nameserver}
    %{ endfor ~}
        search:
    %{ for search_addr in search ~}
            - ${search_addr}
    %{ endfor ~}

runcmd:
- netplan apply