import typing
from typing import List, Union
from dataclasses import dataclass


@dataclass
class Event:
    date: str
    text: str
    address: str = ''
    # v2 fields
    datetime: str = ''
    organization: str = ''
    injured_fio: str = ''
    addr_mappings: typing.List = None
    types_mappings: typing.List = None


@dataclass
class EventFromDb(Event):
    id: int = -1
    version: str = 'default'
    journal_id: int = -1
    created_at: str = 'default'


@dataclass
class FireDep:
    fires_num: str = ''
    dead: str = ''
    injured: str = ''


@dataclass
class PoliceDep:
    incidents_num: str = ''
    notes: str = ''


@dataclass
class AmbulanceDep:
    dead: str = ''
    injured: str = ''
    traumatized: str = ''


@dataclass
class TouristGroups:
    num: str = ''
    persons: str = ''


@dataclass
class MCHSDep:
    tourist_groups: TouristGroups = None
    dtp: str = ''
    search_jobs: str = ''
    save_jobs: str = ''
    another: str = ''


@dataclass
class Weather:
    place: str = ''
    external_temp: str = ''
    in_out_tube_temp: str = ''
    in_out_tube_pressure: str = ''


@dataclass
class Day:
    date: str
    events: List[Event]
    # v2 fields
    fire_dep: FireDep = None
    police_dep: PoliceDep = None
    ambulance_dep: AmbulanceDep = None
    mchs_dep: MCHSDep = None
    weather: typing.List[Weather] = None


@dataclass
class Journal:
    name: str
    days: List[Union[Day]]
    version: str = 'default'
    notes: str = ''
    duty_person: str = ''
