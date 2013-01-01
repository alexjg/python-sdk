import re

class RestResource(object):

    def __init__(self, name, path):
        self.name = name
        self._check_at_least_one_argument(path)
        self.required_args = self._get_required_arguments(path)
        self.object_arg = self._get_object_argument(path)

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
        param_regex = re.compile("{([a-zA-Z0-9_]+)}")
        param_names = param_regex.findall(path)
        return param_names

    @property
    def plural_name(self):
        return self.name + "s"
