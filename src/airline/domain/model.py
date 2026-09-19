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

class StatusVoo(Enum):
    AGENDADO = "AGENDADO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"

class Voo:

    def __init__(self, numero_voo: str):
        self.numero_voo = numero_voo
        self.status = StatusVoo.AGENDADO