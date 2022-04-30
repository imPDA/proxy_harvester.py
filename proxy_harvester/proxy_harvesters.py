from abc import ABC
import asyncio
from datatypes import ProxyAddress
from typing import List

from bs4 import BeautifulSoup
from proxy_harvester.webbrowser import WebBrowser, ChromeWithWire
from database import ProxyDatabase
from datetime import datetime

__version__ = 'dev'

class Scrapper(ABC):
    async def get_new_proxy(self) -> List[ProxyAddress]:
        ...


class Harvester(ABC):
    async def get_proxy(self) -> List[ProxyAddress]:
        ...


class FreeProxyListHarvester(Scrapper):
    """https://free-proxy-list.net/"""
    @classmethod
    async def get_new_proxy(cls) -> List[ProxyAddress]:
        my_browser = WebBrowser(driver=ChromeWithWire())
        my_browser.open(url='https://free-proxy-list.net/')
        soup = BeautifulSoup(my_browser.page_content, 'html.parser')
        return [
            ProxyAddress(ip=proxy.split(':')[0], ports=[proxy.split(':')[1]])
            for proxy
            in soup.find_all('textarea', {'class': 'form-control'})[0].text.split('\n')[3:-1]
        ]


async def main():
    db = ProxyDatabase()

    for proxy in await FreeProxyListHarvester.get_new_proxy():
        db.add_new_proxy(proxy)

    db.save_to_file()
    print(datetime.now())
    print(len(db.data))

    await asyncio.sleep(60*30)
    await main()


if __name__ == '__main__':
    asyncio.run(main())
