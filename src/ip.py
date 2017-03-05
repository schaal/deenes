from xml.etree import ElementTree
import socket
import requests

import IPy

from systemd import journal
from tenacity import retry, wait_exponential, stop_after_attempt

class IP(IPy.IP):
    def __init__(self, ip: str):
        IPy.IP.__init__(self, ip)

    def is_public(self):
        """Return True if this IP is publicly allocated"""
        return self.iptype().startswith(('ALLOCATED', 'PUBLIC'))

    def family(self):
        """Return A for IPv4 and AAAA for IPv6"""
        return 'A' if self.version() == 4 else 'AAAA'

    @retry(wait=wait_exponential(multiplier=1, max=10),
           stop=stop_after_attempt(3))
    def update(self, apikey: str, name: str):
        """Try to update the DNS record with this IP"""
        if not self.is_public():
            return True

        request = requests.get('https://api.tokendns.co/v1/update', params={
            'apikey': apikey,
            'name': name,
            'domain': 'blabladns.xyz',
            'content': self.strNormal(),
            'type': self.family()
        })

        if request.status_code != 200:
            journal.send('Setting IP to {} failed for {} record with {}'.format(
                self, self.family(), request.status_code), priority=journal.LOG_WARNING)
            return False

        journal.send('DNS successfully updated to {}'.format(self))
        return True

class IPGetter:
    def get(self):
        try:
            return IP(self._get())
        except ValueError:
            return None

    def _get(self):
        raise NotImplementedError

class IPv4Getter(IPGetter):
    @retry(wait=wait_exponential(multiplier=1, max=10),
           stop=stop_after_attempt(3))
    def _get(self):
        request = requests.post(url='http://fritz.box:49000/igdupnp/control/WANIPConn1', headers={
            'Content-Type': 'text/xml; charset="utf-8"',
            'SoapAction': 'urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress'
        }, data="<?xml version='1.0' encoding='utf-8'?> <s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'><s:Body><u:GetExternalIPAddress xmlns:u='urn:schemas-upnp-org:service:WANIPConnection:1' /></s:Body></s:Envelope>")
        return ElementTree.fromstring(request.content).find('.//NewExternalIPAddress').text

class IPv6Getter(IPGetter):
    @retry(wait=wait_exponential(multiplier=1, max=10),
           stop=stop_after_attempt(3))
    def _get(self):
        ips = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6)
        return [ip[4][0] for ip in ips if ip[1] == socket.SOCK_STREAM][0]
