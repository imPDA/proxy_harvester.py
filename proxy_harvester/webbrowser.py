from abc import ABC, abstractmethod

# from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import seleniumwire.undetected_chromedriver as uc
from seleniumwire import webdriver, utils
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional

from pprint import pprint
import json


class DriverFactory(ABC):
    """Driver abstract factory."""

    @staticmethod
    @abstractmethod
    def get_driver(*args, **kwargs) -> webdriver:
        raise NotImplementedError


class ChromeWithWire(DriverFactory):
    """SeleniumChrome with Wire"""

    @staticmethod
    def get_driver(*args, **kwargs) -> webdriver:
        svc = Service(ChromeDriverManager().install())

        options = {
            # 'proxy': {
            #     'http': 'http://myusername:password@myproxyserver.com:123456',
            #     'https': 'http://myusername:password@myproxyserver.com:123456',
            #     'no_proxy': 'localhost,127.0.0.1'  # excludes
            # }
        }

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')

        if kwargs.get['headless'] is True:
            chrome_options.add_argument('--headless')

        # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        # chrome_options.add_argument('--ignore-ssl-errors')

        driver = webdriver.Chrome(service=svc, seleniumwire_options=options, options=chrome_options)
        return driver


class UCWithWire(DriverFactory):
    """SeleniumChrome with Wire"""

    @staticmethod
    def get_driver(*args, **kwargs) -> webdriver:
        # svc = Service(ChromeDriverManager().install())
        options = {
            # 'proxy': {
            #     'http': 'http://myusername:password@myproxyserver.com:123456',
            #     'https': 'http://myusername:password@myproxyserver.com:123456',
            #     'no_proxy': 'localhost,127.0.0.1'  # excludes
            # }
        }

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')

        if kwargs.get['headless'] is True:
            chrome_options.add_argument('--headless')

        # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        # chrome_options.add_argument('--ignore-ssl-errors')

        driver = uc.Chrome(options=chrome_options, seleniumwire_options=options)
        return driver


class WebBrowser:
    """Web browser."""

    def __init__(self, driver: DriverFactory, *args, **kwargs):
        self._driver = driver.get_driver(args, kwargs)

    def open(self, url):
        self._driver.get(url)

    @property
    def driver(self) -> webdriver:
        return self._driver

    @property
    def page_content(self):
        return self._driver.page_source


def main():
    # my_browser = WebBrowser(driver=ChromeWithWire())
    # my_browser.open(url='https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?ItemID=211')
    # for request in my_browser.driver.requests:
    #     response = request.response
    #     if response and "Search?ItemID=" in request.url:
    #         string = utils.decode(response.body, response.headers.get('Content-Encoding', 'identity')).decode()
    #         pprint(json.loads(string))
    # pprint(my_browser.page_content)
    pass


if __name__ == '__main__':
    main()

