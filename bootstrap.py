#!/usr/bin/env python3

import json
import urllib
import subprocess
import logging

def main():
    ####################################################
    # Modify these variables to match your environment #
    ####################################################
    nautobot = 'http://192.168.101.7/api/dcim/devices/?serial=' # Nautobot server, should just need to modify IP
    token = '2b501faae646e9fd686513bf7ef2e6852f43b30a' # Nautobot API token
    tftpbase = '192.168.101.40/ztp/' # TFTP server information
    ztpconfig = 'ztp-config' # ztp config file
    firmware = '' # firmware file
    ####################################################

    serial = subprocess.getoutput("FastCli -p 15 -c 'show version | json'")
    snjson = json.loads(serial)
    
    
    nauto = urllib.request.Request(nautobot + snjson['serialNumber'], 
            headers={"Authorization": "Token %s" % token})
    try:
        with urllib.request.urlopen(nauto) as httpresponse:
            info = (httpresponse.read().decode())

    except:
        logging.error('Unable to open connection to nautobot')
    
    match = json.loads(info)
    
    if match['results']:
        subprocess.check_output("FastCli -p 15 -c 'copy tftp://%s%s running-config'" % (tftpbase, ztpconfig), shell=True)
        subprocess.check_output("FastCli -p 15 -c $'config\nhostname %s'" % match['results'][0]['name'], shell=True)
        subprocess.check_output("FastCli -p 15 -c 'write memory'", shell=True)
        if firmware != '':
            subprocess.check_output("FastCli -p 15 -c 'copy tftp://%s%s flash:%s'" % (tftpbase, firmware, firmware), shell=True)
    else:
        logging.error('No match found in Nautobot')
        subprocess.check_output("FastCli -p 15 -c 'copy tftp://%s%s flash:startup-config'" % (tftpbase, ztpconfig), shell=True)
        if firmware != '':
            subprocess.check_output("FastCli -p 15 -c 'copy tftp://%s%s flash:%s'" % (tftpbase, firmware, firmware), shell=True)

#########################
# Execute Main function #
#########################
if __name__ == '__main__':
   main()