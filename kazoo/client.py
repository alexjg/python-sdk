import json
import requests
import kazoo.exceptions as exceptions
from kazoo.request_objects import KazooRequest, UsernamePasswordAuthRequest, \
        ApiKeyAuthRequest

class RestClientMetaClass(type):

    def __init__(cls, name, bases, dct):
        super(RestClientMetaclass, cls).__init__(name, bases, dct)
        for key, value in dct.items():
            if hasattr(value, "verbose_name"):
                cls._add_resource_methods(value, dct)


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

    def get_callflows(self, account_id):
        get_callflows_request = KazooRequest("/accounts/{account_id}/callflows")
        return self._execute_request(get_callflows_request,
                                     account_id=account_id)

    def add_callflow(self, account_id, **kwargs):
        add_callflow_req = KazooRequest("/accounts/{account_id}/callflows")
        return self._execute_request(add_callflow_req,
                                     account_id=account_id,
                                     method="put",
                                     data=kwargs)

    def update_callflow(self, account_id, callflow_id, **kwargs):
        update_callflow_req = KazooRequest("/accounts/{account_id}/callflows/{callflow_id}")
        return self._execute_request(update_callflow_req,
                                     account_id=account_id,
                                     callflow_id=callflow_id,
                                     data=kwargs,
                                     method="post")

    def delete_callflow(self, account_id, callflow_id):
        delete_callflow_req = KazooRequest("/accounts/{account_id}/callflows/{callflow_id}")
        return self._execute_request(delete_callflow_req,
                                     account_id=account_id,
                                     callflow_id=callflow_id,
                                     method="delete")


