#!/usr/bin/python3
"""
NordVPN Prometheus Exporter
"""
import subprocess
import re


def execute(option):
    return subprocess.check_output("nordvpn {}".format(option), shell=True).decode("utf-8")


def parse_status():
    output = execute("status")
    print("Connection->", re.findall(r'(?<=Status:).*', output))


def parse_settings():
    pass


def parse_version():
    pass


def parse_account():
    pass


parse_status()
