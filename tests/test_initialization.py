import unittest
from kazoo import Client
from kazoo.request_objects import UsernamePasswordAuthRequest,\
        ApiKeyAuthRequest

class ConstructorRequiredArgumentsTestCase(unittest.TestCase):

    def assert_invalid_constructor_args(self, **kwargs):
        with self.assertRaises(RuntimeError):
            client = Client(**kwargs)

    def test_without_api_key_or_credentials_or_user_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client()

    def test_with_only_username_raises(self):
        self.assert_invalid_constructor_args(username="something")

    def test_with_only_password_raises(self):
        self.assert_invalid_constructor_args(password="pass")

    def test_with_only_account_name_raises(self):
        self.assert_invalid_constructor_args(account_name="sdfasd")

    def test_without_password_raises(self):
        self.assert_invalid_constructor_args(username="su", account_name="Dfasdf")

    def test_without_account_name_raises(self):
        self.assert_invalid_constructor_args(username="asdfas", password="sdfasd")

    def test_without_username_raises(self):
        self.assert_invalid_constructor_args(account_name="dafas", password="|asdfa")

    def test_with_api_key_does_not_raise(self):
        client = Client(api_key="sometoken")

    def test_with_valid_username_creds_does_not_raise(self):
        client = Client(account_name="user", password="pass", username="username")

    def test_with_username_and_password_creates_user_auth_request(self):
        client = Client(account_name="user", password="pass", username="someusername")
        self.assertEqual(type(client.auth_request), UsernamePasswordAuthRequest)

    def test_with_token_creates_api_key_auth_request(self):
        client = Client(api_key="fhasdlkjfblkasd")
        self.assertEqual(type(client.auth_request), ApiKeyAuthRequest)

