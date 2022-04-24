from setuptools import setup

from proxy_harvester.proxy_harvesters import __version__

setup(
    name='proxy_harvesters',
    version=__version__,

    url='https://github.com/imPDA/proxy_harvester',
    author='imPDA',

    py_modules=['proxy_harvesters'],
)
