import typing
from dataclasses import dataclass


@dataclass
class Event:
    date: str
    address: str
    text: str


@dataclass
class Day:
    date: str
    events: typing.List[Event]


@dataclass
class Journal:
    name: str
    days: typing.List[Day]
