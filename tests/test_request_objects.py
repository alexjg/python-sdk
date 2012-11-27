import json
from kazoo import exceptions
from kazoo.request_objects import KazooRequest, UsernamePasswordAuthRequest, \
        ApiKeyAuthRequest
import mock
import unittest
from tests import utils

class RequestTestCase(unittest.TestCase):

    def assert_data(self, mock_request, expected_data):
        expected_wrapper = {"data": expected_data}
        mock_request.assert_called_with(mock.ANY, headers=mock.ANY,
                                        data=json.dumps(expected_wrapper))



class RequestObjectParameterTestCase(RequestTestCase):

    def setUp(self):
        self.param_name = "param1"
        self.url = "/testpath/{{{0}}}".format(self.param_name)

    def create_req_obj(self, url, auth_required=False):
        return KazooRequest(url, auth_required=auth_required)

    def test_execute_requires_param(self):
        req_obj = self.create_req_obj(self.url)
        with self.assertRaises(ValueError):
            req_obj.execute("http://testserver")

    def test_url_contains_param(self):
        req_obj = self.create_req_obj(self.url)
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.json = {"some_key": "some_val", "status": "success"}
            req_obj.execute("http://testserver", param1="somevalue")
            mock_get.assert_called_with("http://testserver/testpath/somevalue",
                                        headers=mock.ANY)

    def test_request_method_used(self):
        req_obj = self.create_req_obj(self.url)
        with mock.patch('requests.get') as mock_get, mock.patch('requests.post') as mock_post:
            req_obj.execute("http://testserver", param1="value", method="post")
            mock_post.assert_called_with("http://testserver/testpath/value",
                                         headers=mock.ANY)

    def test_request_method_checks_allowed(self):
        req_obj = self.create_req_obj(self.url)
        with self.assertRaises(exceptions.InvalidHttpMethodError):
            req_obj.execute("https://testserver", param1="value", method="baha")

    def test_auth_required_throws_if_no_token_passed(self):
        req_obj = self.create_req_obj(self.url, auth_required=True)
        with self.assertRaises(exceptions.AuthenticationRequiredError):
            with mock.patch('requests.get') as mock_get:
                req_obj.execute("https://testserver", param1="value")

    def test_auth_required_does_not_throw_if_token_present(self):
        req_obj = self.create_req_obj(self.url, auth_required=True)
        with mock.patch('requests.get') as mock_get:
            req_obj.execute("https://testserver", token="jfhasdfasd", param1="value3")


class RequestObjectDataParamsTestCase(RequestTestCase):

    def setUp(self):
        self.path = "/testpath/{param3}"

    def test_data_sent_to_server(self):
        req_obj = KazooRequest(self.path, auth_required=False)
        with mock.patch('requests.get') as mock_get:
            data_dict = {
                "data1":"dataval1"
            }
            req_obj.execute("http://testserver", param3="someval", data=data_dict)
            self.assert_data(mock_get, data_dict)

    def test_data_sent_to_server_with_auth_if_required(self):
        req_obj = KazooRequest(self.path, auth_required=True)
        with mock.patch('requests.post') as mock_post:
            data_dict = {
                "data1":"dataval1"
            }
            token = "sdkjfhasdfa"
            expected_headers = {
                "Content-Type":"application/json",
                "X-Auth-Token":token,
            }
            req_obj.execute("http://testserver", param3="someval",
                            token=token, method="post")
            mock_post.assert_called_with(mock.ANY, headers=expected_headers)


class RequestObjectErrorHandling(RequestTestCase):

    def setUp(self):
        self.error_response = json.loads(utils.load_fixture("bad_auth_response.json"))

    def test_kazoo_api_error_raised_on_error_response(self):
        req_obj = KazooRequest("/somepath", auth_required=False)
        with mock.patch('requests.get') as mock_get:
            mock_response = mock.Mock()
            mock_response.json = self.error_response
            mock_get.return_value = mock_response
            with self.assertRaises(exceptions.KazooApiError) as cm:
                req_obj.execute("http://testserver")
            self.assertEqual(cm.exception.message,
                             self.error_response["message"])



class UsernamePasswordAuthRequestTestCase(RequestTestCase):

    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.b64_password = "cGFzc3dvcmQ="
        self.req_obj = UsernamePasswordAuthRequest(self.username, self.password)

    def test_request_hits_correct_url(self):
        with mock.patch("requests.put") as mock_put:
            self.req_obj.execute("http://testserver")
            mock_put.assert_called_with("http://testserver/user_auth",
                                        headers=mock.ANY,
                                        data=mock.ANY)

    def test_request_sends_correct_data(self):
        with mock.patch('requests.put') as mock_put:
            expected_data = {
                "credentials": self.b64_password,
                "account_name": self.username,
            }
            self.req_obj.execute("http://testserver")
            self.assert_data(mock_put, expected_data)


class ApiKeyAuthRequestTestCase(RequestTestCase):

    def setUp(self):
        self.api_key = "dsfjhasdfknasdfhas"
        self.req_obj = ApiKeyAuthRequest(self.api_key)

    def test_correct_url_hit(self):
        with mock.patch('requests.put') as mock_put:
            self.req_obj.execute("http://testserver")
            mock_put.assert_called_with("http://testserver/api_auth",
                                        headers=mock.ANY,
                                        data=mock.ANY)

    def test_correct_data_sent(self):
        with mock.patch('requests.put') as mock_put:
            self.req_obj.execute("http://testserver")
            expected_data = {
                "api_key": self.api_key
            }
            self.assert_data(mock_put, expected_data)


