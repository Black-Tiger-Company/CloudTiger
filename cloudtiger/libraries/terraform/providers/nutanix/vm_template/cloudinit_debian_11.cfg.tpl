#cloud-config
hostname: ${vm_name}
password: ${password}
chpasswd: { expire: False }
ssh_pwauth: false

users:
  - name: ubuntu
    lock-passwd: false  # Allow password login
    passwd: ${password}  # Specify the password here
    groups: sudo
    shell: /bin/bash
%{ for user in users_list ~}
  - name: ${ user.name }
    ssh-authorized-keys:
%{ for key in user.public_key ~}
      - ${ key }
%{ endfor ~}
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
%{ endfor ~}

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
- path:  /etc/systemd/resolved.conf
  permissions: '0644'
  content: |
    # This file is part of systemd.
    #
    # systemd is free software; you can redistribute it and/or modify it
    # under the terms of the GNU Lesser General Public License as published by
    # the Free Software Foundation; either version 2.1 of the License, or
    # (at your option) any later version.
    #
    # Entries in this file show the compile time defaults.
    # You can change settings by editing this file.
    # Defaults can be restored by simply deleting this file.
    #
    # See resolved.conf(5) for details

    [Resolve]
    DNS=%{ for nameserver in nameservers ~}${nameserver} %{ endfor ~}
    #FallbackDNS=
    Domains=%{ for search_addr in search ~}${search_addr} %{ endfor ~}
    #LLMNR=yes
    #MulticastDNS=yes
    #DNSSEC=allow-downgrade
    #DNSOverTLS=no
    #Cache=yes
    #DNSStubListener=yes
    #ReadEtcHosts=yes

runcmd:
- service networking restart
- systemctl disable systemd-resolved
- systemctl enable systemd-resolved
- ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
- systemctl restart systemd-resolved
