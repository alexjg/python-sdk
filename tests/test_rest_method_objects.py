from kazoo.rest_resources import RestResource
from kazoo import rest_resources
import mock
import unittest

class RestResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.path = "/{argument1}/subresource/{argument2}"
        self.resource = RestResource("subresource", "/{argument1}/subresource/{argument2}")

    def test_resource_generates_required_args_for_all_but_last(self):
        self.assertEqual(self.resource.required_args, ["argument1"])

    def test_resource_generates_correct_object_arg(self):
        self.assertEqual(self.resource.object_arg, 'argument2')

    def test_resource_with_no_args_generates_error(self):
        with self.assertRaises(ValueError):
            resource = RestResource("somename", "/blahblah/blah")

    def test_resource_plural_name(self):
        self.assertEqual(self.resource.plural_name, "subresources")

    def test_resource_path_correctly_calculated(self):
        self.assertEqual(self.resource.path, "/{argument1}/subresource")

    def test_resource_list_method_hits_correct_url(self):
        request = self.resource.get_list_request(argument1=1)
        self.assertEqual(request.path, "/1/subresource")

    def test_resource_individual_method_hits_correct_url(self):
        request = self.resource.get_object_request(argument1=1, argument2=2)
        self.assertEqual(request.path, "/1/subresource/2")

    def test_update_resource_correct_url_and_method(self):
        request = self.resource.get_update_object_request(argument1=1, argument2=2)
        self.assertEqual(request.path, "/1/subresource/2")
        self.assertEqual(request.method, 'post')

    def test_delete_resource_correct_url_and_method(self):
        request = self.resource.get_delete_object_request(argument1=1, argument2=2)
        self.assertEqual(request.path, "/1/subresource/2")
        self.assertEqual(request.method, 'delete')

    def test_create_resource_correct_url_and_method(self):
        request = self.resource.get_create_object_request(argument1=1)
        self.assertEqual(request.path, "/1/subresource")
        self.assertEqual(request.method, 'put')

