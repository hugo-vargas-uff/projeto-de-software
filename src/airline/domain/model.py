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

class ErroRegraVoo(Exception):
    pass

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
        if self.status == StatusVoo.REALIZADO:
            raise ErroRegraVoo("voo realizado, nao pode ser cancelado")
        if self.status == StatusVoo.CANCELADO:
            raise ErroRegraVoo("Voo ja estava cancelado")
        
        self.status = StatusVoo.CANCELADO
        
    def realizar(self):
        if self.status != StatusVoo.AGENDADO:
            raise ErroRegraVoo("So pode realizar voos que estao agendados")
        self.status=StatusVoo.REALIZADO




# Agregado Aeronave

class Aeronave:
    def __init__(self, prefixo: str, modelo: str, capacidade: int):
        self.prefixo = prefixo
        self.modelo = modelo
        self.capacidade = capacidade
        self.disponivel = True

    def __eq__(self, outra):
        if not isinstance(outra, Aeronave):
            return False

        return self.prefixo == outra.prefixo
