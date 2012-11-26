import requests
import kazoo.exceptions as exceptions

class Client(object):
    BASE_URL = "http://api.2600hz.com:8000/v1"

    def __init__(self, api_key):
        self.api_key = api_key
        self._authenticated = False

    def _request(self, path, method, params=None):
        if not self._authenticated:
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
        req = requests.Request(url, method=method, data=data, headers=headers)
        req.send()

    def get_account(self, account_id):
        self._request("/accounts/{0}".format(account_id), "GET")
