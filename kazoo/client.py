import json
import requests
import kazoo.exceptions as exceptions
from kazoo.request_objects import KazooRequest, UsernamePasswordAuthRequest, \
        ApiKeyAuthRequest
from kazoo.rest_resources import RestResource

class RestClientMetaClass(type):

    def __init__(cls, name, bases, dct):
        super(RestClientMetaClass, cls).__init__(name, bases, dct)
        for key, value in dct.items():
            if hasattr(value, "plural_name"):
                cls._add_resource_methods(key, value, dct)

    def _add_resource_methods(cls, resource_field_name, rest_resource, dct):
        cls._generate_list_func(resource_field_name, rest_resource)
        cls._generate_get_object_func(resource_field_name, rest_resource)
        cls._generate_delete_object_func(resource_field_name, rest_resource)
        cls._generate_update_object_func(resource_field_name, rest_resource)
        cls._generate_create_object_func(resource_field_name, rest_resource)
        for view_desc in rest_resource.extra_views:
            cls._generate_extra_view_func(view_desc, resource_field_name, rest_resource)

    def _generate_create_object_func(cls, resource_field_name, rest_resource):
        if "create" not in rest_resource.methods:
            return
        func_name = "create_{0}".format(rest_resource.name)
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, request_type='get_create_object_request', include_kwargs=True)
        setattr(cls, func_name, func)

    def _generate_list_func(cls, resource_field_name, rest_resource):
        if "list" not in rest_resource.methods:
            return
        func_name = "get_{0}".format(rest_resource.plural_name)
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, request_type='get_list_request')
        setattr(cls, func_name, func)

    def _generate_get_object_func(cls, resource_field_name, rest_resource):
        if "detail" not in rest_resource.methods:
            return
        func_name = 'get_{0}'.format(rest_resource.name)
        required_args = rest_resource.required_args + [rest_resource.object_arg]
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, request_type='get_object_request')
        setattr(cls, func_name, func)

    def _generate_delete_object_func(cls, resource_field_name, rest_resource):
        if "delete" not in rest_resource.methods:
            return
        func_name = 'delete_{0}'.format(rest_resource.name)
        required_args = rest_resource.required_args + [rest_resource.object_arg]
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, request_type='get_delete_object_request')
        setattr(cls, func_name, func)

    def _generate_update_object_func(cls, resource_field_name, rest_resource):
        if "update" not in rest_resource.methods:
            return
        func_name = 'update_{0}'.format(rest_resource.name)
        required_args = rest_resource.required_args + [rest_resource.object_arg]
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, request_type='get_update_object_request', include_kwargs=True)
        setattr(cls, func_name, func)

    def _generate_extra_view_func(cls, extra_view_desc, resource_field_name, rest_resource):
        func_name = extra_view_desc["name"]
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, extra_view_name=extra_view_desc["path"])
        setattr(cls, func_name, func)

    def _generate_resource_func(cls, func_name, resource_field_name, required_args, request_type=None, extra_view_name=None, include_kwargs=False):
        # This is quite nasty, the point of it is to generate a function which
        # has named required arguments so that it is nicely self documenting.
        # If you're having trouble following it stick a print statement in
        # around the func_definition variable and the import in a shell.
        required_args_str = ",".join(required_args)
        if len(required_args) > 0:
            required_args_str += ","
        get_request_args = ",".join(["{0}={0}".format(argname) for argname in required_args])
        if request_type:
            get_request_string = "self.{0}.{1}({2})".format(resource_field_name, request_type, get_request_args)
        else:
            get_request_string = "self.{0}.get_extra_view_request(\"{1}\",{2})".format(resource_field_name, extra_view_name, get_request_args)
        if include_kwargs:
            func_definition = "def {0}(self, {1} **kwargs): return self._execute_request({2}, data=kwargs)".format(
                func_name, required_args_str, get_request_string)
        else:
            func_definition = "def {0}(self, {1}): return self._execute_request({2})".format(
                func_name, required_args_str, get_request_string)
        func = compile(func_definition, __file__, 'exec')
        d = {}
        exec func in d
        return d[func_name]





class Client(object):
    __metaclass__ = RestClientMetaClass
    BASE_URL = "http://api.2600hz.com:8000/v1"

    _accounts_resource = RestResource("account",
                                      "/accounts/{account_id}")
    _conference_resource = RestResource("conference",
                                       "/accounts/{account_id}/conferences/{conference_id}")
    _device_resource = RestResource("device",
                                    "/accounts/{account_id}/devices/{device_id}",
                                    extra_views=[{"name":"get_all_devices_status", "path":"status"}])

    def __init__(self, api_key=None, password=None, account_name=None,
                 username=None):
        if not api_key and not password:
            raise RuntimeError("You must pass either an api_key or an "
                               "account name/password pair")

        if password or account_name or username:
            if not (password and account_name and username):
                raise RuntimeError("If using account name/password "
                                   "authentication then you must specify "
                                   "password, userame and account_name "
                                   "arguments")
            self.auth_request = UsernamePasswordAuthRequest(username,
                                                            password,
                                                            account_name)
        else:
            self.auth_request = ApiKeyAuthRequest(api_key)

        self.api_key = api_key
        self._authenticated = False
        self.auth_token = None

    def authenticate(self):
        if not self._authenticated:
            self.auth_token = self.auth_request.execute(
                self.BASE_URL)["auth_token"]
            self._authenticated = True
        return self.auth_token

    def _execute_request(self, request, **kwargs):
        if request.auth_required:
            kwargs["token"] = self.auth_token
        return request.execute(self.BASE_URL, **kwargs)
