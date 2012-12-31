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

    def _execute_request(self, request, **kwargs):
        if request.auth_required:
            kwargs["token"] = self.auth_token
        return request.execute(self.BASE_URL, **kwargs)

    def get_account(self, account_id):
        get_account_request = KazooRequest("/accounts/{account_id}")
        return self._execute_request(get_account_request,
                                     account_id=account_id)

    def update_account(self, account_id, **kwargs):
        """Update the account"""
        update_account_request = KazooRequest("/accounts/{account_id}")
        return self._execute_request(update_account_request,
                                     account_id=account_id,
                                     method='post',
                                     data=kwargs)

    def delete_account(self, account_id):
        delete_account_request = KazooRequest("/accounts/{account_id}")
        return self._execute_request(delete_account_request,
                                     account_id=account_id,
                                     method='delete')

