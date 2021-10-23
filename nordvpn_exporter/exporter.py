#!/usr/bin/python3
"""
Simple NordVPN Prometheus Exporter
"""
import re
import subprocess

from flask import Flask
from prometheus_client import make_wsgi_app, Gauge, Info, Counter
from waitress import serve

__author__ = "veerendra2"
__license__ = "Apache 2.0"
__version__ = "0.1"
__maintainer__ = "veerendra2"


app = Flask("NordVPN-Exporter")

# Define Metrics
status = Gauge('nordvpn_status', 'nordvpn status')
setting_firewall = Gauge('nordvpn_setting_firewall',
                         'nordvpn settings firewall enabled/disabled')
setting_kill_switch = Gauge('nordvpn_setting_kill_switch',
                            'nordvpn settings kill switch enabled/disabled')
setting_obfuscate = Gauge('nordvpn_setting_obfuscate',
                          'nordvpn settings obfuscate enabled/disabled')
setting_notify = Gauge('nordvpn_setting_notify',
                       'nordvpn settings notify enabled/disabled')
setting_auto_connect = Gauge('nordvpn_auto_connect',
                             'nordvpn settings auto connect enabled/disabled')
setting_ipv6 = Gauge('nordvpn_ipv6',
                     'nordvpn settings ipv6 enabled/disabled')
setting_dns = Gauge('nordvpn_dns',
                    'nordvpn settings dns enabled/disabled')
setting_cybersec = Gauge('nordvpn_setting_cybersec',
                         'nordvpn settings cybersec enabled/disabled')
bytes_received = Counter('nordvpn_bytes_received', 'Bytes received')
bytes_sent = Counter('nordvpn_bytes_sent', 'Bytes sent')
current_server = Info('nordvpn_current_server', 'Current connected host name')
connected_country = Info('nordvpn_connected_country',
                         'Current connected country')
connected_city = Info('nordvpn_connected_city', 'Current connected city')
uptime = Info('nordvpn_uptime', 'nordvpn uptime')
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
    return None


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
    if status is None:
        print("[.] nordvpn cli failed to run")
        exit(1)
    if not status:
        metrics_values = [status, "N/A", "N/A", "N/A",
                          "N/A", "N/A", "N/A", "0", "0", "N/A"]
    else:
        metrics_values.append(status)
        metrics_values.append(re.findall(r'(?<=Current server:).*',
                                         status_output)[0].strip())  # 1
        metrics_values.append(re.findall(r'(?<=Country:).*',
                                         status_output)[0].strip())  # 2
        metrics_values.append(re.findall(
            r'(?<=City:).*', status_output)[0].strip())  # 3
        metrics_values.append(re.findall(
            r'(?<=Server IP:).*', status_output)[0].strip())  # 4
        metrics_values.append(re.findall(r'(?<=Current technology:).*',
                                         status_output)[0].strip())  # 5
        metrics_values.append(re.findall(r'(?<=Current protocol:).*',
                                         status_output)[0].strip())  # 6
        rece_bytes = re.findall(
            r'(?<=Transfer: )(.+)received', status_output)[0]  # 7
        sent_bytes = re.findall(
            r'(?<=received,)(.+)sent', status_output)[0]  # 8
        metrics_values.append(parse_size(rece_bytes))
        metrics_values.append(parse_size(sent_bytes))
        metrics_values.append(re.findall(
            r'(?<=Uptime:).*', status_output)[0].strip())  # 9
    # These are alway available
    metrics_values.append(re.findall(
        r'(?<=Technology:).*', settings_output)[0].strip())  # 10
    try:
        metrics_values.append(re.findall(
            r'(?<=Protocol:).*', settings_output)[0].strip())  # 11
    except:
        pass
    metrics_values.append('N/A')
    metrics_values.append(re.findall(
        r'(?<=Firewall:).*', settings_output)[0].strip())   # 12
    metrics_values.append(re.findall(r'(?<=Kill Switch:).*',
                                     settings_output)[0].strip())  # 13
    metrics_values.append(re.findall(
        r'(?<=CyberSec:).*', settings_output)[0].strip())  # 14
    try:
        metrics_values.append(re.findall(
            r'(?<=Obfuscate:).*', settings_output)[0].strip())  # 15
    except:
        pass
    metrics_values.append('disabled')
    metrics_values.append(re.findall(
        r'(?<=Notify:).*', settings_output)[0].strip())  # 16
    metrics_values.append(re.findall(
        r'(?<=Auto-connect:).*', settings_output)[0].strip())  # 17
    metrics_values.append(re.findall(
        r'(?<=IPv6:).*', settings_output)[0].strip())  # 18
    metrics_values.append(re.findall(
        r'(?<=DNS:).*', settings_output)[0].strip())  # 19
    metrics_values.append(version_output.split()[2].strip())  # 20
    metrics_values.append(account_output.split('(')[1].strip())  # 21
    return metrics_values


@app.route("/metrics")
def expose_metrics():
    results = parse_nordvpn_cli()
    status.set(results[0])
    current_server.info({'server': results[1]})
    connected_country.info({'country': results[2]})
    connected_city.info({'city': results[3]})
    connected_ip.info({'ip': results[4]})
    current_tech.info({'tech': results[5]})
    current_protocol.info({'protocol': results[6]})
    bytes_received.inc(int(results[7]))
    bytes_sent.inc(int(results[8]))
    uptime.info({'uptime': results[9]})
    setting_tech.info({'tech': results[10]})
    setting_protocol.info({'protocol': results[11]})
    setting_firewall.set(toggle_values[results[12]])
    setting_kill_switch.set(toggle_values[results[13]])
    setting_cybersec.set(toggle_values[results[14]])
    setting_obfuscate.set(toggle_values[results[15]])
    setting_notify.set(toggle_values[results[16]])
    setting_auto_connect.set(toggle_values[results[17]])
    setting_ipv6.set(toggle_values[results[18]])
    setting_dns.set(toggle_values[results[19]])
    version.info({'version': results[20]})
    service_expiry.info({'expiry': results[21]})
    return make_wsgi_app()


@ app.route("/")
def mainPage():
    return ("<h1>NordVPN Exporter</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.")


if __name__ == '__main__':
    expose_metrics()
    print("Starting NordVPN Exporter on http://localhost:8080")
    serve(app, host='0.0.0.0', port=8080)
