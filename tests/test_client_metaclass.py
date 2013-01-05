import unittest
from kazoo.client import RestClientMetaClass
from kazoo.rest_resources import RestResource
import inspect


class TestClass(object):
    __metaclass__ = RestClientMetaClass
    some_resource = RestResource(
        "some_resource",
        "/{resource_one_id}/subresources/{resource_two_id}")
    extra_views_resource = RestResource(
        "books",
        "/{resource_one_id}/books/{bookid}",
        extra_views=["unavailable",
                     {"name": "get_all_books_status", "path": "status"}])
    detail_only_resource = RestResource(
        "auction",
        "/users/{user_id}/auctions/{auction_id}",
        methods=["detail"])
    extra_object_view_resource = RestResource(
        "tools",
        "/sheds/{shed_id}/tools/{tool_id}",
        extra_views=[
            {"name": "get_tool_users", "path": "users", "scope": "object"}]
    )
    custom_names_resource = RestResource(
        "stupidname",
        "/place/{objid}",
        method_names={
            "list": "get_birds",
            "object": "get_bird",
            "create": "create_bird",
            "update": "update_bird",
            "delete": "delete_bird"
        })


class MetaclassMethodCreationTestCase(unittest.TestCase):

    def setUp(self):
        self.test_resource = TestClass()

    def test_get_list_resource_has_no_args(self):
        args, _, _, _ = inspect.getargspec(
            self.test_resource.get_some_resources)
        self.assertEqual(args, ["self", "resource_one_id"])

    def test_get_single_resource_has_object_id_as_argument(self):
        self._assert_resource_id_arguments("get_some_resource")

    def test_update_resource_has_object_id_arguments(self):
        self._assert_resource_id_arguments(
            "update_some_resource", includes_data=True)

    def test_delete_resource_has_object_id_arguments(self):
        self._assert_resource_id_arguments("delete_some_resource")

    def test_create_resource_has_no_object_id(self):
        args, _, varkw, _ = inspect.getargspec(
            self.test_resource.create_some_resource)
        self.assertEqual(args, ["self", "resource_one_id", "data"])

    def test_extra_views_created(self):
        self.assertTrue(hasattr(self.test_resource, "get_all_books_status"))
        self.assertTrue(hasattr(self.test_resource, "get_unavailable"))

    def test_extra_view_with_object_scope_has_extra_argument(self):
        args, _, _, _ = inspect.getargspec(self.test_resource.get_tool_users)
        self.assertEqual(args, ["self", "shed_id", "tool_id"])

    def test_only_specified_methods_created(self):
        self.assertTrue(hasattr(self.test_resource, "get_auction"))
        invalid_names = [
            "get_auctions",
            "create_auction",
            "update_auction",
            "delete_auction"
        ]
        for name in invalid_names:
            self.assertFalse(hasattr(self.test_resource, name))

    def _assert_resource_id_arguments(self, method_name, includes_data=False):
        func = getattr(self.test_resource, method_name)
        args, _, _, _ = inspect.getargspec(func)
        if includes_data:
            self.assertEqual(args,
                             ["self",
                              "resource_one_id", "resource_two_id", "data"])
        else:
            self.assertEqual(args,
                             ["self",
                              "resource_one_id", "resource_two_id"])


class GeneratedMethodNamesTestCase(unittest.TestCase):

    def setUp(self):
        self.test_resource = TestClass()

    def test_methods(self):
        method_names = ["get_bird", "get_birds", "create_bird",
                        "update_bird", "delete_bird"]
        for method_name in method_names:
            self.assertTrue(hasattr(self.test_resource, method_name))
