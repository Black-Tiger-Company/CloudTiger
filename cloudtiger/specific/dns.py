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
        $result = @(Add-DnsServerResourceRecordA -Name {hostname} -ZoneName {zonename} -AllowUpdateAny -IPv4Address {ip_address} -TimeToLive 01:00:00)
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


