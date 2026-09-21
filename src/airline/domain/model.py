import uuid

class Reserva:

    def __init__(self, voo_id, passageiro_id):
        self.id = uuid.uuid4()
        self.voo_id = voo_id
        self.passageiro_id = passageiro_id
        self.status = StatusReserva.CONFIRMADA

    def cancelar(self):
        self.status = StatusReserva.CANCELADA

class Passageiro:

    def __init__(self, nome, cpf):
        self.id = uuid.uuid4()
        self.nome = nome
        self.cpf = cpf

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




# agregado despacho
class ErroRegraDespacho(Exception):
    pass

@dataclass(frozen=True)
class Volume:
    peso: float

class Despacho:
    def __init__(self, carga_maxima: float):
        self.carga_maxima = carga_maxima
        self.volumes = []

    def adicionar_volume(self, volume):
        novo_peso = self.peso_total() + volume.peso

        if novo_peso > self.carga_maxima:
            raise ErroRegraDespacho(
                "Peso total dos volumes ultrapassa a carga maxima da aeronave"
            )

        self.volumes.append(volume)

    def peso_total(self):
        return sum(volume.peso for volume in self.volumes)