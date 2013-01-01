import json
import requests
import kazoo.exceptions as exceptions
from kazoo.request_objects import KazooRequest, UsernamePasswordAuthRequest, \
        ApiKeyAuthRequest

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

    def _generate_create_object_func(cls, resource_field_name, rest_resource):
        func_name = "create_{0}".format(rest_resource.name)
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, 'create_object_request', include_kwargs=True)
        setattr(cls, func_name, func)

    def _generate_list_func(cls, resource_field_name, rest_resource):
        func_name = "get_{0}".format(rest_resource.plural_name)
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, 'get_list_request')
        setattr(cls, func_name, func)

    def _generate_get_object_func(cls, resource_field_name, rest_resource):
        func_name = 'get_{0}'.format(rest_resource.name)
        required_args = rest_resource.required_args + [rest_resource.object_arg]
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, 'get_object_request')
        setattr(cls, func_name, func)

    def _generate_delete_object_func(cls, resource_field_name, rest_resource):
        func_name = 'delete_{0}'.format(rest_resource.name)
        required_args = rest_resource.required_args + [rest_resource.object_arg]
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, 'get_delete_object_request')
        setattr(cls, func_name, func)

    def _generate_update_object_func(cls, resource_field_name, rest_resource):
        func_name = 'update_{0}'.format(rest_resource.name)
        required_args = rest_resource.required_args + [rest_resource.object_arg]
        func = cls._generate_resource_func(func_name, resource_field_name, required_args, 'get_update_object_request', include_kwargs=True)
        setattr(cls, func_name, func)

    def _generate_resource_func(cls, func_name, resource_field_name, required_args, request_type, include_kwargs=False):
        # This is quite nasty, the point of it is to generate a function which
        # has named required arguments so that it is nicely self documenting.
        required_args_str = ",".join(required_args)
        get_request_args = ",".join(["{0}={0}".format(argname) for argname in required_args])
        get_request_string = "self.{0}.{1}({2})".format(resource_field_name, request_type, get_request_args)
        if include_kwargs:
            func_definition = "def {0}(self, {1}, **kwargs): return self._execute_request(self, {2}, data=kwargs)".format(
                func_name, required_args_str, get_request_string)
        else:
            func_definition = "def {0}(self, {1}): return self._execute_request(self, {2})".format(
                func_name, required_args_str, get_request_string)
        func = compile(func_definition, __file__, 'exec')
        d = {}
        exec func in d
        return d[func_name]





class Client(object):
    BASE_URL = "http://api.2600hz.com:8000/v1"

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

    def get_account(self, account_id):
        get_account_request = KazooRequest("/accounts/{account_id}")
        return self._execute_request(get_account_request,
                                     account_id=account_id)

    def update_account(self, account_id, **kwargs):
        """Update the account"""
        update_account_request = KazooRequest("/accounts/{account_id}")
        return self._execute_request(update_account_request,
                                     account_id=account_id,
                                     method='post',
                                     data=kwargs)

    def delete_account(self, account_id):
        delete_account_request = KazooRequest("/accounts/{account_id}")
        return self._execute_request(delete_account_request,
                                     account_id=account_id,
                                     method='delete')

    def get_callflows(self, account_id):
        get_callflows_request = KazooRequest("/accounts/{account_id}/callflows")
        return self._execute_request(get_callflows_request,
                                     account_id=account_id)

    def add_callflow(self, account_id, **kwargs):
        add_callflow_req = KazooRequest("/accounts/{account_id}/callflows")
        return self._execute_request(add_callflow_req,
                                     account_id=account_id,
                                     method="put",
                                     data=kwargs)

    def update_callflow(self, account_id, callflow_id, **kwargs):
        update_callflow_req = KazooRequest("/accounts/{account_id}/callflows/{callflow_id}")
        return self._execute_request(update_callflow_req,
                                     account_id=account_id,
                                     callflow_id=callflow_id,
                                     data=kwargs,
                                     method="post")

    def delete_callflow(self, account_id, callflow_id):
        delete_callflow_req = KazooRequest("/accounts/{account_id}/callflows/{callflow_id}")
        return self._execute_request(delete_callflow_req,
                                     account_id=account_id,
                                     callflow_id=callflow_id,
                                     method="delete")


