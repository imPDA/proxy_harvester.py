from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum, auto


class ProxyType(Enum):
    HTTP = auto()
    HTTPS = auto()
    Socks4 = auto()
    Socks5 = auto()


@dataclass
class ProxyAddress:
    ip: str
    ports: List[int] = field(default_factory=list)
    types: List[ProxyType] = field(default_factory=list)
    data: Dict = field(default_factory=dict)
    statistics: Dict = field(default_factory=dict)
