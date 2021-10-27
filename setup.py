#!/usr/bin/python3
import sys
import setuptools
from setuptools.command.install import install

version = sys.version_info[:2]
if (3, 0) < version < (3, 4):
    print('nordvpn_exporter requires Python version 3.4 or later ({}.{} detected).'.format(*version))
    sys.exit(1)

setuptools.setup(
    name='nordvpn_exporter',
    version='1.0',
    description='A simple NordVPN Exporter',
    url='https://github.com/veerendra2/nordvpn-exporter',
    author='Veerendra K',
    license='Apache 2.0',
    project_urls={
        "Bug Tracker": "https://github.com/veerendra2/nordvpn-exporter/issues",
    },
    packages=setuptools.find_packages(where="src"),
    install_requires=["prometheus_client", "waitress", "Flask"],
    entry_points={'console_scripts': [
        'nordvpn_exporter = nordvpn_exporter:main']},
    package_dir={'': 'src'},
    python_requires=">=3.4",
    classifiers=[
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta"
    ],
    zip_safe=False)
