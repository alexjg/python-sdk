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

    def test_resource_with_no_required_args_correct(self):
        resource = RestResource("somename", "/sompath/{someobj_id}")
        self.assertEqual(resource.required_args, [])
        self.assertEqual(resource.object_arg, "someobj_id")

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

class ExtraViewsResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.resource = RestResource(
            "somresource",
            "/{id1}/somesubresource/{id2}",
            extra_views = [
                {"path":"status", "name": "all_devices_status"},
                "missing",
                {"path":"children", "name":"subresource_children", "scope":"object"}]
        )

    def test_extra_view_returns_correct_url(self):
        request = self.resource.get_extra_view_request("status", id1=1)
        self.assertEqual(request.path, "/1/somesubresource/status")

    def test_extra_view_with_object_scope_returns_correct_url(self):
        request = self.resource.get_extra_view_request("children", id1=1, id2=2)
        self.assertEqual(request.path, "/1/somesubresource/2/children")

    def test_extra_views_described_by_dictionary(self):
        for view_desc in self.resource.extra_views:
            if view_desc["name"] == "all_devices_status":
                self.assertEqual(view_desc["path"], "status")

    def test_extra_views_described_by_string(self):
        for view_desc in self.resource.extra_views:
            if view_desc["name"] == "missing":
                self.assertEqual(view_desc["path"], "missing")
                self.assertEqual(view_desc["name"], "get_missing")

    def test_scope_added_if_not_specified(self):
        for view_desc in self.resource.extra_views:
            if view_desc["path"] != "children":
                self.assertEqual(view_desc["scope"], "aggregate")

    def test_specified_scope_takes_precedence(self):
        for view_desc in self.resource.extra_views:
            if view_desc["path"] == "children":
                self.assertEqual(view_desc["scope"], "object")


class PluralNameResourceTestCase(unittest.TestCase):

    def test_resource_plural_name(self):
        resource = RestResource("subresource", "/{oneid}/someotherplace")
        self.assertEqual(resource.plural_name, "subresources")

    def test_if_plural_name_set_in_constructor_then_use_that(self):
        resource = RestResource("subresource", "/{oneid}/someotherplace",
                                plural_name="subresourcae")
        self.assertEqual(resource.plural_name, "subresourcae")


class AvailableMethodsResourceTestCase(unittest.TestCase):

    def test_excludes_resource(self):
        resource = RestResource("subresource", "/{oneid}/someplace", exclude_methods=["list", "detail"])
        self.assertEqual(resource.methods, ["create", "update", "delete"])




