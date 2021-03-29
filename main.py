import asyncio
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import re
import logging
from logging import StreamHandler, Formatter
import concurrent.futures
from inspect import getgeneratorstate
import pickle
import pathlib


def generator_initializer(func):
    def wrap(*args, **kwargs):
        g = func(*args, **kwargs)
        g.send(None)
        return g
    return wrap


class Requester:
    """do-CUM-entation"""

    def __init__(self, *args, **kwargs):
        # TODO: инкапсулировать, сделать проверку на None
        self.loop = kwargs.get('loop', None)
        self.executor = kwargs.get('executor', None)

        self.url = kwargs.get('url', None)
        self.name = kwargs.get('name', None)
        self.response = None
        self.soup = None
        self.browser = kwargs.get('browser', None)
        if self.browser is not None:
            logger.info('Работаем с cуществующим браузером {0}'.format(self.browser))

        self._last_update = 0
        self._update_period = 0.5*60
        self._status = 'awaiting'

    async def update(self, func):
        await asyncio.sleep(self._update_period)
        self.loop.run_in_executor(self.executor, func)

    @staticmethod
    def _create_browser():
        options = Options()

        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        options.add_argument('--enable-javascript')

        path_to_chrome_driver = './chrome89/chromedriver.exe'  # chrome version 89
        browser = webdriver.Chrome(path_to_chrome_driver, options=options)

        return browser

    def no_response(self):
        if self.response is None:
            logger.error('Ответ не сохранен')
            return True
        else:
            return False

    def captcha(self):
        captcha = self.soup.find_all("body", onload="e=document.getElementById('captcha');if(e){e.focus();}")
        if captcha:
            logger.warning('В {0} капча'.format(self.name))
            return True
        else:
            return False

    def send_request(self):
        if self.browser is None:
            self.browser = self._create_browser()
            logger.info('Нет браузера, создаем {0}'.format(self.browser))

        logger.debug('Запрашиваем {0}'.format(self.url))

        self.browser.get(self.url)
        self.update_response()

    def update_response(self):
        self.response = self.browser.page_source
        self.soup = BeautifulSoup(self.response, 'html.parser')

    """
    def parse_request(self):
        soup = BeautifulSoup(self.response, 'html.parser')

        captcha = soup.find_all("body", onload="e=document.getElementById('captcha');if(e){e.focus();}")
        if captcha:
            logger.warning('В {0} капча'.format(self.name))
            return
    """

    # TODO: ??
    # def get_request(self):
    #     return self.response

    def close_browser(self):
        # input('Закрытие браузера, продолжить?')
        try:
            self.browser.close()
            self.browser.quit()
        except WebDriverException as e:
            logger.error('WebDriverException: {0}'.format(e.msg))
        else:
            logger.info('Закрытие {0} ({1})'.format(self.name, self.browser))
            self.browser = None

    def __del__(self):
        if self.browser is not None:
            self.close_browser()


class ProxyRequester(Requester):
    """do-CUM-entation"""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.counter = None
        self._directory = './dump'
        self._path_to_dump = '{path}/{name}.pickle'.format(path=self._directory, name=self.name)
        self.proxy_addresses = self.read_dump()

    def get_random_proxy(self):
        if self.proxy_addresses == {}:
            print('В {0} пока пусто'.format(self.name))

    def read_dump(self):
        pathlib.Path(self._directory).mkdir(parents=True, exist_ok=True)
        try:
            file = open(self._path_to_dump, 'rb')
        except FileNotFoundError:
            with open(self._path_to_dump, 'wb') as file:
                pickle.dump({}, file)
                return {}
        else:
            with file:
                return pickle.load(file)

    # TODO: запись дампа по времени?
    def write_dump(self):
        with open(self._path_to_dump, 'wb') as file:
            pickle.dump(self.proxy_addresses, file)

    def renew_counter(self):
        self.counter = self.proxy_counter()

    # TODO: итератор! переделать?
    def log_amount(self):
        try:
            self.counter.throw(StopIteration)
        except StopIteration as e:
            logger.debug('Из {0} было добавлено {1} новых прокси'.format(self.name, e.value[0]))
        finally:
            self.renew_counter()

    @generator_initializer
    def proxy_counter(self):
        new = 0
        total = 0
        while True:
            try:
                if_known = yield
            except StopIteration:
                break
            else:
                if if_known == 'unknown':
                    new += 1
                total += 1
        return new, total

    def add_proxy(self, proxy):
        if self.counter is None:  # TODO: смахивает на костыли с итератором
            self.counter = self.proxy_counter()

        self.counter.send('known' if proxy['ip'] in self.proxy_addresses else 'unknown')
        self.proxy_addresses.update({proxy['ip']: proxy})

    # TODO: могу я создать метод, который обязательно должен быть переопределен или
    #  для этого надо создавать отдельную проверку при конструировании?

    def close_browser(self):
        self.write_dump()
        super().close_browser()


class ProxyHidemyname(ProxyRequester):
    # https://hidemy.name/ru/proxy-list/?anon=4&start=64#list
    # anonymity : 1-Нет, 2-Низкая, 3-Средняя, 4-Высокая 1234-Все

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs, name='Хайдмайнэйм')
        self.url = 'https://hidemy.name/ru/proxy-list/?anon=4'

    def run(self):
        base_url = self.url
        for i in range(0, 11):
            # TODO: рефактор запроса
            self.url = self.url if i == 0 else '{base}start={page}#list'.format(base=base_url, page=64*i)

            self.send_request()
            self.parse_request()

        self.url = base_url
        self.close_browser()
        print('{} {}'.format('Создаем задачу на перезапуск', self.name))
        self.loop.create_task(self.update(self.run))

    def proceed_row(self, row):
        new_proxy = dict()

        new_proxy['ip'] = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', str(row)).group(0)
        new_proxy['port'] = re.search(r'<td>(\d{1,5})</td>', str(row)).group(1)
        new_proxy['country'] = re.search(r'<span class="country">([\w\s\-\,\'\’]*)</span>', str(row)).group(1)
        new_proxy['city'] = re.search(r'<span class="city">([\w\s\-\,\'\’]*)</span>', str(row)).group(1)
        new_proxy['ping'] = re.search(r'<p>(\d+) мс</p>', str(row)).group(1)
        new_proxy['type'] = re.findall(r'SOCKS4|SOCKS5|HTTP|HTTPS', str(row))

        return new_proxy

    def parse_request(self):
        if self.no_response(): return
        if self.captcha(): return

        table_of_proxy = self.soup.find_all("div", {'class': 'table_block'})[0].find_all("tbody")[0]
        list_of_proxy = table_of_proxy.find_all("tr")

        for row in list_of_proxy:
            # Может быть проблема при поиске регулярных выражений
            # noinspection PyBroadException
            try:
                new_proxy = self.proceed_row(row)
            except Exception as e:
                logger.exception(row)
            else:
                self.add_proxy(new_proxy)
        self.log_amount()

        # logger.debug('Новый прокси из {0}: {1}:{2}, {3}, {4}, {5}мс, {6}'.format(
        #     self.name, ip_address, port, country, city, ping, ', '.join(type_of_proxy)))


# class ProxyAwmproxy(ProxyRequester):
#     def __init__(self, *args, **kwargs):
#         super().__init__(self, *args, **kwargs)
#         self.name = 'АВМпрокси'
#         self.url = 'https://awmproxy.com/'
#
#     def run(self):
#         pass
#
#     def parse_request(self):
#         pass


class ProxyBestproxies(ProxyRequester):
    # https://best-proxies.ru/proxylist/free/

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs, name='Бестпроксиз')
        self.url = 'https://best-proxies.ru/proxylist/free/'
        self.dict_types_of_proxy = {
            'HTTP': 'HTTP',
            'HTTPS': 'HTTPS',
            'SOCKS4': 'SOCKS4',
            'SOCKS5': 'SOCKS5',
            'HTTP': 'HTTP',
            'Для <span style="color:#4066db">G</span><span style="color:#ee2c36">o</span><span style="color:#fdad0a">o</span><span style="color:#4066db">g</span><span style="color:#019d14">l</span><span style="color:#ee2c36">e</span> без капчи': 'Google',
            'Для <span class="red">Я</span>ндекс без капчи': 'Yandex',
            'Для <span style="color:#f7a600">@</span><span style="color:#3c73a8">Mail</span><span style="color:#f7a600">.Ru</span>': 'Mail.ru',
            'Для <span style="color:#00acee">Twitter</span>': 'Twitter',
            'С возможностью отправки почты': 'SMTP',
        }

    def run(self):  # TODO: переписать
        while True:
            self.send_request()
            time.sleep(2)
            if re.search(r'<title>Проверка браузера</title>', self.response).group(0) is not None:
                self.update_response()
                break
        self.parse_request()
        self.close_browser()
        print('{} {}'.format('Создаем заадчу на перезапуск', self.name))
        self.loop.create_task(self.update(self.run))
        # self.loop.run_in_executor(self.executor, self.run)

    def proceed_row(self, type_row, data_row):
        new_proxy = dict()

        new_proxy['ip'] = re.search(r'data-ip=\"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\"', str(data_row)).group(1)
        new_proxy['port'] = re.search(r'data-port=\"(\d{1,5})\"', str(data_row)).group(1)
        new_proxy['location'] = re.search(r'data-geo=\"([\w\s\-\,\'\’\?\.]*)\"', str(data_row)).group(1)
        new_proxy['ping'] = re.search(r'<br/>(\d+) мсек', str(data_row)).group(1)
        new_proxy['type'] = re.findall(r'data-types=\"([HTPSOCK45/,\s]*)\"', str(data_row))[0].split(', ')
        new_proxy['grade'] = self.dict_types_of_proxy[re.findall(r'<strong>(.+)</strong>', str(type_row))[0]]
        new_proxy['anonymity'] = re.findall(r'Высоко анонимный|Прозрачный|Анонимный', str(data_row))[0]

        return new_proxy

    def parse_request(self):
        if self.no_response(): return
        if self.captcha(): return

        table_of_proxy = self.soup.find_all("tbody")[0]
        list_of_proxies = table_of_proxy.find_all("tr")

        for i in range(2, len(list_of_proxies), 2):
            # noinspection PyBroadException
            try:
                type_row = list_of_proxies[i]
                data_row = list_of_proxies[i+1]
                new_proxy = self.proceed_row(type_row, data_row)
            except Exception as e:
                logger.exception(data_row)
            else:
                self.add_proxy(new_proxy)
        self.log_amount()

    # TODO: улучшить
    # logger.debug('Новый прокси из {0} для {1}: {2}:{3}, {4}, {5}мс, {6}'.format(
    #     self.name, proxy_grade, ip_address, port, location, ping, ', '.join(type_of_proxy)))


# TODO: добавить сайты


def startup_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stderr)
    handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    _logger.addHandler(handler)

    return _logger


# async def timer():
#     last = time.time()
#     print('{}'.format('Start'))
#     await asyncio.sleep(10)
#     print('{} - {}'.format('End', time.time()-last))


async def run_browsers(_executor):
    active = ['Хайдмайнэйм',
              # 'АМВпрокси',
              'Бестпроксиз',
              ]

    loop = asyncio.get_event_loop()
    browser_list = list()
    for some_proxy_site in ProxyRequester.__subclasses__():
        initialized = some_proxy_site(loop=loop, executor=executor)
        if initialized.name in active:
            browser_list.append(loop.run_in_executor(_executor, initialized.run))

    completed, pending = await asyncio.wait(browser_list)
    results = [t.result() for t in completed]


if __name__ == '__main__':
    logger = startup_logger()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3, )
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            run_browsers(executor)
        )
        event_loop.run_forever()
        # TODO: сохранится ли многопоточность???
    finally:
        event_loop.close()
    # TODO: как добавлять по ходу спектакля?

    input('Ввод: ')
