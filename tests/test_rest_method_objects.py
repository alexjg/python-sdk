import unittest
from kazoo.rest_resources import RestResource

class RestResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.resource = RestResource("/{argument1}/subresource/{argument2}")

    def test_resource_generates_required_args_for_all_but_last(self):
        self.assertEqual(self.resource.required_args, ["argument1"])

    def test_resource_generates_correct_object_arg(self):
        self.assertEqual(self.resource.object_arg, 'argument2')

    def test_resource_with_no_args_generates_error(self):
        with self.assertRaises(ValueError):
            resource = RestResource("/blahblah/blah")

