Role Name
=========

A brief description of the role goes here.

Requirements
------------

This role assumes your directory structure is this way
```
$ tree
├── playbook.yml
├── group_vars
│   └── all
│       └── config
├── hosts
└── requirements.yml
```

Role Variables
--------------

No variable required

Dependencies
------------

Before using, you must install the role locally
```
ansible-galaxy install -r requirements.yml
```

Example Playbook
----------------

A playbook using *haproxy* should look like
```
  - name: install and configure haproxy
    hosts: haproxy
    become: yes
    gather_facts: no
    become_method:
    tasks:
      - name: install and configure haproxy
        import_role:
          name: haproxy
        vars:
          download_certificates_list:
            - src: repository/certificates.txt
              dest: /etc/ssl/platform/platform.tech.pem
```
Then you can run it
```
ansible-playbook -i hosts playbook.yml
```

License
-------


Author Information
------------------
