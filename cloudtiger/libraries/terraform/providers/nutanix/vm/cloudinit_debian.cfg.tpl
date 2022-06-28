#cloud-config
hostname: debian
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
     # dns-* options are implemented by the resolvconf package, if installed
     dns-nameservers %{ for nameserver in nameservers } ${nameserver}%{ endfor }

runcmd:
- service networking restart

