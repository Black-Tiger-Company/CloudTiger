"""
This file stores the 'helpers' strings for unit tests
"""

helpers = {
    "basic": """Cloud Tiger is a CLI tool for creating, configuring and managing
  infrastructures.

Options:
  --project-root, --r TEXT    set the gitops project root
  --libraries-path, --l TEXT  set a custom folder of libraries for Terraform
                              modules and Ansible playbooks
  --output-file, --o TEXT     define a file path for dumping outputs of
                              CloudTiger
  --error-file, --e TEXT      define a file path for dumping erros of CloudTiger
  --recursive, --r            this option will apply your command recursively on
                              all scope folders inside current folder
  --help                      Show this message and exit.

Commands:
  ans   Ansible actions
  init  init actions
  tf    Terraform actions
"""
}
