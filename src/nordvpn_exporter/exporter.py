#!/usr/bin/python3
"""
Simple NordVPN Prometheus Exporter
"""
import re
import subprocess
import os
import argparse

from flask import Flask
from prometheus_client import make_wsgi_app, Gauge, Info, Counter
from waitress import serve

__author__ = "veerendra2"
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "veerendra2"


app = Flask("NordVPN-Exporter")

# Define Metrics
bytes_sent = Counter('nordvpn_bytes_sent', 'Bytes sent', ['hostname'])
bytes_received = Counter('nordvpn_bytes_received',
                         'Bytes received', ['hostname'])
settings = Info('nordvpn_settings', 'nordvn client settings')
connection = Info('nordvpn_connection', 'nordvn connection')
status = Gauge('nordvpn_status', 'nordvn status', ['hostname'])


def daemonize():
    if os.fork():
        os._exit(0)
    os.chdir("/")
    os.umask(22)
    os.setsid()
    os.umask(0)
    if os.fork():
        os._exit(0)
    stdin = open(os.devnull)
    stdout = open(os.devnull, 'w')
    os.dup2(stdin.fileno(), 0)
    os.dup2(stdout.fileno(), 1)
    os.dup2(stdout.fileno(), 2)
    stdin.close()
    stdout.close()
    os.umask(22)
    for fd in range(3, 1024):
        try:
            os.close(fd)
        except OSError:
            pass


def execute(option):
    output = subprocess.check_output("nordvpn {}".format(option), shell=True)
    return output.decode("utf-8")


def parse_size(size):
    units = {"B": 1, "KiB": 10**3, "MiB": 10**6, "GiB": 10**9, "TiB": 10**12}
    number, unit = [string.strip() for string in size.split()]
    return int(float(number)*units[unit])


def parse_nordvpn_cli():
    status_output = execute("status")
    settings_output = execute("settings")
    #account_output = execute("account")
    version_output = execute("--version")
    status_labels = dict()
    settings = dict()
    bytes_sent = 0
    bytes_received = 0
    con_status = 0
    for status_line in status_output.splitlines():
        fields = [x.strip() for x in status_line.split(':')]
        if len(fields) == 2:
            if fields[1].strip() == "Connected":
                con_status = 1

            elif fields[1].strip() == "Disconnected":
                con_status = 0
            else:
                if fields[0] == "Transfer":
                    bytes_received = parse_size(re.findall(
                        r'(.+)received', fields[1])[0].strip())
                    bytes_sent = parse_size(re.findall(
                        r'(?<=received,)(.+)sent', fields[1])[0].strip())
                else:
                    status_labels.setdefault(
                        fields[0].replace(" ", "_").replace("-", "_").lower(), fields[1])
    for settings_line in settings_output.splitlines():
        fields = [x.strip() for x in settings_line.split(':')]
        if len(fields) == 2:
            settings.setdefault(fields[0].replace(
                " ", "_").replace("-", "_").lower(), fields[1])
    settings.setdefault("version", version_output.split()[2])
    settings.setdefault("hostname", os.uname()[1])
    status_labels.setdefault("hostname", os.uname()[1])
    return (con_status, status_labels, settings, bytes_received, bytes_sent)


@app.route("/metrics")
def expose_metrics():
    status_info, status_labels, settings_info, bytes_received_info, bytes_sent_info = parse_nordvpn_cli()
    status.labels(os.uname()[1]).set(status_info)
    bytes_received.labels(os.uname()[1]).inc(bytes_received_info)
    bytes_sent.labels(os.uname()[1]).inc(bytes_sent_info)
    connection.info(status_labels)
    settings.info(settings_info)
    return make_wsgi_app()


@ app.route("/")
def mainPage():
    return ("<h1>NordVPN Exporter</h1>" + "Click <a href='/metrics'>here</a> to see metrics.")


def main():
    PORT = 8082
    parser = argparse.ArgumentParser(description='Simple NordVPN exporter')
    parser.add_argument('-d', action='store_true',
                        dest='daemon', default=False, help='Run as daemon')
    parser.add_argument('-p', action='store',
                        dest='port', help='Port')
    parser.add_argument('-v', action='version', version='%(prog)s 1.0')
    results = parser.parse_args()
    if results.port:
        PORT = results.port
    print("Starting NordVPN Exporter on http://localhost:{}".format(PORT))
    if results.daemon:
        print("[*] Running in background")
        daemonize()
    serve(app, host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    main()
