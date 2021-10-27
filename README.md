![GitHub](https://img.shields.io/github/license/veerendra2/nordvpn-exporter)
![GitHub Repo stars](https://img.shields.io/github/stars/veerendra2/nordvpn-exporter)
![GitHub issues](https://img.shields.io/github/issues/veerendra2/nordvpn-exporter)

# `nordvpn` Prometheus Exporter
> This is not official NordVPN exporter. 

[<img src="https://user-images.githubusercontent.com/8393701/138961711-e56542f4-0ac0-4113-bbec-6172e4ce066e.png">](https://user-images.githubusercontent.com/8393701/138961711-e56542f4-0ac0-4113-bbec-6172e4ce066e.png)


A simple exporter fetch info from `nordvpn` cli. 

## Why?
To monitor remote devices VPN connection. In my case, I use RaspberryPi4 and run `nordvpn` in [docker](https://github.com/bubuntux/nordvpn)

## Dependency
* `nordvpn` cli.
   * Installation guide [here](https://support.nordvpn.com/FAQ/Setup-tutorials/1182453582/Installing-and-using-NordVPN-on-Linux.htm)

## Install
```
$ pip3 install nordvpn_exporter
```
## Usage
```
$ nordvpn_exporter --help
usage: nordvpn_exporter [-h] [-d] [-p PORT] [-v]

Simple NordVPN exporter

optional arguments:
  -h, --help  show this help message and exit
  -d          Run as daemon
  -p PORT     Port
  -v          show program's version number and exit
```
* Run exporter directly and `curl http://localhost:8082/metrics` in another terminal
```
$ nordvpn_exporter 
Starting NordVPN Exporter on http://localhost:8082
```
* I created a simple "daemonize" option to run exporter background 
```
$ nordvpn_exporter -d
Starting NordVPN Exporter on http://localhost:8082
[*] Running in background

$ curl http://localhost:8082/metrics | head
#=#=-#     #                                                                                                                                     
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 264.0
python_gc_objects_collected_total{generation="1"} 33.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
```
