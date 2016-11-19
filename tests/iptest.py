import unittest

from src.ip import IP, IPv4Getter, IPv6Getter

class IPTestCase(unittest.TestCase):
    def test_is_public(self):
        self.assertFalse(IP('192.168.0.1').is_public())
        self.assertTrue(IP('8.8.8.8').is_public())

        self.assertFalse(IP('::1').is_public())

    def test_family(self):
        self.assertEqual('A', IP('192.168.0.1').family())
        self.assertEqual('AAAA', IP('::1').family())

    def test_ipv4_getter(self):
        getter = IPv4Getter()
        self.assertTrue(getter.get().is_public())

    def test_ipv6_getter(self):
        getter = IPv6Getter()
        self.assertTrue(getter.get().is_public())

if __name__ == '__main__':
    unittest.main()
