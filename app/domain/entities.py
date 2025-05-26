from datetime import date
from dataclasses import dataclass

@dataclass
class Branch:
    id: int
    branch_name: str
    address: str
    city: str
    location_url: str
    is_active: bool

@dataclass
class Contact:
    id: str
    wa_id: str
    phone_number: str
    name: str
    step: str

@dataclass
class Client:
    id: int
    name: str
    phone_number: str
    contacts: list[Contact]

@dataclass
class Appointment:
    id: int
    date: date
    available: bool
