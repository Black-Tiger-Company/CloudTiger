# Ansible playbooks and roles development guidelines

CloudTiger is bundled with a short list of embedded Ansible playbooks, located in `cloudtiger/libraries/ansible/playbooks`

There is also a list of standard Ansible roles from Ansible Galaxy located in `cloudtiger/libraries/ansible/requirements`

There are several ways to develop/edit roles and playbooks for CloudTiger :

- create/edit an embedded playbook
- create/edit a role

Prerequisites :

- Get a project root prepared for CloudTiger
- Install the CloudTiger CLI in "development" mode (using `pip3 install -e` option)
- Create yourself a "development" scope in the gitops project you chose
- Create yourself a target development host VM and ensure it is reachable through SSH (using `cloudtiger config/<SCOPE> ans 1`)

## Embedded playbook

Create/edit the playbook here : `cloudtiger/libraries/ansible/playbooks`.

Write a `playbook` block in the `ansible` key of your `config.yml` :

```yaml
ansible:
- name: ...
  type: playbook
  params:
    become: true
    ...
    hosts: ...
  source: ...
```

Run :

- `cloudtiger config/<SCOPE> ans P` to copy the playbooks from CloudTiger's sources to your project root
- `cloudtiger config/<SCOPE> ans 2` to load/reload the parameters in `<PROJECT_ROOT>/scopes/<SCOPE>/inventory/execute_ansible.yml`

Then run `cloudtiger config/<SCOPE> ans 3` to test the execution

## Role

You can define the sources for extra Ansible roles in your project folder by creating a file `standard/ansible_requirements.yml` inside it :

```yaml
roles:
- name: <ROLE_NAME>
  src: <ROLE_URL>
- name: ...
  ...
```

The roles defined here will be added (or override in case of name collision) to the ones in `cloudtiger/libraries/ansible/requirements` when running the command `cloudtiger config/<SCOPE> ans D`

You can create a stub for a new Ansible role with the following command :

```bash
cd <DEV_FOLDER>
ansible-galaxy init <ROLE_NAME>
```

If you want to create/edit a role with sources from your local filesystem, you can add it to the `config.yml` this way :

```yaml
ansible:
- name: ...
  type: role
  hosts: ...
  roles:
  - source: /path/to/your/role/sources/ROLE_NAME
    params:
      become: true
      ...
```

Notice that you won't need to have the role downloaded by Ansible Galaxy in this case (i.e. no need for the command `cloudtiger config/<SCOPE> ans P`) since it is loading the role from local filesystem

Run `cloudtiger config/<SCOPE> ans 2` to load/reload the parameters

Then run `cloudtiger config/<SCOPE> ans 3` to test the execution

Once the role is ready for shipping, push the sources either on a artefact repository or on a source repository, and set the repository with the role's name in `standard/ansible_requirements.yml`