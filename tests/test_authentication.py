import mock
import unittest
from kazoo import Client


class AuthenticationTestCase(unittest.TestCase):

    def test_authentication_sets_auth_token(self):
        with mock.patch('kazoo.client.ApiKeyAuthRequest') as mock_req_class:
            mock_req = mock.Mock()
            mock_req.execute.return_value = {"auth_token": "authorizethis"}
            mock_req_class.return_value = mock_req
            client = Client(api_key="dsfjasbfkasdf")
            client.authenticate()
            mock_req.execute.assert_called_with(client.BASE_URL)
            self.assertEqual(client.auth_token, "authorizethis")
