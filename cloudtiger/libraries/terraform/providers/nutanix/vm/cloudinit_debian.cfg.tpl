#cloud-config
hostname: ${vm_name}
password: debian
chpasswd: { expire: False }
ssh_pwauth: True

write_files:
- path: /etc/network/interfaces.d/00-installer-config
  permissions: '0644'
  content: |
    # static IP address
    auto ${interface}
    iface ${interface} inet static
     address ${vm_address}
     netmask ${netmask}
     gateway ${vm_gateway}
- path: /etc/resolvconf/resolv.conf.d/base
  permissions: '0644'
  content: |
    %{ for nameserver in nameservers ~}
    nameserver ${nameserver}
    %{ endfor ~}

runcmd:
- service networking restart
- service resolvconf restart
