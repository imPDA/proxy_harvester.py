from abc import ABC, abstractmethod

# from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import seleniumwire.undetected_chromedriver as uc
import undetected_chromedriver.v2 as uc2
from seleniumwire import webdriver, utils
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Union

from pprint import pprint
import json


class DriverFactory(ABC):
    """Driver abstract factory."""

    @staticmethod
    @abstractmethod
    def get_driver(*args, **kwargs) -> Union[webdriver.Chrome, webdriver.Firefox, webdriver.Edge]:
        raise NotImplementedError


class ChromeWithWire(DriverFactory):
    """SeleniumWire-Chrome """
    @staticmethod
    def get_driver(*args, **kwargs) -> webdriver.Chrome:
        svc = Service(ChromeDriverManager().install())

        options = {
            # 'proxy': {
            #     'http': 'http://myusername:password@myproxyserver.com:123456',
            #     'https': 'http://myusername:password@myproxyserver.com:123456',
            #     'no_proxy': 'localhost,127.0.0.1'  # excludes
            # }
        }

        chrome_options = webdriver.ChromeOptions()
        if kwargs.get('headless', True):
            chrome_options.add_argument('--headless')
        if kwargs.get('no_sandbox', False):
            chrome_options.add_argument('--no-sandbox')

        # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        # chrome_options.add_argument('--ignore-ssl-errors')

        driver = webdriver.Chrome(service=svc, seleniumwire_options=options, options=chrome_options)
        return driver


class UCWithWire(DriverFactory):
    """SeleniumWire-UndetectedChrome"""
    @staticmethod
    def get_driver(*args, **kwargs) -> webdriver.Chrome:
        options = {
            # 'proxy': {
            #     'http': 'http://myusername:password@myproxyserver.com:123456',
            #     'https': 'http://myusername:password@myproxyserver.com:123456',
            #     'no_proxy': 'localhost,127.0.0.1'  # excludes
            # }
        }

        chrome_options = uc.ChromeOptions()
        if kwargs.get('headless', True):
            chrome_options.add_argument('--headless')
        if kwargs.get('no_sandbox', False):
            chrome_options.add_argument('--no-sandbox')

        # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        # chrome_options.add_argument('--ignore-ssl-errors')

        driver = uc.Chrome(
            options=chrome_options,
            seleniumwire_options=options,
            version_main=100,  # TODO fix version
        )
        return driver


class WebBrowser:
    """Web browser"""
    def __init__(self, driver: DriverFactory, *args, **kwargs):
        self._driver = driver.get_driver(*args, **kwargs)

    def open(self, url):
        self._driver.get(url)

    @property
    def driver(self):
        return self._driver


def main():
    my_browser = WebBrowser(driver=UCWithWire(), headless=False)
    my_browser.open(url='https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?ItemID=211')
    # for request in my_browser.driver.requests:
    #     response = request.response
    #     if response and "Search?ItemID=" in request.url:
    #         string = utils.decode(response.body, response.headers.get('Content-Encoding', 'identity')).decode()
    #         pprint(json.loads(string))
    # pprint(my_browser.page_content)
    pass


if __name__ == '__main__':
    main()

