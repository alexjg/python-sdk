import json
import os.path as path


def load_fixture(filename):
    full_path = path.join(path.abspath(path.dirname(__file__)),
                          "fixtures", filename)
    return open(full_path).read()


def load_fixture_as_dict(json_filename):
    raw = load_fixture(json_filename)
    return json.loads(raw)
