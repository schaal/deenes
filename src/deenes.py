#!/usr/bin/python3

import asyncio
import time
import sys

from argparse import ArgumentParser

from threading import Lock
from configparser import NoOptionError

from pyroute2 import IPDB

from systemd.daemon import notify

from .ip import IPv4Getter, IPv6Getter
from .config import Config

class NoConfigError(Exception):
    """Raised when a config value is missing"""
    def __init__(self, message: str):
        Exception.__init__(self)
        self.message = message

class Deenes:
    def __init__(self, apikey: str, hostname: str, interface: str, simulate: bool):
        self.event_loop = asyncio.get_event_loop()
        self.ipdb = IPDB()
        self.lock = Lock()
        self.simulate = simulate

        self.last_ips = {'A': None, 'AAAA': None}
        self.getters = [IPv4Getter(), IPv6Getter()]
        self.cfg = {'apikey': apikey, 'hostname': hostname, 'interface': interface}

        for key in ('apikey', 'hostname', 'interface'):
            if self.cfg[key] is None:
                raise NoConfigError("Missing config value " + key)

    def _updatedomain(self):
        time.sleep(5)

        for getter in self.getters:
            ip = getter.get()
            if self.simulate:
                print(ip)
            if not self.simulate and ip is not None and ip != self.last_ips[ip.family()]:
                if ip.update(self.cfg['apikey'], self.cfg['hostname']):
                    self.last_ips[ip.family()] = ip

        self.lock.release()

    def _cb_ipdb(self, ipdb, msg, action):
        if action == 'RTM_NEWADDR' and msg['index'] == self.ipdb.interfaces[self.cfg['interface']]['index']:
            if self.lock.acquire(blocking=False):
                self.event_loop.call_soon_threadsafe(self._updatedomain)

    def start(self):
        """Start the event loop"""
        try:
            self.event_loop.call_soon(self._loop)
            self.event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            notify('STOPPING=1')
            self.ipdb.release()
            self.event_loop.stop()
            self.event_loop.close()

    def _loop(self):
        notify('READY=1\nSTATUS=Listening to ip address changes...')
        if self.lock.acquire(blocking=False):
            self.event_loop.call_soon_threadsafe(self._updatedomain)
        self.ipdb.register_callback(self._cb_ipdb)

def main():
    parser = ArgumentParser(description='TokenDNS updater')
    parser.add_argument('--simulate', action='store_true')
    args = parser.parse_args()

    try:
        if not args.simulate:
            cfg = Config()
            deenes = Deenes(cfg.apikey, cfg.hostname, cfg.interface, args.simulate)
        else:
            deenes = Deenes('simulate', 'simulate', 'simulate', args.simulate)
        deenes.start()
    except FileNotFoundError as ex:
        print("No configuration found at " + ex.filename)
        sys.exit(1)
    except (NoOptionError, NoConfigError) as ex:
        print(ex.message)
        sys.exit(1)
