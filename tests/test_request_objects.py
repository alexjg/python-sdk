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

    def test_execute_requires_param(self):
        req_obj = TestRequestObject(self.url)
        with self.assertRaises(ValueError):
            req_obj.execute("http://testserver")

    def test_url_contains_param(self):
        req_obj = TestRequestObject(self.url)
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.json = {"some_key": "some_val"}
            req_obj.execute("http://testserver", param1="somevalue")
            mock_get.assert_called_with("http://testserver/testpath/somevalue")

    def test_request_method_used(self):
        req_obj = TestRequestObject(self.url)
        with mock.patch('requests.get') as mock_get, mock.patch('requests.post') as mock_post:
            req_obj.execute("http://testserver", param1="value", method="post")
            mock_post.assert_called_with("http://testserver/testpath/value")

    def test_request_method_checks_allowed(self):
        req_obj = TestRequestObject(self.url)
        with self.assertRaises(exceptions.InvalidHttpMethodError):
            req_obj.execute("https://testserver", param1="value", method="baha")


