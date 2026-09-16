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