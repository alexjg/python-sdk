import setuptools
from distutils.core import setup

#Nasty hack to get version without importing currently uninstalled module
import os.path as path
version_line = open(path.join(path.dirname(__file__), "kazoo", "__init__.py")).read().split("\n")[2]
version = version_line.split("\"")[1]

setup(
    name="kazoo-api",
    version=version,
    description="Wrapper for the Kazoo API",
    author="Alex Good",
    url="http://2600hz.com/platform.html",
    packages = ["kazoo"],
    install_requires=["requests >=0.14,< 1.0"],
    license="MIT License",
    readme='README.rst',
)
