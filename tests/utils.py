import os.path as path

def load_fixture(filename):
    full_path = path.join(path.abspath(path.dirname(__file__)), "fixtures", filename)
    return open(full_path).read()
