from typing import Dict, Optional
import pickle
from pprint import pprint
from pathlib import Path

from proxy_harvester.datatypes import ProxyAddress, ProxyType


class ProxyDatabase:
    """Database."""
    def __init__(self, path: Optional[str | Path] = None):
        self._path = path if path else 'database.pickle'
        self._database: Dict | None = None
        self._database = self.open_from_file()

    @property
    def data(self):
        return self._database

    def open_from_file(self) -> Dict:
        try:
            with open(self._path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            print('File not found, create empty file first!')
            self.save_to_file()
            return {}

    def save_to_file(self):
        with open(self._path, 'wb') as f:
            pickle.dump(self._database, f)

    def add_new_proxy(self, proxy: ProxyAddress):
        if proxy.ip not in self._database:
            self._database.update({proxy.ip: proxy})
        else:
            pass
            # print(f"{proxy} already in database.")

    def pop_proxy(self, proxy: str | ProxyAddress):
        if isinstance(proxy, ProxyAddress):
            return self._database.pop(proxy.ip)
        return self._database.pop(proxy)


def main():
    db = ProxyDatabase()
    pprint(db.data)

    # db.add_new_proxy(ProxyAddress(
    #     ip='192.155.107.58',
    #     ports=[1080],
    #     types=[ProxyType.HTTPS],
    # ))
    #
    # db.pop_proxy('192.155.107.58')

    db.save_to_file()


if __name__ == '__main__':
    main()
