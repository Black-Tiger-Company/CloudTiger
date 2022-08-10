from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, constr, NegativeInt, IPvAnyAddress, IPvAnyInterface, validator, root_validator

#typing.Union

class DatacenterEnum(str, Enum):
    bnc = 'BNC'

class EnvironmentEnum(str, Enum):
    prod = 'prod'
    preprod = 'preprod'

#IPvAnyAddress
IP_ADRESS = constr(regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
#IPvAnyInterface (or IPv4Network ?)
CIDR_BLOCK = constr(regex="^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]){1}(\/([0-9]|[1-2][0-9]|3[0-2]))?$")
# Version
VERSION = constr(regex="^(\d{1,2}\.\d{1,2}\.\d{1,3})$")

class Subnet(BaseModel):
    availability_zone: str
    cidr_block: IPvAnyInterface
    gateway_ip_address: IPvAnyAddress
    nameservers: List[IPvAnyAddress]
    network_interface: str
    unmanaged: bool
    managed_ips: bool
    vlan_id: int

class Network(BaseModel):
    datacenter: DatacenterEnum
    subnets: Dict[str, Subnet]

class VmExtraParameters(BaseModel):
    DNS_suffix: str
    Gateway: IPvAnyAddress
    Host_FQDN: str
    IP_address: IPvAnyAddress
    Name_servers: IPvAnyAddress
    Netmask: IPvAnyAddress
    Network_iface: str
    annotation: str
    cdrom_backed: List[Any]
    cdrom_unbacked: List[Any]
    cpu_hot_add_enabled: bool
    cpu_limit: NegativeInt
    cpu_reservation: Optional[str] #None
    cpu_share_level: str
    custom_attributes: Dict[str, Any]
    enable_disk_uuid: bool
    enable_logging: Optional[str] #None
    folder: str
    guest_id: str
    mac_address: str
    memory_hot_add_enabled: bool
    memory_limit: NegativeInt
    memory_reservation: Optional[str] #None
    memory_share_level: str
    network_interface: str
    num_cores_per_socket: int
    resource_pool_id: str
    sata_controller_count: int
    scsi_type: str
    sync_time_with_host: bool

class VmSize(BaseModel):
    memory: int
    nb_sockets: int
    nb_vcpu_per_socket: int

class VmVolume(BaseModel):
    datastore: str
    eagerly_scrub: Optional[bool]
    index: int
    name: str
    size: int
    thin_provisioned: bool
    vmdk_path: str

class Vm(BaseModel):
    datacenter: str
    extra_parameters: VmExtraParameters
    group: str
    imported: bool
    private_ip: IPvAnyAddress
    size: VmSize
    volumes: Dict[str, VmVolume]

# class Kubernetes(BaseModel):
#     prefix: str
#     zones: List[str]
#     network: str
#     subnetworks: List[str]
#     os_username: str
#     password: str
#     system_image: str #"kubernetes"
#     instance_type: str #"k8s_worker"
#     k8s_node_groups :
#         k8s_main :
#         desired_size: 1
#         disk_size: 16
#         max_size: 1
#         min_size: 1
#         subnetwork: "datalake_replication_subnet_1"
#     ingress_rules: List["icmp","ssh","https", "http_bis", "http", "nginx_k8s", "resty_k8s", "keycloak_k8s"]
#     egress_rules: ["default"]
#     cluster_volumes :
#       first_cluster_volume :
#         size: 256
#         name: "data_disk"
#         zone: "us-east-1a"
#         type: "sc1"

class AnsibleRoleParam(BaseModel):
    chart_environment: EnvironmentEnum
    context: str
    customer: str
    kubeconfig_path: str
    repository: str
    version: VERSION
    workdir: str

class AnsibleRole(BaseModel):
    params: AnsibleRoleParam
    source: str
    
class Ansible(BaseModel):
    hosts: str
    name: str
    roles: List[AnsibleRole]
    sudo_prompt: bool
    type: str

# Main class
class Blacktiger(BaseModel):
    network: Dict[str, Network]
    vm: Dict[str, Dict[str, Dict[str, Vm]]] #1st dict: network > 2nd dict: subnet > 3rd vm
    provider: str
    ansible: List[Ansible]

    @root_validator
    def vm_network_validation(cls, values):
        network, vm = values.get('network'), values.get('vm')
        for network_key in vm.keys():
            if not network_key in network:
                raise ValueError('Network: "'+ network_key + '" in vm doesn\'t exist in network')
            for subnet_key in vm[network_key].keys():
                if not subnet_key in network[network_key].subnets:
                    raise ValueError('Subnet: "'+ subnet_key + '" in vm doesn\'t exist in network ' + network_key)
        return values
