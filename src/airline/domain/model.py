class Reserva:

    def __init__(self, voo_id, passageiro_id):
        self.voo_id = voo_id
        self.passageiro_id = passageiro_id
        self.status = StatusReserva.CONFIRMADA

    def cancelar(self):
        self.status = StatusReserva.CANCELADA

from enum import Enum

class StatusReserva(Enum):
        CONFIRMADA = "CONFIRMADA"
        CANCELADA = "CANCELADA"


# ----------------------------------
# agregado voo 

from dataclasses import dataclass

class StatusVoo(Enum):
    AGENDADO = "AGENDADO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"

@dataclass(frozen=True)
class Trecho:
    origem: str
    destino: str

class Voo:
    def __init__(self, numero_voo: str, trecho: Trecho=None):
        self.numero_voo = numero_voo
        self.trecho=trecho
        self.status = StatusVoo.AGENDADO

    def cancelar(self):
        self.status = StatusVoo.CANCELADO
    def realizar(self):
        self.status=StatusVoo.REALIZADO
