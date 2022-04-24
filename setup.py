from setuptools import setup, find_packages

from proxy_harvester.proxy_harvesters import __version__

setup(
    name='ProxyHarvesters',
    version=__version__,
    url='https://github.com/imPDA/proxy_harvester',
    author='imPDA',
    packages=find_packages(),
)
