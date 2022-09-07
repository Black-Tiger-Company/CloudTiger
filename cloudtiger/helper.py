"""
This file stores the 'helpers' strings for unit tests
"""

helpers = {
    "basic": """Usage: main [OPTIONS] SCOPE COMMAND [ARGS]...\n\n  Cloud Tiger is a CLI tool for creating, configuring and managing\n  infrastructures.\n\nOptions:\n  --version                  Show the version and exit.\n  -p, --project-root TEXT    set the gitops project root\n  -l, --libraries-path TEXT  set a custom folder of libraries for Terraform\n                             modules and Ansible playbooks\n  -o, --output-file TEXT     define a file path for dumping outputs of\n                             CloudTiger\n  -e, --error-file TEXT      define a file path for dumping erros of CloudTiger\n  -r, --recursive            this option will apply your command recursively on\n                             all scope folders insidecurrent folder\n  -v, --verbose              set logger to verbose mode\n  -h, --help                 Show this message and exit.\n\nCommands:\n  ans      Ansible actions\n  init     init actions\n  service  service configuration\n  tf       Terraform actions\n"""
}
