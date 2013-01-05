from kazoo.request_objects import KazooRequest
import re

method_types = ["detail", "list", "update", "create", "delete"]


class RestResource(object):

    def __init__(self, name, path, plural_name=None, extra_views=[],
                 methods=method_types, exclude_methods=[]):
        self._param_regex = re.compile("{([a-zA-Z0-9_]+)}")
        self.name = name
        self._plural_name = plural_name
        self._check_at_least_one_argument(path)
        self.required_args = self._get_required_arguments(path)
        self.object_arg = self._get_object_argument(path)
        self.path = self._get_resource_path(path)
        self._initialize_extra_view_descriptions(extra_views)
        self._initialize_methods(methods, exclude_methods)

    def _initialize_methods(self, methods, exclude_methods):
        self.methods = list(set(methods) - set(exclude_methods))

    def _get_resource_path(self, path):
        return path[:path.find(self.object_arg) - 2]

    def _check_at_least_one_argument(self, path):
        if len(self._get_params(path)) == 0:
            raise ValueError("Rest resources need at least one argument")

    def _get_required_arguments(self, path):
        params = self._get_params(path)
        if len(params) > 1:
            return params[:-1]
        return []

    def _get_object_argument(self, path):
        return self._get_params(path)[-1]

    def _get_params(self, path):
        param_names = self._param_regex.findall(path)
        return param_names

    def _get_full_url(self, params):
        object_id = params[self.object_arg]
        return self.path.format(**params) + "/{0}".format(object_id)

    def _initialize_extra_view_descriptions(self, view_descs):
        self.extra_views = []
        for view_desc in view_descs:
            if hasattr(view_desc, "has_key"):
                result = view_desc
            else:
                result = {"name": "get_" + view_desc, "path": view_desc}
            if "scope" not in result:
                result["scope"] = "aggregate"
            self.extra_views.append(result)

    def get_list_request(self, **kwargs):
        relative_path = self.path.format(**kwargs)
        return KazooRequest(relative_path)

    def get_object_request(self, **kwargs):
        return KazooRequest(self._get_full_url(kwargs))

    def get_update_object_request(self, **kwargs):
        return KazooRequest(self._get_full_url(kwargs), method='post')

    def get_delete_object_request(self, **kwargs):
        return KazooRequest(self._get_full_url(kwargs), method='delete')

    def get_create_object_request(self, **kwargs):
        return KazooRequest(self.path.format(**kwargs), method='put')

    def get_extra_view_request(self, viewname, **kwargs):
        view_desc = None
        for desc in self.extra_views:
            if desc["path"] == viewname:
                view_desc = desc
        if view_desc is None:
            raise ValueError("Unknown extra view name {0}".format(viewname))
        if view_desc["scope"] == "aggregate":
            return KazooRequest(self.path.format(**kwargs) + "/" + viewname)
        return KazooRequest(self._get_full_url(kwargs) + "/" + viewname)

    @property
    def plural_name(self):
        if self._plural_name:
            return self._plural_name
        return self.name + "s"
