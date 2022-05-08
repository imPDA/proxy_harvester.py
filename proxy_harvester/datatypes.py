from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum, auto


# class ProxyType(Enum):
#     HTTP = auto()
#     HTTPS = auto()
#     socks4 = auto()
#     socks5 = auto()


@dataclass
class ProxyAddress:
    ip: str
    ports: dict[str, int] = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    statistics: dict = field(default_factory=dict)

    def to_json(self):
        return self.__dict__

    @classmethod
    def from_json(cls, some_json):
        return cls(
            ip=some_json['ip'],
            ports=some_json['ports'],
            data=some_json['data'],
            statistics=some_json['statistics'],
        )

    def __eq__(self, other):
        if isinstance(other, ProxyAddress):
            return self.ip == other.ip and self.ports == other.ports


if __name__ == '__main__':
    pass
    # a = ProxyType['HTTP']
    # b = ProxyType.HTTP
    # print(type(a))
    # print(type(b))
