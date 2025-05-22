from datetime import date
from dataclasses import dataclass

@dataclass
class Branch:
    id: int
    branch_name: str
    manager: int
    manager_name: str

@dataclass
class Contact:
    id: str
    wa_id: str
    phone_number: str
    name: str
    step: str

@dataclass
class Client:
    name: str
    phone_number: str
    contacts: list[Contact]

@dataclass
class Appointment:
    date: date
    available: bool
