#!/usr/bin/env python3

import json
import time
from multiprocessing.connection import wait
import requests
import subprocess
import logging

def main():
    ####################################################
    # Modify these variables to match your environment #
    ####################################################
    nautobot = 'http://192.168.101.7/api/dcim/devices/?serial=' # Nautobot server, should just need to modify IP
    token = '2b501faae646e9fd686513bf7ef2e6852f43b30a' # Nautobot API token
    tftp = '192.168.101.40' # TFTP server IP
    ztpfile = 'ztp-config' # ZTP config file
    firmware = ''
    ####################################################

    serial = subprocess.getoutput("FastCli -p 15 -c 'show version | json'")
    snjson = json.loads(serial)
    
    nauto = requests.get(nautobot + snjson['serialNumber'], 
            headers={"Authorization": "Token %s" % token})
    match = nauto.json()
    
    if match['results'][0]['name'] != '':
        subprocess.check_output("FastCli -p 15 -c 'copy tftp://%s/ztp/%s running-config'" % (tftp, ztpfile), shell=True)
        subprocess.check_output("FastCli -p 15 -c $'config\nhostname %s'" % match['results'][0]['name'], shell=True)
        subprocess.check_output("FastCli -p 15 -c 'write memory'", shell=True)
        if firmware != '':
            subprocess.check_output("FastCli -p 15 -c 'copy tftp://%s/ztp/%s flash:%s'" % (tftp, firmware, firmware), shell=True)
    else:
        logging.error('No match found in Nautobot')

#########################
# Execute Main function #
#########################
if __name__ == '__main__':
   main()
