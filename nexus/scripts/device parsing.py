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



def ios_bl_show_version(file_with_path, hostname, IP):
    for line in open(file_with_path,'r'):
        if "Cisco IOS" in line:
            if "BOOTLDR" not in line:
                ios = line.split(',')
                if len(ios) == 4:
                    ios_type, ios_features, ios_version, ios_release = ios
                if len(ios) == 3:
                    ios_type = "Cisco IOS Software"
                    ios_features, ios_version, ios_release = ios
                if len(ios) == 5:
                    ios_type, ios_features, ios_version, ios_release, temp = ios
                SW_type = "Cisco IOS Software"
                SW_version = ios_version.replace("Version","").strip()
            #print ios_type,ios_version
        elif "uptime is" in line:
            hostname, uptime = line.split('uptime is')
            hostname = hostname.strip()
            uptime = dateparser.parse(uptime)
        elif "bytes of memory" in line:
            platform, memory_size = line.split('K bytes of memory.')[0].split('processor')
            platform = platform.split('(')[0].upper().replace("CISCO","").strip()
            memory_size = float(memory_size.split(")")[1].replace("with", "").strip())
            #print platform, memory_size
    updated_by = datetime.datetime.now()
    device_temp = Device(hostname, IP, platform, SW_type, SW_version, uptime, memory_size, updated_by)
    device_old = Device.query.filter_by(hostname = hostname).first()
    if device_old:
        #print device_old.hostname
        device_old.IP = IP
        device_old.platform = platform
        device_old.SW_type = SW_type
        device_old.SW_version = SW_version
        device_old.uptime = uptime
        device_old.memory_size = memory_size
        device_old.updated_by = updated_by
    else:
        db.session.add(device_temp)
    db.session.commit()
    return

def ios_show_version(file_with_path, hostname, IP):
    for line in open(file_with_path,'r'):
        if "IOS" in line:
            if ("BOOTLDR" not in line) or ("Target" not in line):
                ios = line.split(',')
                if len(ios) == 4:
                    SW_type, ios_features, ios_version, ios_release = ios
                if len(ios) == 3:
                    ios_features, ios_version, ios_release = ios
                SW_type = "Cisco IOS Software"
                SW_version = ios_version.replace("Version","").strip()
            #print ios_type,ios_version
        elif "uptime is" in line:
            uptime = line.split('uptime is')[1]
            uptime = dateparser.parse(uptime)
        elif "bytes of memory" in line:
            # processor for CAT49, else
            if "processor" in line:
                platform, memory_size = line.split('K bytes of memory')[0].split('processor')
                memory_size = memory_size.split(")")[1].replace("with", "").strip()
            else:
                temp = line.split('K bytes of memory')[0].split('with')
                if len(temp) ==3:
                    platform, temp1, memory_size = temp
                elif len(temp) ==2:
                    platform, memory_size = temp
            if "K/" in memory_size:
                memory_size_temp = memory_size.split("K/")
                memory_size = float(memory_size_temp[0]) + float(memory_size_temp[1])
            else:
                memory_size = float(memory_size)
            platform = platform.split('(')[0].upper().replace("CISCO","").strip()

            #print platform, memory_size
    updated_by = datetime.datetime.now()
    device_temp = Device(hostname, IP, platform, SW_type, SW_version, uptime, memory_size, updated_by)
    device_old = Device.query.filter_by(hostname = hostname).first()
    if device_old:
        #print device_old.hostname
        device_old.IP = IP
        device_old.platform = platform
        device_old.SW_type = SW_type
        device_old.SW_version = SW_version
        device_old.uptime = uptime
        device_old.memory_size = memory_size
        device_old.updated_by = updated_by
        #db.session.commit()
    else:
        db.session.add(device_temp)
    db.session.commit()
    return


def nos_show_version(file_with_path, hostname, IP):
    for line in open(file_with_path,'r'):
        if "system:    version" in line:
            SW_type = "Cisco Nexus Operating System (NX-OS)"
            SW_version = line.split('system:    version')[1].strip()
        elif "Kernel uptime is" in line:
            uptime = dateparser.parse(line.split('Kernel uptime is')[1])
        elif "Chassis" in line:
            platform = line.split('Chassis')[0].split('(')[0].upper().replace("CISCO","").strip()
            if "NEXUS7000" in platform:
                platform = platform.split()[0]
        elif "memory" in line:
            memory_size = float(line.split('with')[1].split("kB of memory")[0].strip())
    updated_by = datetime.datetime.now()
    device_temp = Device(hostname, IP, platform, SW_type, SW_version, uptime, memory_size, updated_by)
    device_old = Device.query.filter_by(hostname = hostname).first()
    if device_old:
        #print device_old.hostname
        device_old.IP = IP
        device_old.platform = platform
        device_old.SW_type = SW_type
        device_old.SW_version = SW_version
        device_old.uptime = uptime
        device_old.memory_size = memory_size
        device_old.updated_by = updated_by
    else:
        db.session.add(device_temp)
    db.session.commit()
    return



root_folder = '/Users/yijxiang/Desktop/1/topology_design/new_info/0621_info/20160619060001-048d7b82cd60-inetworks/'
file_name_show_version = 'show version.log'

file_name_show_cdp_neighbor_detail = "show cdp neighbor detail.log"
file_name_show_interface = "show interface.log"
file_name_nos_show_interface = "show interface.log"
file_name_show_running_config = "show running-config.log"
dict_ip_hostname = {}

device_list = []

for one_file_with_path in all_files_with_path(file_name_show_version, root_folder):
    #print one_file_with_path
    file_create_time = dateparser.parse(time.ctime(os.path.getctime(one_file_with_path)))
    hostname, ip_address, temp =  os.path.basename(one_file_with_path).split('_')
    if not IPAddress(ip_address).is_unicast():
        print "error, no ip address information in the file folder"

    if ("65" in hostname) or ("76" in hostname) or ("72" in hostname) or ("49" in hostname) or ("35" in hostname) or ("36" in hostname) or ("37" in hostname) or ("38" in hostname) or ("39" in hostname) or ("45" in hostname) or ("29" in hostname):
        ios_show_version(one_file_with_path, hostname, ip_address)
    elif ("55SW" in hostname) or ("70SW" in hostname) or ("30SW" in hostname) or ("50SW" in hostname) or ("70WA" in hostname) or ("56SW" in hostname):
        nos_show_version(one_file_with_path, hostname, ip_address)
    elif ("BL" in hostname) :
        ios_bl_show_version(one_file_with_path, hostname, ip_address)
    else:
        print hostname

