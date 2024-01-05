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

write_files:
- path: /etc/netplan/00-installer-config.yaml
  permissions: '0644'
  content: |
    # This is the network config written by 'subiquity'
    network:
      version: 2
      renderer: networkd
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
        search:
    %{ for search_addr in search ~}
        - ${search_addr}
    %{ endfor ~}
      routes:
          - to: default
            via: ${vm_gateway}

- path: /root/temporary
  permissions: '0600'
  content: |
    --- /etc/sssd/sssd.conf~    2023-12-13 19:14:57.000000000 +0100
    +++ /etc/sssd/sssd.conf    2023-12-13 19:19:02.156374438 +0100
    @@ -1,8 +1,10 @@
    -
     [sssd]
     domains = btgroup.io
     config_file_version = 2
    -services = nss, pam
    +services = nss, pam, sudo, ssh
    +
    +[sudo]
    +
    
     [domain/btgroup.io]
     default_shell = /bin/bash
    @@ -16,3 +18,6 @@
     use_fully_qualified_names = True
     ldap_id_mapping = True
     access_provider = ad
    +ldap_user_extra_attrs = sshPublicKeys:sshPublicKeys
    +ldap_user_ssh_public_key = sshPublicKeys
    +ldap_use_tokengroups = True

runcmd:
- rm /etc/netplan/50-cloud-init.yaml
- netplan apply
- echo "${password_user_ldap_join}" | realm join -U ${user_ldap_join} ${domain_ldap} --computer-ou=${ou_ldap}
- cd / && patch -p0 -i /root/temporary
- sssctl cache-remove -o -p -s && sss_cache -E && service sssd restart && service ssh restart

package_update: true
package_upgrade: true
packages:
  - apt-transport-https
