#!/usr/bin/python3
import sys
import os
import setuptools
from setuptools.command.install import install

version = sys.version_info[:2]
if (3, 0) < version < (3, 4):
    print('funmotd requires Python version 3.4 or later ({}.{} detected).'.format(*version))
    sys.exit(1)


class PostInstall(install):
    def run(self):
        install.run(self)
        mode = 0o666
        bashrc_file = os.path.join(os.path.expanduser('~'), ".bashrc")
        for filepath in self.get_outputs():
            if os.path.split(filepath)[1] == "config.json":
                os.chmod(filepath, mode)
        try:
            with open(bashrc_file) as f:
                bashrc_content = f.read()
            if bashrc_content.find("funmotd") != -1:
                print("[*] .bashrc file has already 'funmotd'. Nothing to do")
            else:
                with open(bashrc_file, 'a') as f:
                    f.write("\nfunmotd")
                print("[*] Updated .bashrc file.")
        except Exception:
            print("[-] Caught Exception while updating .bashrc file. Please update it manually: 'echo funmotd >> ~/.bashrc'")


setuptools.setup(
    name='nordvpn_exporter',
    version='0.1',
    description='NordVPN Exporter',
    url='https://github.com/veerendra2/nordvpn-exporter',
    author='Veerendra K',
    license='Apache 2.0',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': [
        'nordvpn_exporter = nordvpn_exporter:main']},
    package_dir={'nordvpn_exporter': 'nordvpn_exporter/'},
    include_package_data=True,
    python_requires=">=3.4",
    cmdclass={'install': PostInstall, },
    classifiers=[
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta"
    ],
    zip_safe=False)
