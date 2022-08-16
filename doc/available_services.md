# Available services

This document lists services available as Terraform modules

## Cloud providers

| Functionality | Internal description | AWS | Involved services | Azure | Involved services | GCP | Involved services |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| network | providing networks and subnetworks | &check; | VPC, Subnet, NAT Gateway, Internet Gateway, Elastic IP, Route Table | &check; | Virtual Network, Subnet, Public IP, NAT Gateway, Network Security Group | &check; | Compute Network, Compute Subnetwork, Compute Address, Compute Router NAT, Compute Route |
| vm | providing standalone virtual machines | &check; | EC2 Instance, EBS Volume, Elastic IP | &check; | Virtual Machine, Network Interface, Public IP, Security Rule, Managed Disk | &check; | Compute Instance, Compute Disk, Compute Address, Compute Firewall |
| iam | roles and policies | &check; | IAM Policy, IAM Role, IAM Instance Profile | &check; | User Assigned Identity, Role, Role Assignment | - | - |

## API services

### Gitlab

| Functionality | Description | State |
|-----------|-----------|-----------|
| users | Create and manage users | experimental |

### Nexus

| Functionality | Description | State |
|-----------|-----------|-----------|
| privileges | Manages privileges | experimental |
| roles | Manages roles | experimental |
| users | Manages internal users | experimental |
| repository | Manages repositories | experimental |