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
            cls._generate_extra_view_func(view_desc, resource_field_name,
                                          rest_resource)

    def _generate_create_object_func(cls, resource_field_name, rest_resource):
        if "create" not in rest_resource.methods:
            return
        func_name = rest_resource.method_names["create"]
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(
            func_name,
            resource_field_name,
            required_args,
            request_type='get_create_object_request',
            requires_data=True)
        setattr(cls, func_name, func)

    def _generate_list_func(cls, resource_field_name, rest_resource):
        if "list" not in rest_resource.methods:
            return
        func_name = rest_resource.method_names["list"]
        required_args = rest_resource.required_args
        func = cls._generate_resource_func(
            func_name,
            resource_field_name,
            required_args,
            request_type='get_list_request')
        setattr(cls, func_name, func)

    def _generate_get_object_func(cls, resource_field_name, rest_resource):
        if "detail" not in rest_resource.methods:
            return
        func_name = rest_resource.method_names["object"]
        required_args = rest_resource.required_args + \
            [rest_resource.object_arg]
        func = cls._generate_resource_func(
            func_name,
            resource_field_name,
            required_args,
            request_type='get_object_request')
        setattr(cls, func_name, func)

    def _generate_delete_object_func(cls, resource_field_name, rest_resource):
        if "delete" not in rest_resource.methods:
            return
        func_name = rest_resource.method_names["delete"]
        required_args = rest_resource.required_args + \
            [rest_resource.object_arg]
        func = cls._generate_resource_func(
            func_name,
            resource_field_name,
            required_args,
            request_type='get_delete_object_request')
        setattr(cls, func_name, func)

    def _generate_update_object_func(cls, resource_field_name, rest_resource):
        if "update" not in rest_resource.methods:
            return
        func_name = rest_resource.method_names["update"]
        required_args = rest_resource.required_args + \
            [rest_resource.object_arg]
        func = cls._generate_resource_func(
            func_name,
            resource_field_name,
            required_args,
            request_type='get_update_object_request',
            requires_data=True)
        setattr(cls, func_name, func)

    def _generate_extra_view_func(cls, extra_view_desc, resource_field_name,
                                  rest_resource):
        func_name = extra_view_desc["name"]
        if extra_view_desc["scope"] == "aggregate":
            required_args = rest_resource.required_args
        else:
            required_args = rest_resource.required_args + \
                [rest_resource.object_arg]
        func = cls._generate_resource_func(
            func_name,
            resource_field_name,
            required_args,
            extra_view_name=extra_view_desc["path"])
        setattr(cls, func_name, func)

    def _generate_resource_func(cls, func_name, resource_field_name,
                                resource_required_args, request_type=None,
                                extra_view_name=None, requires_data=False):
        # This is quite nasty, the point of it is to generate a function which
        # has named required arguments so that it is nicely self documenting.
        # If you're having trouble following it stick a print statement in
        # around the func_definition variable and then import in a shell.
        required_args = list(resource_required_args)
        if requires_data:
            required_args.append("data")
        required_args_str = ",".join(required_args)
        if len(required_args) > 0:
            required_args_str += ","
        get_request_args = ",".join(["{0}={0}".format(argname)
                                     for argname in required_args])
        if request_type:
            get_request_string = "self.{0}.{1}({2})".format(
                resource_field_name, request_type, get_request_args)
        else:
            get_req_templ = "self.{0}.get_extra_view_request(\"{1}\",{2})"
            get_request_string = get_req_templ.format(
                resource_field_name, extra_view_name, get_request_args)
        if requires_data:
            func_definition = "def {0}(self, {1}): return self._execute_request({2}, data=data)".format(
                func_name, required_args_str, get_request_string)
        else:
            func_definition = "def {0}(self, {1}): return self._execute_request({2})".format(
                func_name, required_args_str, get_request_string)
        func = compile(func_definition, __file__, 'exec')
        d = {}
        exec func in d
        return d[func_name]


class Client(object):
    """The interface to the Kazoo API

    This class should be initialized either with a username, password and
    account name combination, or with an API key. Once you have initialized
    the client you will need to call :meth:`authenticate()` before you can
    begin making API calls.

        >>>import kazoo
        >>>client = kazoo.Client(api_key="sdfasdfas")
        >>>client.authenticate()

    API calls which require data take it in the form of a required argument
    called 'data' which is the last argument to the method. For example ::

        >>>client.update_account(acct_id, {"name": "somename", "realm":"superfunrealm"})

    Dictionaries and lists will automatically be converted to their appropriate
    representation so you can do things like: ::

        >>>client.update_callflow(acct_id, callflow_id, {"flow":{"module":"somemodule"}})

    Invalid data will result in an exception explaining the problem.

    The server response is returned from each method as a python dictionary of
    the returned JSON object, for example: ::

        >>>client.get_account(acct_id)
        {u'auth_token': u'abc437d000007d0454cc984f6f09daf3',
         u'data': {u'billing_mode': u'normal',
          u'caller_id': {},
          u'caller_id_options': {},
          u'id': u'c4f64412ad0057222c0009a3e7da011',
          u'media': {u'bypass_media': u'auto'},
          u'music_on_hold': {},
          u'name': u'test3',
          u'notifications': {},
          u'realm': u'4c8050.sip.2600hz.com',
          u'superduper_admin': False,
          u'timezone': u'America/Los_Angeles',
          u'wnm_allow_additions': False},
         u'request_id': u'ea6441422fb85000ad21db4f1e2326c1',
         u'revision': u'3-c16dd0a629fe1da0000e1e7b3e5fb35a',
         u'status': u'success'}

    For each resource exposed by the kazoo api there are corresponding methods
    on the client. For example, for the 'callflows' resource the
    correspondence is as follows.

        GET /accounts/{account_id}/callflows -> client.get_callflows(acct_id)
        GET /accounts/{account_id}/callflows/{callflow_id} -> client.get_callflow(acct_id, callflow_id)
        PUT /accounts/{account_id}/callflows/ -> client.create_callflow(acct_id, data)
        POST /account/{account_id}/callflows/{callflow_id} -> client.update_callflow(acct_id, data)
        DELETE /account/{account_id}/callflows/{callflow_id} -> client.delete_callflow(acct_id, callflow_id)

    Some resources do not have all methods available, in which case they are
    not present on the client.

    There are also some resources which don't quite fit this paradigm, they are:

        GET /accounts/{account_id}/children -> client.get_account_children(acct_id)
        GET /accounts/{account_id}/descendants -> client.get_account_descendants(acct_id)
        GET /accounts/{account_id}/devices/status -> client.get_all_devices_status(acct_id)
        GET /accounts/{account_id}/servers/{server_id}/deployment -> client.get_deployment(acct_id, server_id)
        GET /accounts/{account_id}/users/hotdesk -> client.get_hotdesk(acct_id)

    """
    __metaclass__ = RestClientMetaClass
    BASE_URL = "http://api.2600hz.com:8000/v1"

    _accounts_resource = RestResource("account",
                                      "/accounts/{account_id}",
                                      exclude_methods=["list",
                                                       "delete", "create"],
                                      extra_views=[
                                          {"name": "get_account_children",
                                           "path": "children",
                                           "scope": "object"},
                                          {"name": "get_account_descendants",
                                           "path": "descendants",
                                           "scope": "object"}])
    _callflow_resource = RestResource(
        "callflow",
        "/accounts/{account_id}/callflows/{callflow_id}")
    _conference_resource = RestResource(
        "conference",
        "/accounts/{account_id}/conferences/{conference_id}")
    _device_resource = RestResource(
        "device",
        "/accounts/{account_id}/devices/{device_id}",
        extra_views=[{"name": "get_all_devices_status", "path": "status"}])
    _directories_resource = RestResource(
        "directory",
        "/accounts/{account_id}/directories/{directory_id}",
        plural_name="directories")
    _global_resources = RestResource(
        "global_resource",
        "/accounts/{account_id}/global_resources/{resource_id}")
    _limits_resource = RestResource("limit",
                                    "/accounts/{account_id}/limits/{ignored}",
                                    methods=["list"])
    _local_resources_resource = RestResource(
        "local_resource",
        "/accounts/{account_id}/local_resources/{resource_id}")
    _media_resource = RestResource("media",
                                   "/accounts/{account_id}/media/{media_id}",
                                   plural_name="media",
                                   method_names={
                                       "list": "get_all_media"
                                   })
    _menus_resource = RestResource("menu",
                                   "/accounts/{account_id}/menus/{menu_id}")
    _phone_number_resource = RestResource(
        "phone_number",
        "/accounts/{account_id}/phone_numbers/{phone_number_id}")
    _queues_resource = RestResource("queue",
                                    "/accounts/{account_id}/queues/{queue_id}")
    _server_resource = RestResource(
        "server",
        "/accounts/{account_id}/servers/{server_id}",
        methods=["list"],
        extra_views=[
            {"name": "get_deployment",
             "path": "deployment",
             "scope": "object"},
            {"name": "get_server_log", "path": "log"}
        ])
    _create_server_deployment_resource = RestResource(
        "server_deployment",
        "/accounts/{account_id}/servers/{server_id}/deployment/{ignored}",
        methods=["create"])
    _temporal_rules_resource = RestResource(
        "temporal_rule",
        "/accounts/{account_id}/temporal_rules/{rule_id}")
    _users_resource = RestResource(
        "user",
        "/accounts/{account_id}/users/{user_id}",
        extra_views=[{"name": "get_hotdesk", "path": "hotdesk"}])
    _vmbox_resource = RestResource(
        "voicemail_box",
        "/accounts/{account_id}/vmboxes/{vmbox_id}")

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
        """Call this before making other api calls to fetch an auth token
        which will be automatically used for all further requests
        """
        if not self._authenticated:
            self.auth_token = self.auth_request.execute(
                self.BASE_URL)["auth_token"]
            self._authenticated = True
        return self.auth_token

    def _execute_request(self, request, **kwargs):
        if request.auth_required:
            kwargs["token"] = self.auth_token
        return request.execute(self.BASE_URL, **kwargs)
