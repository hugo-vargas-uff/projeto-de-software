from datetime import date
from airline.domain.model import Aeronave, StatusOrdemManutencao
from airline.domain.repositories import AeronaveRepository
from airline.service_layer.services import AeronaveService

import pytest

from airline.domain.exception import AeronaveJaExiste



class FakeAeronaveRepository(AeronaveRepository):

    def __init__(self):
        self.aeronaves = {}

    def salvar(self, aeronave):
        self.aeronaves[aeronave.prefixo] = aeronave

    def buscar(self, prefixo):
        return self.aeronaves.get(prefixo)


#----testes

def test_salvar_e_buscar_aeronave_por_prefixo():
    repositorio = FakeAeronaveRepository()

    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    repositorio.salvar(aeronave)

    encontrada = repositorio.buscar("PT-MVA")

    assert encontrada == aeronave

def test_buscar_aeronave_inexistente_retorna_none():
    repositorio = FakeAeronaveRepository()

    encontrada = repositorio.buscar("PT-XXX")

    assert encontrada is None





def test_cadastrar_aeronave():
    repo = FakeAeronaveRepository()
    service = AeronaveService(repo)

    aeronave = service.cadastrar_aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    encontrada = repo.buscar("PT-MVA")

    assert encontrada == aeronave
    assert encontrada.modelo == "Boeing 737"


def test_abrir_ordem_manutencao():
    repo = FakeAeronaveRepository()
    service = AeronaveService(repo)

    service.cadastrar_aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    ordem = service.abrir_ordem_manutencao(
        "PT-MVA",
        "Troca de oleo"
    )

    assert ordem.status == StatusOrdemManutencao.PENDENTE

    aeronave = repo.buscar("PT-MVA")
    assert len(aeronave.ordens_manutencao) == 1


def test_concluir_ordem_manutencao():
    repo = FakeAeronaveRepository()
    service = AeronaveService(repo)

    service.cadastrar_aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    service.abrir_ordem_manutencao(
        "PT-MVA",
        "Troca de oleo"
    )

    ordem = service.concluir_ordem_manutencao(
        "PT-MVA",
        "Troca de oleo"
    )

    assert ordem.status == StatusOrdemManutencao.CONCLUIDA


def test_consultar_disponibilidade():
    repo = FakeAeronaveRepository()
    service = AeronaveService(repo)

    service.cadastrar_aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    disponivel = service.consultar_disponibilidade(
        "PT-MVA",
        date(2026, 9, 28)
    )

    assert disponivel is True

def test_nao_deve_cadastrar_aeronave_com_prefixo_repetido():
    repo = FakeAeronaveRepository()
    service = AeronaveService(repo)

    service.cadastrar_aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    with pytest.raises(AeronaveJaExiste):
        service.cadastrar_aeronave(
            prefixo="PT-MVA",
            modelo="Airbus A320",
            capacidade=186,
            validade_vistoria=date(2027, 12, 31)
        )