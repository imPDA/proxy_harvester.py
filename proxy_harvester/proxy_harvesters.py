import functools
from abc import ABC
import asyncio
import requests

from proxy_harvester.datatypes import ProxyAddress
from proxy_harvester.database import ProxyDatabase
from proxy_harvester.webbrowser import WebBrowser, ChromeWithWire

from typing import List
from bs4 import BeautifulSoup
from datetime import datetime
from proxy_harvester.datatypes import ProxyAddress
from pprint import pprint


class Harvester(ABC):
    async def get_new_proxy(self) -> List[ProxyAddress]:
        ...


# class FreeProxyListHarvester(Harvester):
#     """https://free-proxy-list.net/"""
#     @classmethod
#     async def get_new_proxy(cls) -> List[ProxyAddress]:
#         my_browser = WebBrowser(driver=ChromeWithWire())
#         my_browser.open(url='https://free-proxy-list.net/')
#         soup = BeautifulSoup(my_browser.page_content, 'html.parser')
#         return [
#             ProxyAddress(
#                 ip=proxy.split(':')[0],
#                 ports=[proxy.split(':')[1]],
#                 data={
#                     'source': 'free-proxy-list.net',
#                 },
#                 types=[ProxyType.HTTP, ProxyType.HTTPS]
#             )
#             for proxy
#             in soup.find_all('textarea', {'class': 'form-control'})[0].text.split('\n')[3:-1]
#         ]


class WebShareHarvester(Harvester):
    @classmethod
    async def get_new_proxy(cls) -> List[ProxyAddress]:

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(
                requests.get,
                "https://proxy.webshare.io/api/proxy/list/?page=1",
                headers={'Authorization': 'Token eacf2f49d212cde7b7dfcfe7c3a9561acfb1201b'}
            )
        )

        return [ProxyAddress(
            ip=proxy['proxy_address'],
            ports=proxy['ports'],
            data={
                'source': 'webshare',
                'username': proxy['username'],
                'password': proxy['password'],
            }
        ) for proxy in response.json()['results']]


class ProxyScrapeHarvester(Harvester):
    """https://proxyscrape.com/free-proxy-list"""

    URLS = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&simplified=true",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all&simplified=true",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
    ]

    @staticmethod
    async def _get_text(url) -> str:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(
                requests.get,
                url,
            )
        )
        return response.text

    @classmethod
    async def get_new_proxy(cls) -> List[ProxyAddress]:
        list_of_proxy = []

        for url, protocol in zip(cls.URLS, ['http', 'socks4', 'socks5']):
            proxy = await cls._get_text(url)
            list_of_proxy.append([
                ProxyAddress(
                    ip=proxy.split(':')[0],
                    ports={protocol: int(proxy.split(':')[1])},
                    data={'source': 'proxyscrape'},
                ) for proxy in proxy.splitlines()
            ])

        return list_of_proxy


async def main():
    # db = ProxyDatabase()
    # pprint(db.data.values())

    # for proxy in await FreeProxyListHarvester.get_new_proxy():
    #     db.add_new_proxy(proxy)
    #

    # print(datetime.now())
    # print(len(db.data))

    # for proxy in db.data.values():
    #     proxy.data.update({'source': 'free-proxy-list.net'})
    #     proxy.types = [ProxyType.HTTP, ProxyType.HTTPS]
    # db.save_to_file()

    # await asyncio.sleep(60*30)
    # await main()

    pprint(await ProxyScrapeHarvester.get_new_proxy())


if __name__ == '__main__':
    asyncio.run(main())
