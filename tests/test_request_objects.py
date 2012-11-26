import json
from kazoo import exceptions
from kazoo.request_objects import BaseRequest
import mock
import unittest

class TestRequestObject(BaseRequest):
    pass


class RequestObjectParameterTestCase(unittest.TestCase):

    def setUp(self):
        self.param_name = "param1"
        self.url = "/testpath/{{{0}}}".format(self.param_name)

    def create_req_obj(self, url, auth_required=False):
        return TestRequestObject(url, auth_required=auth_required)

    def test_execute_requires_param(self):
        req_obj = self.create_req_obj(self.url)
        with self.assertRaises(ValueError):
            req_obj.execute("http://testserver")

    def test_url_contains_param(self):
        req_obj = self.create_req_obj(self.url)
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.json = {"some_key": "some_val"}
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


class RequestObjectDataParamsTestCase(unittest.TestCase):

    def setUp(self):
        self.path = "/testpath/{param3}"

    def test_data_sent_to_server(self):
        req_obj = TestRequestObject(self.path, auth_required=False)
        with mock.patch('requests.get') as mock_get:
            data_dict = {
                "data1":"dataval1"
            }
            req_obj.execute("http://testserver", param3="someval", data=data_dict)
            mock_get.assert_called_with(mock.ANY, data=json.dumps(data_dict),
                                        headers=mock.ANY)

    def test_data_sent_to_server_with_auth_if_required(self):
        req_obj = TestRequestObject(self.path, auth_required=True)
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




