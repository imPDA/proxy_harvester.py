from setuptools import setup, find_packages

with open('requirements.txt', 'r', encoding='utf-16') as f:
    required = f.read().splitlines()
    print(required)

setup(
    name='ProxyHarvester',
    version='0.6.dev3',
    url='https://github.com/imPDA/proxy_harvester.py',
    author='imPDA',
    # packages=find_packages(),
    packages=['proxy_harvester'],
    install_requires=required,
)


