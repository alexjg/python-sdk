import json
import requests
import kazoo.exceptions as exceptions

class Client(object):
    BASE_URL = "http://api.2600hz.com:8000/v1"

    def __init__(self, api_token):
        self.api_token = api_token
        self._authenticated = False
        self.auth_token = None

    def _request(self, path, method, params=None,
                 require_auth=True):
        if require_auth and not self._authenticated:
            raise exceptions.InvalidConfigurationError("The client is not "
                                                       "authenticated, please "
                                                       "call client.authenticate")
        url = self.BASE_URL + path
        if params:
            data = json.dumps({"data": params})
        else:
            data = None
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kazoo python SDK",
        }
        req_func = getattr(requests, method)
        response = req_func(url, data=data, headers=headers)
        return response

    def authenticate(self):
        if not self._authenticated:
            resp = self.auth_token = self._request("/api_auth", "put",
                                            params={"api_token": self.api_token},
                                            require_auth=False)
            self.auth_token = resp.json["auth_token"]
            self._authenticated = True

    def get_account(self, account_id):
        return self._request("/accounts/{0}".format(account_id), "GET")
