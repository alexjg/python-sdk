import unittest
from kazoo import Client

class ConstructorRequiredArgumentsTestCase(unittest.TestCase):

    def test_without_token_or_credentials_or_user_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client()

    def test_with_username_but_not_password_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client(account_name="somename")

    def test_with_password_but_no_username_raises(self):
        with self.assertRaises(RuntimeError):
            client = Client(password="somepassword")

    def test_with_token_does_not_raise(self):
        client = Client(api_token="soemtoken")

    def test_with_username_and_password_does_not_raise(self):
        client = Client(account_name="user", password="pass")

