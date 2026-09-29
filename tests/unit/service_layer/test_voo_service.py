from datetime import date
import pytest
from airline.domain.model import Voo, Trecho, Aeronave, StatusVoo, ErroRegraVoo
from airline.domain.repositories import VooRepository
from airline.domain.exception import (
    VooJaExiste,
    VooNaoEncontrado,
    AeronaveNaoEncontrada,
    AeronaveIndisponivel,
)
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
    #disponivel na data de hj
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

#testes
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

def test_agendar_voo_com_numero_repetido_da_erro():
    servico, voos, aeronaves, session = montar_servico()
    aeronaves.salvar(nova_aeronave())
    voos.salvar(novo_voo("MV-100"))

    with pytest.raises(VooJaExiste):
        servico.agendar_voo("MV-100", "GRU", "GIG", "PR-400", HOJE)

    assert session.committed is False  #deu erro, entao nada pode ser confirmado

def test_agendar_voo_com_aeronave_inexistente_da_erro():
    servico, voos, aeronaves, session = montar_servico()

    with pytest.raises(AeronaveNaoEncontrada):
        servico.agendar_voo("MV-100", "GRU", "GIG", "PR-999", HOJE)

    assert voos.buscar("MV-100") is None
    assert session.committed is False

def test_agendar_voo_com_aeronave_em_manutencao_da_erro():
    servico, voos, aeronaves, session = montar_servico()
    aeronave = nova_aeronave()
    aeronave.abrir_ordem_manutencao("Troca de pneus")  #manutencao aberta = indisponivel
    aeronaves.salvar(aeronave)

    with pytest.raises(AeronaveIndisponivel):
        servico.agendar_voo("MV-100", "GRU", "GIG", "PR-400", HOJE)

    assert voos.buscar("MV-100") is None
    assert session.committed is False


# cancelar voo

def test_cancelar_voo_muda_o_status_e_confirma():
    servico, voos, aeronaves, session = montar_servico()
    voos.salvar(novo_voo("MV-100"))

    servico.cancelar_voo("MV-100")

    assert voos.buscar("MV-100").status == StatusVoo.CANCELADO
    assert session.committed is True

def test_cancelar_voo_inexistente_da_erro():
    servico, voos, aeronaves, session = montar_servico()

    with pytest.raises(VooNaoEncontrado):
        servico.cancelar_voo("NAO-EXISTE")

    assert session.committed is False


