import unittest
from kazoo.client import RestClientMetaClass
from kazoo.rest_resources import RestResource
import inspect


class TestClass(object):
    __metaclass__ = RestClientMetaClass
    some_resource = RestResource("some_resource",
        "/{resource_one_id}/subresources/{resource_two_id}")
    get_only_resource = RestResource("get_only",
        "/{resource_one_id}/getithere",
        methods="get",
        plural_name="getonly")

class MetaclassMethodCreationTestCase(unittest.TestCase):

    def setUp(self):
        self.test_resource = TestClass()

    def test_get_list_resource_has_no_args(self):
        args, _, _, _ = inspect.getargspec(self.test_resource.get_some_resources)
        self.assertEqual(args, ["self", "resource_one_id"])

    def test_get_single_resource_has_object_id_as_argument(self):
        self._assert_resource_id_arguments("get_some_resource")

    def test_update_resource_has_object_id_arguments(self):
        self._assert_resource_id_arguments("update_some_resource")

    def test_delete_resource_has_object_id_arguments(self):
        self._assert_resource_id_arguments("delete_some_resource")

    def test_create_resource_has_no_object_id(self):
        args, _, varkw, _ = inspect.getargspec(self.test_resource.create_some_resource)
        self.assertEqual(args, ["self", "resource_one_id"])

    def test_get_only_resource_only_creates_get_only(self):
        self.assertTrue(hasattr(self.test_resource), "get_getonly")
        wrong_names = ["create_get_only", "get_get_only", "delete_get_only", "update_get_only"]
        for name in wrong_names:
            self.assertTrue(not hasattr(self.test_resource), name)

    def _assert_resource_id_arguments(self, method_name):
        func = getattr(self.test_resource, method_name)
        args, _, _, _ = inspect.getargspec(func)
        self.assertEqual(args, ["self", "resource_one_id", "resource_two_id"])



