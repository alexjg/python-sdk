import unittest
from kazoo import Client
from kazoo.request_objects import UsernamePasswordAuthRequest,\
        ApiKeyAuthRequest

class ConstructorRequiredArgumentsTestCase(unittest.TestCase):

    def test_without_api_key_or_credentials_or_user_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client()

    def test_with_username_but_not_password_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client(account_name="somename")

    def test_with_password_but_no_username_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client(password="somepassword")

    def test_with_api_key_does_not_raise(self):
        client = Client(api_key="sometoken")

    def test_with_username_and_password_does_not_raise(self):
        client = Client(account_name="user", password="pass")

    def test_with_username_and_password_creates_user_auth_request(self):
        client = Client(account_name="user", password="pass")
        self.assertEqual(type(client.auth_request), UsernamePasswordAuthRequest)

    def test_with_token_creates_api_key_auth_request(self):
        client = Client(api_key="fhasdlkjfblkasd")
        self.assertEqual(type(client.auth_request), ApiKeyAuthRequest)

