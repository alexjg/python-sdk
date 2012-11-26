import json
import unittest
import mock
import requests
import kazoo
from kazoo import exceptions
from tests import utils

class AuthenticationTestCase(unittest.TestCase):

    def setUp(self):
        self.api_token = "ifajskdfasdnmfkasbdfas"
        self.client = kazoo.Client(self.api_token)

    def test_calling_api_without_authenticating_raises(self):
        with self.assertRaises(exceptions.InvalidConfigurationError):
            self.client.get_account("ignoredId")

    def test_authenticate_gets_auth_details(self):
        with mock.patch("requests.put") as mock_requests:
            mock_response = mock.Mock()
            mock_response.content = utils.load_fixture("good_auth_response.json")
            mock_response.json = json.loads(utils.load_fixture("good_auth_response.json"))
            mock_requests.return_value = mock_response
            self.client.authenticate()
            self.assertEqual(self.client.auth_token, "9f19181bf42bc66ab6d881ae4e1591d4")

