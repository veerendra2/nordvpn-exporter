#!/usr/bin/python3
"""
Simple NordVPN Prometheus Exporter
"""
import re
import subprocess

from flask import Flask
from prometheus_client import make_wsgi_app, Gauge, Info, Counter

__author__ = "veerendra2"
__license__ = "Apache 2.0"
__version__ = "0.1"
__maintainer__ = "veerendra2"


app = Flask("NordVPN-Exporter")

# Define Metrics
status = Gauge('nordvpn_status', 'nordvpn status')
firewall = Gauge('nordvpn_setting_firewall',
                 'nordvpn settings firewall enabled/disabled')
kill_switch = Gauge('nordvpn_setting_kill_switch',
                    'nordvpn settings kill switch enabled/disabled')
obfuscate = Gauge('nordvpn_setting_obfuscate',
                  'nordvpn settings obfuscate enabled/disabled')
notify = Gauge('nordvpn_setting_notify',
               'nordvpn settings notify enabled/disabled')
auto_connect = Gauge('nordvpn_auto_connect',
                     'nordvpn settings auto connect enabled/disabled')
ipv6 = Gauge('nordvpn_ipv6',
             'nordvpn settings ipv6 enabled/disabled')
dns = Gauge('nordvpn_dns',
            'nordvpn settings dns enabled/disabled')
bytes_received = Counter('nordvpn_bytes_received', 'Bytes received')
bytes_sent = Counter('nordvpn_bytes_sent', 'Bytes sent')
current_server = Info('nordvpn_current_server', 'Current connected host name')
connected_country = Info('nordvpn_connected_country',
                         'Current connected country')
connected_city = Info('nordvpn_connected_city', 'Current connected city')
connected_ip = Info('nordvpn_connected_ip',
                    'Current current connected host ip')
current_tech = Info('nordvpn_current_tech', 'Current connected protocol')
current_protocol = Info('nordvpn_current_protocol',
                        'Settings protocol')
setting_tech = Info('nordvpn_setting_tech', 'nordvpn settings technology')
setting_protocol = Info('nordvpn_setting_protocol',
                        'Settings protocol')
version = Info('nordvpn_version', 'Current connected host name')
service_expiry = Info('nordvpn_service_expiry', 'Service expiry date')


def execute(option):
    try:
        output = subprocess.check_output(
            "nordvpn {}".format(option), shell=True)
        return output.decode("utf-8")
    except:
        pass
    return ''


def parse_size(size):
    units = {"B": 1, "KiB": 10**3, "MiB": 10**6, "GiB": 10**9, "TiB": 10**12}
    number, unit = [string.strip() for string in size.split()]
    return int(float(number)*units[unit])


def parse_nordvpn_cli():
    # Fetch outputs
    status_output = execute("status")
    settings_output = execute("settings")
    account_output = execute("account")
    version_output = execute("--version")

    print("Connection->", re.findall(r'(?<=Status:).*',
          status_output)[0].strip())
    print("Server->", re.findall(r'(?<=Current server:).*',
          status_output)[0].strip())
    print("Country->", re.findall(r'(?<=Country:).*',
          status_output)[0].strip())
    print("City->", re.findall(r'(?<=City:).*', status_output)[0].strip())
    print("Tech->", re.findall(r'(?<=Current technology:).*', status_output)
          [0].strip())
    rece_bytes = re.findall(r'(?<=Transfer: )(.+)received', status_output)[0]
    sent_bytes = re.findall(r'(?<=received,)(.+)sent', status_output)[0]
    print(parse_size(rece_bytes))
    print(parse_size(sent_bytes))
    print("Uptime", re.findall(r'(?<=Uptime:).*', status_output)[0].strip())

    print("Technology->", re.findall(r'(?<=Technology:).*',
          settings_output)[0].strip())
    print("Protocol->", re.findall(r'(?<=Protocol:).*',
          settings_output)[0].strip())
    print("Firewall->", re.findall(r'(?<=Firewall:).*',
          settings_output)[0].strip())
    print("Kill Switch->",
          re.findall(r'(?<=Kill Switch:).*', settings_output)[0].strip())
    print("CyberSec->", re.findall(r'(?<=CyberSec:).*',
          settings_output)[0].strip())
    print("Obfuscate->", re.findall(r'(?<=Obfuscate:).*',
          settings_output)[0].strip())
    print("Auto-connect->",
          re.findall(r'(?<=Auto-connect:).*', settings_output)[0].strip())
    print("IPv6->", re.findall(r'(?<=IPv6:).*', settings_output)[0].strip())
    print("DNS->", re.findall(r'(?<=DNS:).*', settings_output)[0].strip())

    print("Version", version_output.split()[2].strip())

    print("Expire", account_output.split('(')[0].strip())


parse_nordvpn_cli()
