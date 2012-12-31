import json
import requests
import kazoo.exceptions as exceptions
from kazoo.request_objects import KazooRequest, UsernamePasswordAuthRequest, \
        ApiKeyAuthRequest

class Client(object):
    BASE_URL = "http://api.2600hz.com:8000/v1"


    def __init__(self, api_key=None, password=None, account_name=None,
                 username=None):
        if not api_key and not password:
            raise RuntimeError("You must pass either an api_key or an "
                               "account name/password pair")

        if password or account_name or username:
            if not (password and account_name and username):
                raise RuntimeError("If using account name/password "
                                   "authentication then you must specify "
                                   "password, userame and account_name "
                                   "arguments")
            self.auth_request = UsernamePasswordAuthRequest(username,
                                                            password,
                                                            account_name)
        else:
            self.auth_request = ApiKeyAuthRequest(api_key)

        self.api_key = api_key
        self._authenticated = False
        self.auth_token = None

    def authenticate(self):
        if not self._authenticated:
            self.auth_token = self.auth_request.execute(
                self.BASE_URL)["auth_token"]
            self._authenticated = True
        return self.auth_token

    def get_account(self, account_id):
        get_account_request = KazooRequest("/accounts/{account_id}")
        return get_account_request.execute(self.BASE_URL,
                                           account_id=account_id,
                                           token=self.auth_token)

    def update_account(self, account_id, **kwargs):
        """Update the account"""
        update_account_request = KazooRequest("/accounts/{account_id}")
        return update_account_request.execute(self.BASE_URL,
                                              account_id=account_id,
                                              token=self.auth_token,
                                              data=kwargs)
