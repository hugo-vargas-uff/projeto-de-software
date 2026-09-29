from datetime import date

from airline.domain.model import Voo, Trecho, Aeronave, StatusVoo
from airline.domain.repositories import VooRepository
from airline.service_layer.services import VooService
from test_aeronave_service import FakeAeronaveRepository

class FakeVooRepository(VooRepository):
    
    def __init__(self):
        self._voos = {}

    def salvar(self, voo: Voo) -> None:
        self._voos[voo.numero_voo] = voo

    def buscar(self, numero_voo: str):
        return self._voos.get(numero_voo)

class FakeSession:
    committed = False
    def commit(self):
        self.committed = True


HOJE = date(2026, 9, 28) #data fixa

def nova_aeronave(prefixo="PR-400", capacidade=150):
    #disponivel na data hj
    return Aeronave( prefixo=prefixo, modelo="Airbus A320", capacidade=capacidade, validade_vistoria=date(2027, 1, 1),
    )

def novo_voo(numero_voo="MV-100"):
    return Voo(numero_voo=numero_voo, trecho=Trecho("GRU", "GIG"), aeronave_id="PR-400", capacidade_assentos=150,
    )

def montar_servico():
    voos = FakeVooRepository()
    aeronaves = FakeAeronaveRepository()
    session = FakeSession()
    servico = VooService(voos, aeronaves, session)
    return servico, voos, aeronaves, session


def test_agendar_voo_copia_a_capacidade_da_aeronave():
    servico, voos, aeronaves, session = montar_servico()
    aeronaves.salvar(nova_aeronave(capacidade=150))

    servico.agendar_voo("MV-100", "GRU", "GIG", "PR-400", HOJE)

    voo = voos.buscar("MV-100")
    assert voo is not None
    assert voo.trecho == Trecho("GRU", "GIG")
    assert voo.assentos_disponiveis == 150  #veio da aeronave
    assert voo.status == StatusVoo.AGENDADO
    assert session.committed is True