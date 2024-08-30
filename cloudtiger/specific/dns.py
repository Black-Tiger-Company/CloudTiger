import sys
from pypsrp.client import Client
from cloudtiger.cloudtiger import Operation

def dns_login(operation: Operation, dns_server, user, password):

    """ this function provides a login to a Windows DNS server """

    try:
        ms_connection = Client(dns_server, username=user, password=password, ssl=False)
    except:
        operation.logger.error("Windows server authentication error")
        raise TypeError("Windows server authentication error")
        sys.exit()

    return ms_connection

def dns_add_a_record(operation: Operation, hostname, ip_address, zonename, ms_connection):

    """ this function add an A record to a Windows DNS server """

    powershell_script = f"""
        $result = @(Add-DnsServerResourceRecordA -Name {hostname} -ZoneName {zonename} -AllowUpdateAny -IPv4Address {ip_address} -TimeToLive 01:00:00 -CreatePtr)
        $isnoerror = $?      
        $error = $error
        $res = $result + $isnoerror + $error
        Write-Output $res
        """

    output, streams, had_errors = ms_connection.execute_ps(powershell_script)
    operation.logger.info("Adding A record :")
    operation.logger.info(f"output : {output}")
    operation.logger.info(f"streams : {streams}")
    operation.logger.info(f"had_errors : {had_errors}")

    return output

def dns_add_ptr_record(operation: Operation, hostname, ip_address, zonename, ms_connection):

    """ this function add an PTR record to a Windows DNS server """

    powershell_script = f"""
        $result = @(Add-DnsServerResourceRecordPtr -Name {ip_address} -ZoneName {zonename} -AllowUpdateAny -PtrDomainName  {hostname} -TimeToLive 01:00:00)
        $isnoerror = $?      
        $error = $error
        $res = $result + $isnoerror + $error
        Write-Output $res
        """

    output, streams, had_errors = ms_connection.execute_ps(powershell_script)
    operation.logger.info("Adding PTR record :")
    operation.logger.info(f"output : {output}")
    operation.logger.info(f"streams : {streams}")
    operation.logger.info(f"had_errors : {had_errors}")

    return output

def get_reverse_lookup_zone(ip_address):
    # Split the IP address into octets
    octets = ip_address.split('.')

    # Reverse the order of the octets
    reversed_octets = octets[:3][::-1]

    # Join the reversed octets with dots and append the domain suffix
    reverse_lookup_zone = '.'.join(reversed_octets) + '.in-addr.arpa'

    return reverse_lookup_zone


def dns_add_reverse_lookup_zone(operation: Operation, zonename, ip_address,  ms_connection):

    """ this function add a Reverse lookup zone to a Windows DNS server """
    reverse_lookup_zone = get_reverse_lookup_zone(ip_address)
    operation.logger.info(f"Check Reverse lookup zone {reverse_lookup_zone}")

    list_reverse_lookup_zone_powershell_script = f"""
        $result = @(Get-DnsServerZone | ? {{ $_.IsReverseLookupZone -eq $true -and $_.IsAutoCreated -eq $false }}).ZoneName
        Write-Output $result
        """

    cidr=".".join(ip_address.split('.')[0:3]) + ".0/24"
    create_reverse_lookup_zone_powershell_script = f"""
        $result = @(Add-DnsServerPrimaryZone -NetworkID "{cidr}" -ReplicationScope "Domain")
        $isnoerror = $?
        $error = $error
        $res = $result + $isnoerror + $error
        Write-Output $res
        """
    
    output, streams, had_errors = ms_connection.execute_ps(list_reverse_lookup_zone_powershell_script)
    list_reverse = output.split('\n')
    operation.logger.info(f"Search if {reverse_lookup_zone} exists in reverse lookup zone list")
    print(list_reverse)
    if reverse_lookup_zone in list_reverse:
        operation.logger.info(f"{reverse_lookup_zone} alreay exists")
    else:
        operation.logger.info(f"Nod Found => Creation of {reverse_lookup_zone} in CIDR {cidr}")
        output, streams, had_errors = ms_connection.execute_ps(create_reverse_lookup_zone_powershell_script)
        operation.logger.info(f"output : {output}")
        operation.logger.info(f"had_errors : {had_errors}")

    return output


def dns_delete_a_record(operation: Operation, hostname, ip_address, zonename, ms_connection):

    """ this function add an PTR record to a Windows DNS server """

    powershell_script = f"""
        $result = @(Remove-DnsServerResourceRecord -Name {hostname} -ZoneName {zonename} -RecordData {ip_address} -RecordType "A")
        $isnoerror = $?      
        $error = $error
        $res = $result + $isnoerror + $error
        Write-Output $res
        """

    output, streams, had_errors = ms_connection.execute_ps(powershell_script)
    operation.logger.info("Deleting A record :")
    operation.logger.info(f"output : {output}")
    operation.logger.info(f"streams : {streams}")
    operation.logger.info(f"had_errors : {had_errors}")

    return output

def dns_delete_ptr_record(operation: Operation, hostname, ip_address, zonename, ms_connection):

    """ this function add an PTR record to a Windows DNS server """

    powershell_script = f"""
        $result = @(Remove-DnsServerResourceRecord -Name {ip_address} -ZoneName {zonename} -PtrDomainName  {hostname} -RecordType "PTR")
        $isnoerror = $?      
        $error = $error
        $res = $result + $isnoerror + $error
        Write-Output $res
        """

    output, streams, had_errors = ms_connection.execute_ps(powershell_script)
    operation.logger.info("Deleting PTR record :")
    operation.logger.info(f"output : {output}")
    operation.logger.info(f"streams : {streams}")
    operation.logger.info(f"had_errors : {had_errors}")

    return output


