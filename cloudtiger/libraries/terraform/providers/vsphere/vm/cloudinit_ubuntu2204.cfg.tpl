#cloud-config
hostname: ${vm_name}
chpasswd: { expire: False }

ssh_pwauth: false
disable_root: true

keyboard:
  layout: fr

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
- path: /etc/netplan/00-installer-config.yaml
  permissions: '0644'
  content: |
    network:
      version: 2
      ethernets:
        ens192:
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
- chmod -R go-rwx /etc/netplan
- netplan apply

package_update: true
package_upgrade: true
packages:
  - apt-transport-https