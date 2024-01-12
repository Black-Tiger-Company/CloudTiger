#cloud-config
hostname: ${vm_name}
keyboard:
  layout: fr
chpasswd: #Change your local password here
    list: |
      ${user}:${password}
    expire: false
users:
  - default #Define a default user
  - name: ${user}
    gecos: ${user}
    lock_passwd: false
    groups: sudo, users, admin
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
system_info:
  default_user:
    name: ubuntu
    lock_passwd: false
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
#disable_root: false #Enable root acce
ssh_pwauth: yes #Use pwd to access (otherwise follow official doc to use ssh-keys)
power_state:
  timeout: 5
  mode: reboot

write_files:
- path: /etc/netplan/00-installer-config.yaml
  permissions: '0644'
  content: |
    network:
      version: 2
      ethernets:
        eth0:
          match:
            name: en*
          set-name: eth0
          addresses:
          - ${vm_address}/${netmask}
          nameservers:
            addresses: 
    %{ for nameserver in nameservers ~}
            - ${nameserver}
    %{ endfor ~}
      routes:
          - to: default
            via: ${vm_gateway}

runcmd:
- chmod -R go-rwx /etc/netplan
- netplan apply
- rmmod floppy
- echo "blacklist floppy" | sudo tee /etc/modprobe.d/blacklist-floppy.conf
- LANG=C sudo update-initramfs -u -k all && LANG=C sudo update-grub