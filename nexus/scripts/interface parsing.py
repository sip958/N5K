from nexus.models import *
from os.path import join
from xlwings import Workbook, Range

import sys
import os, time
import string
import re
import dateparser
import datetime
from netaddr import *
from marshmallow import Schema, fields, ValidationError, pprint


def apple_finder(file,apple):
    for line in file:
        if apple in line:
             yield line

def all_apples_finder(file,apples):
    for line in file:
        if all(x in line for x in apples):
            yield line


def all_files_with_path(some_file_name,some_path):
    for root, dirs, files in os.walk(some_path):
        for curfile in files:
            if some_file_name in curfile:
                yield join(root, curfile)


def ios_show_interface(file_with_path, hostname):
    file_opened = open(file_with_path,'r')
    blocks = re.split('\r\n(?=[A-Z][a-zA-Z]*.*line protocol)', file_opened.read())
    interface = []
    blocks.pop(0)
    for block in blocks:
        block = block.replace("\r\n","\n")
        local_interface = ""
        desc = ""
        status = ""
        operate_mode = ""
        for line in block.split("\n"):
            if (", line protocol is" in line) and not ("Null0" in line):
                local_interface, physical_status = line.split(", line protocol is")[0].split("is")
                local_interface = local_interface.strip()
                physical_status = physical_status.strip()
                status = line.split(", line protocol is")[1].strip()
            if local_interface:
                if "Description:" in line:
                    desc = line.split("Description:")[1].strip()
        if local_interface:
            #print local_interface,mac_address,desc,ip,bw
            interface_temp = Interfaces(local_interface, desc, status, operate_mode)
            interface_old = Interfaces.query.filter_by(hostname = hostname).first()
            if interface_old:
                #print device_old.hostname
                interface_old.desc = desc
                interface_old.status = status
                interface_old.operate_mode = operate_mode
            else:
                db.session.add(interface_temp)
            db.session.commit()
    return


def nox_show_interface(file_with_path, hostname):
    file_opened = open(file_with_path,'r')
    blocks = re.split('\r\n *\r\n', file_opened.read())
    interface = []
    for block in blocks:
        block = block.replace("\r\n","\n")
        local_interface = ""
        mac_address = ""
        desc = ""
        ip = ""
        bw1 = 0
        Port_mode = ""
        for line in block.split("\n"):
            if ("is up" in line) and not ("admin state is up" in line):
                local_interface = line.split()[0]
            if local_interface:
                if ("Hardware:" in line) and ("address:" in line):
                    mac_address = line.split("address:")[1].split()[0]
                elif "Description:" in line:
                    desc = line.split("Description:")[1].strip()
                elif "Internet Address is" in line:
                    ip = line.split("Internet Address is")[1].strip()
                elif ("BW " in line) and ("Loopback" not in local_interface) :
                    bw = line.split("BW ")[1].split("(")[0].strip()
                    if "Kbit" in bw:
                        bw1 = int(bw.split()[0])
                elif "Port mode is " in line :
                    Port_mode = line.split("Port mode is")[1].strip()
                #print local_interface,mac_address,desc,ip,bw
        if local_interface:
            #print local_interface,mac_address,desc,ip,bw
            interface.append(dict(Port_mode = Port_mode,source = hostname, source_interface = local_interface, mac_address = mac_address, description = desc, source_ip = ip, bandwidth = bw1))
    return interface



root_folder = '/Users/yijxiang/Desktop/1/topology_design/new_info/0621_info/20160619060001-048d7b82cd60-inetworks/'
file_name_show_interface = "show interface.log"

interface_list = []

for one_file_with_path in all_files_with_path(file_name_show_interface, root_folder):
    file_create_time = dateparser.parse(time.ctime(os.path.getctime(one_file_with_path)))
    hostname, ip_address, temp =  os.path.basename(one_file_with_path).split('_')
    if not IPAddress(ip_address).is_unicast():
        print "error, no ip address information in the file folder"


    if ("65" in hostname) or ("76" in hostname) or ("72" in hostname) or ("49" in hostname) or ("35" in hostname) or ("36" in hostname) or ("37" in hostname) or ("38" in hostname) or ("39" in hostname) or ("45" in hostname) or ("29" in hostname):
        ios_show_interface(one_file_with_path, hostname, ip_address)
    elif ("55SW" in hostname) or ("70SW" in hostname) or ("30SW" in hostname) or ("50SW" in hostname) or ("70WA" in hostname) or ("56SW" in hostname):
        nox_show_interface(one_file_with_path, hostname, ip_address)
    elif ("BL" in hostname) :
        ios_show_interface(one_file_with_path, hostname, ip_address)
    else:
        print hostname

