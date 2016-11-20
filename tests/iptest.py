import unittest

from requests_mock import Mocker

from src.ip import IP, IPv4Getter, IPv6Getter

SOAP = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<u:GetExternalIPAddressResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
<NewExternalIPAddress>8.8.8.8</NewExternalIPAddress>
</u:GetExternalIPAddressResponse>
</s:Body>
</s:Envelope>"""

class IPTestCase(unittest.TestCase):
    def test_is_public(self):
        self.assertFalse(IP('192.168.0.1').is_public())
        self.assertTrue(IP('8.8.8.8').is_public())

        self.assertFalse(IP('::1').is_public())

    def test_family(self):
        self.assertEqual('A', IP('192.168.0.1').family())
        self.assertEqual('AAAA', IP('::1').family())

    def test_ipv4_getter(self):
        with Mocker() as mock:
            mock.post('http://fritz.box:49000/igdupnp/control/WANIPConn1', text=SOAP)
            getter = IPv4Getter()
            self.assertEqual(getter.get(), IP('8.8.8.8'))

    def test_ipv6_getter(self):
        getter = IPv6Getter()
        self.assertTrue(getter.get().is_public())

if __name__ == '__main__':
    unittest.main()
