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
    [sssd]
    domains = ${domain_ldap}
    config_file_version = 2
    services = nss, pam, sudo, ssh

    [sudo]

    [domain/${domain_ldap}]
    ldap_user_search_base = ${ldap_user_search_base}%{ for ad_group in ad_groups ~}?DC=btgroup,DC=io?subtree?(memberOf=CN=${ad_group},OU=BT_Groups,DC=btgroup,DC=io)%{ endfor ~}?DC=btgroup,DC=io?subtree?(memberOf=CN=acl-ssh-${vm_name},OU=BT_Groups,DC=btgroup,DC=io)
    ldap_sudo_search_base = ${ldap_sudo_search_base}
    ad_enabled_domains = ${domain_ldap}
    default_shell = /bin/bash
    krb5_store_password_if_offline = True
    cache_credentials = True
    krb5_realm = ${uppercase_domain_ldap}
    realmd_tags = manages-system joined-with-adcli 
    id_provider = ad
    fallback_homedir = /home/%u@%d
    ad_domain = ${domain_ldap}
    use_fully_qualified_names = True
    ldap_id_mapping = True
    access_provider = ad
    ldap_user_extra_attrs = sshPublicKeys:sshPublicKeys
    ldap_user_ssh_public_key = sshPublicKeys
    ldap_use_tokengroups = True


runcmd:
- hostnamectl hostname ${vm_name}
- timedatectl set-timezone Europe/Paris
- rm /etc/netplan/50-cloud-init.yaml
- chmod -R go-rwx /etc/netplan
- netplan apply
- echo "waiting 10s"
- sleep 10
- service ssh stop
- LANG=C sudo apt-file update && LANG=C sudo apt update && LANG=C sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=l NEEDRESTART_SUSPEND=1 apt-get dist-upgrade -y
- echo "${password_user_ldap_join}" | realm join -v -U ${user_ldap_join} ${domain_ldap} --computer-ou="${ou_ldap}"
#- LANG=C sudo apt-file update && LANG=C sudo apt update && LANG=C sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=l NEEDRESTART_SUSPEND=1 apt-get dist-upgrade -y && echo "${password_user_ldap_join}" | realm join -v -U ${user_ldap_join} ${domain_ldap} --computer-ou="${ou_ldap}" && rm /var/cache/apt/archives/* ; LANG=C sudo update-initramfs -u -k all && LANG=C sudo update-grub
- cp /root/temporary /etc/sssd/sssd.conf
- sssctl cache-remove -o -p -s && sss_cache -E && service sssd restart
- rm /root/temporary
- userdel -r ubuntu
- apt list --upgradable -a && if test -f /var/run/reboot-required ; then banner reboot && sync && sync && sync && sudo reboot ; else service ssh start ; fi
- eject

# package_update: true
# package_upgrade: true
# packages:
#   - apt-transport-https
