from datetime import date
from dataclasses import dataclass

@dataclass
class Cliente:
    nombre: str
    telefono: str

@dataclass
class Cita:
    fecha: date
    disponible: bool
