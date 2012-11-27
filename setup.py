import setuptools
from distutils.core import setup

setup(
    name="kazoo",
    version="0.0.1",
    description="Wrapper for the Kazoo API",
    author="Alex Good",
    url="http://2600hz.com/platform.html",
    packages = ["kazoo"],
    requires=["requests"],
    license="MIT License",
)
