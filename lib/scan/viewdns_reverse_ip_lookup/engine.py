#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
import socks
import socket
import json
from core._time import now
from xml.etree import ElementTree as ET
from core.alert import *
from core.targets import target_type
from core.targets import target_to_host
from core.log import __log_into_file
from lib.icmp.engine import do_one as do_one_ping
from lib.socks_resolver.engine import getaddrinfo


def extra_requirements_dict():
    return {}


def start(target, users, passwds, ports, timeout_sec, thread_number, num, total, log_in_file, time_sleep, language,
          verbose_level, socks_proxy, retries, ping_flag, methods_args, scan_id,
          scan_cmd):  # Main function
    if target_type(target) != 'SINGLE_IPv4' or target_type(target) != 'DOMAIN' or target_type(target) != 'HTTP' or target_type !='SINGLE_IPv6':
        # output format
        time.sleep(time_sleep)
        if socks_proxy is not None:
            socks_version = socks.SOCKS5 if socks_proxy.startswith('socks5://') else socks.SOCKS4
            socks_proxy = socks_proxy.rsplit('://')[1]
            if '@' in socks_proxy:
                socks_username = socks_proxy.rsplit(':')[0]
                socks_password = socks_proxy.rsplit(':')[1].rsplit('@')[0]
                socks.set_default_proxy(socks_version, str(socks_proxy.rsplit('@')[1].rsplit(':')[0]),
                                        int(socks_proxy.rsplit(':')[-1]), username=socks_username,
                                        password=socks_password)
                socket.socket = socks.socksocket
                socket.getaddrinfo = getaddrinfo
            else:
                socks.set_default_proxy(socks_version, str(socks_proxy.rsplit(':')[0]), int(socks_proxy.rsplit(':')[1]))
                socket.socket = socks.socksocket
                socket.getaddrinfo = getaddrinfo
        # set user agent
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
                   "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
                   "Accept-Language": "en-US,en;q=0.5"
                   }
        # timeout check
        if ping_flag:
            if socks_proxy is not None:
                socks_version = socks.SOCKS5 if socks_proxy.startswith('socks5://') else socks.SOCKS4
                socks_proxy = socks_proxy.rsplit('://')[1]
                if '@' in socks_proxy:
                    socks_username = socks_proxy.rsplit(':')[0]
                    socks_password = socks_proxy.rsplit(':')[1].rsplit('@')[0]
                    socks.set_default_proxy(socks_version, str(socks_proxy.rsplit('@')[1].rsplit(':')[0]),
                                            int(socks_proxy.rsplit(':')[-1]), username=socks_username,
                                            password=socks_password)
                    socket.socket = socks.socksocket
                    socket.getaddrinfo = getaddrinfo
                else:
                    socks.set_default_proxy(socks_version, str(socks_proxy.rsplit(':')[0]),
                                            int(socks_proxy.rsplit(':')[1]))
                    socket.socket = socks.socksocket
                    socket.getaddrinfo = getaddrinfo
            warn(messages(language, 100).format(target, 'heartbleed_vuln'))
            if do_one_ping(target, timeout_sec, 8) is None:
                return None
        total_req = 1
        trying = 1
        info(messages(language, 113).format(trying, total_req, num, total, target, 'viewdns ip lookup'))
        n = 0
        while 1:
            try:
                res = requests.get('http://viewdns.info/reverseip/?host={0}&t=1'.format(target), timeout=timeout_sec,
                                   headers=headers, verify=True).text
                break
            except:
                n += 1
                if n is retries:
                    warn(messages(language, 106).format("viewdns.info"))
                    return 1
        _values = []
        try:
            s = '<table>' + res.rsplit('''<table border="1">''')[1].rsplit("<br></td></tr><tr></tr>")[0]
            table = ET.XML(s)
            rows = iter(table)
            headers = [col.text for col in next(rows)]
            for row in rows:
                values = [col.text for col in row]
                _values.append(dict(zip(headers, values))["Domain"])
        except:
            pass
        if len(_values) is 0:
            info(messages(language, 164))
        if len(_values) > 0:
            for domain in _values:
                info(messages(language, 114).format(domain))
                data = json.dumps({'HOST': target, 'USERNAME': '', 'PASSWORD': '', 'PORT': '', 
                    'TYPE': 'viewdns_reverse_ip_lookup_scan', 'DESCRIPTION': domain, 
                    'TIME': now(), 'CATEGORY': "scan", 'SCAN_ID': scan_id, 'SCAN_CMD': scan_cmd}) + "\n"
                __log_into_file(log_in_file, 'a', data)
        if verbose_level is not 0:
            data = json.dumps({'HOST': target, 'USERNAME': '', 'PASSWORD': '', 'PORT': '', 'TYPE': 'viewdns_reverse_ip_lookup_scan', 
                'DESCRIPTION': messages(language, 114).format(len(_values), ", ".join(_values) if len(
                    _values) > 0 else "None"), 'TIME': now(), 'CATEGORY': "scan", 'SCAN_ID': scan_id, 
                'SCAN_CMD': scan_cmd}) + "\n"
            __log_into_file(log_in_file, 'a', data)
    else:
        warn(messages(language, 69).format('viewdns_reverse_ip_lookup_scan', target))
