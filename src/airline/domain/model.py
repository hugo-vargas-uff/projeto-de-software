import uuid, re
from enum import Enum

from airline.domain.exception import TipoCpfInvalidoException, CpfInvalidoException


class StatusReserva(Enum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


class Reserva:

    def __init__(self, voo_id, passageiro_id):
        self.voo_id = voo_id
        self.passageiro_id = passageiro_id
        self.status = StatusReserva.CONFIRMADA

    def cancelar(self):
        self.status = StatusReserva.CANCELADA

    @classmethod
    def restaurar(cls, voo_id, passageiro_id, status):
        reserva = cls.__new__(cls)

        reserva.voo_id = voo_id
        reserva.passageiro_id = passageiro_id
        reserva.status = status

        return reserva

class CPF:
    def __init__(self, valor: str):
        self.valor = self.normalizar(valor)
        self.validar()

    def normalizar(self, valor: str) -> str:
        return re.sub(r"\D", "", valor)

    def validar(self):
        if len(self.valor) != 11:
            raise CpfInvalidoException("CPF deve possuir 11 dígitos.")

        if self.valor == self.valor[0] * 11:
            raise CpfInvalidoException("CPF inválido.")


class Passageiro:
    def __init__(self, nome, cpf: CPF):
        if not isinstance(cpf, CPF):
            raise TipoCpfInvalidoException("O CPF deve ser uma instância da classe CPF.")

        self.id = uuid.uuid4()
        self.nome = nome
        self.cpf = cpf

    @classmethod
    def restaurar(cls, id, nome, cpf):
        if not isinstance(cpf, CPF):
            raise TipoCpfInvalidoException("O CPF deve ser uma instância da classe CPF.")

        passageiro = cls.__new__(cls)
        passageiro.id = id
        passageiro.nome = nome
        passageiro.cpf = cpf
        return passageiro

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

# mudancas de status que cada status permite
TRANSICOES_VOO = {
    StatusVoo.AGENDADO:{StatusVoo.CANCELADO, StatusVoo.REALIZADO},
    StatusVoo.CANCELADO: set(),
    StatusVoo.REALIZADO: set(),
}

# status em que o voo ainda aceita passageiro novo
STATUS_QUE_ACEITAM_ASSENTO = {StatusVoo.AGENDADO}

class Voo:
    def __init__(self, numero_voo: str, trecho: Trecho, aeronave_id: str, capacidade_assentos: int):
        self.numero_voo = numero_voo
        self.trecho=trecho
        self.aeronave_id = aeronave_id
        self.assentos_disponiveis = capacidade_assentos
        self.status = StatusVoo.AGENDADO

    def cancelar(self):
        self.mudar_status(StatusVoo.CANCELADO)
        
    def realizar(self):
        self.mudar_status(StatusVoo.REALIZADO)

    def alocar_assento(self):
        if self.status not in STATUS_QUE_ACEITAM_ASSENTO:
            raise ErroRegraVoo(f"voo {self.status.value.lower()} nao aceita assento novo")
        if self.assentos_disponiveis <= 0:
            raise ErroRegraVoo("lotado, sem assentos livres.")
        self.assentos_disponiveis -= 1

    def mudar_status(self, novo_status):
        if novo_status not in TRANSICOES_VOO[self.status]:
            raise ErroRegraVoo(f"voo {self.status.value.lower()} nao pode passar para {novo_status.value.lower()}")
        self.status = novo_status


# Agregado Aeronave

class Aeronave:
    def __init__(
        self,
        prefixo: str,
        modelo: str,
        capacidade: int,
        validade_vistoria
    ):
        self.prefixo = prefixo
        self.modelo = modelo
        self.capacidade = capacidade
        self.validade_vistoria = validade_vistoria
        self.ordens_manutencao = []

    def __eq__(self, outra):
        if not isinstance(outra, Aeronave):
            return False

        return self.prefixo == outra.prefixo

    def __hash__(self):
        return hash(self.prefixo)

    def abrir_ordem_manutencao(self, descricao: str):
        ordem = OrdemManutencao(descricao)
        self.ordens_manutencao.append(ordem)
        return ordem

    def concluir_ordem_manutencao(self, ordem):
        ordem.concluir()

    def esta_disponivel(self, hoje):
        vistoria_valida = self.validade_vistoria >= hoje

        possui_manutencao_pendente = any(
            ordem.status == StatusOrdemManutencao.PENDENTE
            for ordem in self.ordens_manutencao
        )

        return vistoria_valida and not possui_manutencao_pendente

    
class StatusOrdemManutencao(Enum):
    PENDENTE = "PENDENTE"
    CONCLUIDA = "CONCLUIDA"


class OrdemManutencao:
    def __init__(self, descricao: str):
        self.descricao = descricao
        self.status = StatusOrdemManutencao.PENDENTE

    def concluir(self):
        self.status = StatusOrdemManutencao.CONCLUIDA




# agregado despacho
class ErroRegraDespacho(Exception):
    pass

@dataclass(frozen=True)
class Volume:
    peso: float

class Despacho:
    def __init__(self, voo_id: str, carga_maxima: float):
        self.id = uuid.uuid4()
        self.voo_id = voo_id
        self.carga_maxima = carga_maxima
        self.volumes = []

    def adicionar_volume(self, volume):
        novo_peso = self.peso_total() + volume.peso

        if novo_peso > self.carga_maxima:
            raise ErroRegraDespacho(
                "Peso total dos volumes ultrapassa a carga maxima do despacho"
            )

        self.volumes.append(volume)

    def peso_total(self):
        return sum(volume.peso for volume in self.volumes)

    def peso_disponivel(self):
        return self.carga_maxima - self.peso_total()

    def __eq__(self, outro):
        if not isinstance(outro, Despacho):
            return False
        return self.id == outro.id

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def restaurar(cls, id, voo_id, carga_maxima, volumes):
        despacho = cls.__new__(cls)
        despacho.id = id
        despacho.voo_id = voo_id
        despacho.carga_maxima = carga_maxima
        despacho.volumes = list(volumes)
        return despacho



# Agregado Tripulante

class ErroRegraTripulacao(Exception):
    pass


class CargoTripulante(Enum):
    PILOTO = "PILOTO"
    COPILOTO = "COPILOTO"
    COMISSARIO = "COMISSARIO"


class Tripulante:
    def __init__(self, nome: str, cargo: CargoTripulante, teto_horas: float = 85.0):
        self.id = uuid.uuid4()
        self.nome = nome
        self.cargo = cargo
        self.teto_horas = teto_horas
        self.horas_de_voo = 0.0

    def registrar_horas_de_voo(self, horas: float):
        if self.horas_de_voo + horas > self.teto_horas:
            raise ErroRegraTripulacao("Teto regulamentar de horas ultrapassado")
        self.horas_de_voo += horas

    def pode_voar(self, duracao_horas: float) -> bool:
        return (self.horas_de_voo + duracao_horas) <= self.teto_horas

    def __eq__(self, outro):
        if not isinstance(outro, Tripulante):
            return False
        return self.id == outro.id

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def restaurar(cls, id, nome, cargo, teto_horas, horas_de_voo):
        tripulante = cls.__new__(cls)
        tripulante.id = id
        tripulante.nome = nome
        tripulante.cargo = cargo
        tripulante.teto_horas = teto_horas
        tripulante.horas_de_voo = horas_de_voo
        return tripulante


    

# Agregado Escalas


class Escala:
    def __init__(self, voo_id: str):
        self.id = uuid.uuid4()
        self.voo_id = voo_id
        self.tripulantes_ids = []

    def adicionar_tripulante(self, tripulante_id):
        if tripulante_id in self.tripulantes_ids:
            raise ErroRegraTripulacao("Tripulante ja escalado para este voo")
        self.tripulantes_ids.append(tripulante_id)

    def remover_tripulante(self, tripulante_id):
        if tripulante_id in self.tripulantes_ids:
            self.tripulantes_ids.remove(tripulante_id)

    def total_tripulantes(self) -> int:
        return len(self.tripulantes_ids)

    def __eq__(self, outra):
        if not isinstance(outra, Escala):
            return False
        return self.id == outra.id

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def restaurar(cls, id, voo_id, tripulantes_ids):
        escala = cls.__new__(cls)
        escala.id = id
        escala.voo_id = voo_id
        escala.tripulantes_ids = list(tripulantes_ids)
        return escala

