from kazoo.request_objects import KazooRequest
import re

class RestResource(object):

    def __init__(self, name, path):
        self._param_regex = re.compile("{([a-zA-Z0-9_]+)}")
        self.name = name
        self._check_at_least_one_argument(path)
        self.required_args = self._get_required_arguments(path)
        self.object_arg = self._get_object_argument(path)
        self.path = self._get_resource_path(path)

    def _get_resource_path(self, path):
        return path[:path.find(self.object_arg) - 2]

    def _check_at_least_one_argument(self, path):
        if len(self._get_params(path)) == 0:
            raise ValueError("Rest resources need at least one argument")

    def _get_required_arguments(self, path):
        params = self._get_params(path)
        if len(params) > 1:
            return params[:-1]

    def _get_object_argument(self, path):
        return self._get_params(path)[-1]

    def _get_params(self, path):
        param_names = self._param_regex.findall(path)
        return param_names

    def get_list_request(self, **kwargs):
        relative_path = self.path.format(**kwargs)
        return KazooRequest(relative_path)


    @property
    def plural_name(self):
        return self.name + "s"
