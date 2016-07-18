from os.path import join
from xlwings import Workbook, Range

import sys #only needed to determine Python version number
import os, time
import string
import re
import dateparser
from netaddr import *
from marshmallow import Schema, fields, ValidationError, pprint
from pandas import DataFrame, read_csv
import pandas as pd


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


def ios_bl_show_version(file_with_path):
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
                ios_version = ios_version.replace("Version","").strip()
            #print ios_type,ios_version
        elif "uptime is" in line:
            hostname, uptime = line.split('uptime is')
            hostname = hostname.strip()
            uptime = dateparser.parse(uptime)
        elif "bytes of memory" in line:
            platform, memory_size = line.split('bytes of memory')[0].split('processor')
            platform = platform.split('(')[0].upper().replace("CISCO","").strip()
            memory_size = memory_size.split(")")[1].replace("with", "").strip()
            #print platform, memory_size
    return dict(hostname=hostname, sw_type = ios_type, sw_version = ios_version, device_uptime = uptime, device_platform = platform, device_memory = memory_size)


def ios_show_version(file_with_path):
    for line in open(file_with_path,'r'):
        if "IOS" in line:
            if ("BOOTLDR" not in line) or ("Target" not in line):
                ios = line.split(',')
                if len(ios) == 4:
                    ios_type, ios_features, ios_version, ios_release = ios
                if len(ios) == 3:
                    ios_type = "Cisco IOS Software"
                    ios_features, ios_version, ios_release = ios
                ios_version = ios_version.replace("Version","").strip()
            #print ios_type,ios_version
        elif "uptime is" in line:
            hostname, uptime = line.split('uptime is')
            hostname = hostname.strip()
            uptime = dateparser.parse(uptime)
        elif "bytes of memory" in line:
            if "processor" in line:
                platform, memory_size = line.split('bytes of memory')[0].split('processor')
                memory_size = memory_size.split(")")[1].replace("with", "").strip()
            else:
                temp = line.split('bytes of memory')[0].split('with')
                if len(temp) ==3:
                    platform, temp, memory_size = line.split('bytes of memory')[0].split('with')
                elif len(temp) ==2:
                    platform, memory_size = line.split('bytes of memory')[0].split('with')
                memory_size = memory_size.strip()
            platform = platform.split('(')[0].upper().replace("CISCO","").strip()

            #print platform, memory_size
    return dict(hostname=hostname, sw_type = ios_type, sw_version = ios_version, device_uptime = uptime, device_platform = platform, device_memory = memory_size)

def nos_show_version(file_with_path, hostname):
    for line in open(file_with_path,'r'):
        if "system:    version" in line:
            nos_type = "Cisco Nexus Operating System (NX-OS)"
            nos_version = line.split('system:    version')[1].strip()
        elif "Kernel uptime is" in line:
            uptime = dateparser.parse(line.split('Kernel uptime is')[1])
        elif "Chassis" in line:
            platform = line.split('Chassis')[0].split('(')[0].upper().replace("CISCO","").strip()
            if "NEXUS7000" in platform:
                platform = platform.split()[0]
        elif "memory" in line:
            memory_size = line.split('with')[1].replace("of memory.","").strip()
    return dict(hostname=hostname, sw_type = nos_type, sw_version = nos_version, device_uptime = uptime, device_platform = platform, device_memory = memory_size)

