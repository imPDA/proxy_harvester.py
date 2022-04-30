from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='ProxyHarvester',
    version='0.3.dev1',
    url='https://github.com/imPDA/proxy_harvester.py',
    author='imPDA',
    # packages=find_packages(),
    packages=['proxy_harvester'],
    install_requires=required,
)


