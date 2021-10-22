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


toggle_values = {"Connected": 1, "Disconnected": 0,
                 "enabled": 1, "disabled": 0}


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
    status = None
    metrics_values = []
    status = toggle_values[re.findall(
        r'(?<=Status:).*', status_output)[0].strip()]
    print(status)
    if not status:
        metrics_values = [status, "N/A", "N/A", "N/A",
                          "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    else:
        metrics_values = status
        metrics_values.append(re.findall(r'(?<=Current server:).*',
                                         status_output)[0].strip())  # 1
        metrics_values.append(re.findall(r'(?<=Country:).*',
                                         status_output)[0].strip())  # 2
        metrics_values.append(re.findall(
            r'(?<=City:).*', status_output)[0].strip())  # 3
        metrics_values.append(re.findall(r'(?<=Current technology:).*',
                                         status_output)[0].strip())  # 4
        rece_bytes = re.findall(
            r'(?<=Transfer: )(.+)received', status_output)[0]  # 5
        sent_bytes = re.findall(
            r'(?<=received,)(.+)sent', status_output)[0]  # 6
        metrics_values.append(parse_size(rece_bytes))  # 7
        metrics_values.append(parse_size(sent_bytes))  # 8
        metrics_values.append(re.findall(
            r'(?<=Uptime:).*', status_output)[0].strip())  # 9
    # These are alway available
    metrics_values.append(re.findall(
        r'(?<=Technology:).*', settings_output)[0].strip())  # 10
    metrics_values.append(re.findall(
        r'(?<=Protocol:).*', settings_output)[0].strip())  # 11
    metrics_values.append(re.findall(
        r'(?<=Firewall:).*', settings_output)[0].strip())   # 12
    metrics_values.append(re.findall(r'(?<=Kill Switch:).*',
                                     settings_output)[0].strip())  # 13
    metrics_values.append(re.findall(
        r'(?<=CyberSec:).*', settings_output)[0].strip())  # 14
    metrics_values.append(re.findall(
        r'(?<=Obfuscate:).*', settings_output)[0].strip())  # 15
    metrics_values.append(re.findall(
        r'(?<=Auto-connect:).*', settings_output)[0].strip())  # 16
    metrics_values.append(re.findall(
        r'(?<=IPv6:).*', settings_output)[0].strip())  # 17
    metrics_values.append(re.findall(
        r'(?<=DNS:).*', settings_output)[0].strip())  # 18
    metrics_values.append(version_output.split()[2].strip())  # 19
    metrics_values.append(account_output.split('(')[1].strip())  # 20
    return metrics_values

# @app.route("/metrics")


def expose_metrics():
    results = parse_nordvpn_cli()
    status.set(results[0])
    current_server.set(results[1])
    connected_country.set(results[2])
    connected_city.set(results[3])
    connected_ip.set(results[4])
    current_tech.set(results[5])
    current_protocol.set(results[6])
    setting_tech.set(results[7])
    setting_protocol.set(results[8])
    version.set(results[9])
    service_expiry.set(results[10])


if __name__ == '__main__':
    expose_metrics()
