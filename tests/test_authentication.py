import unittest
import mock
import requests
import kazoo
from kazoo import exceptions

class AuthenticationTestCase(unittest.TestCase):

    def setUp(self):
        self.api_key = "ifajskdfasdnmfkasbdfas"
        self.client = kazoo.Client(self.api_key)

    def test_calling_api_without_authenticating_raises(self):
        with self.assertRaises(exceptions.InvalidConfigurationError):
            self.client.get_account("ignoredId")
