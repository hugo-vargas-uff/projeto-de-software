"""
Teste de contrato do AeronaveRepository.

O mesmo cenario roda contra o repositorio falso e contra o SQLAlchemy. Se os
dois forem substituiveis (Liskov), todos os testes passam nos dois. Se um
passar e o outro falhar, o contrato esta sendo quebrado por uma das
implementacoes.
"""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyAeronaveRepository
from airline.domain.model import Aeronave, StatusOrdemManutencao
from unit.service_layer.test_aeronave_service import FakeAeronaveRepository

HOJE = date(2026, 11, 2)


@pytest.fixture(params=["fake", "sqlalchemy"])
def repositorio(request):
    # cada teste abaixo roda duas vezes: uma com cada implementacao
    if request.param == "fake":
        yield FakeAeronaveRepository()
        return

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)()
    yield SqlAlchemyAeronaveRepository(sessao)
    sessao.close()


def nova_aeronave():
    return Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31),
    )


def test_salvar_e_buscar_devolve_a_aeronave(repositorio):
    repositorio.salvar(nova_aeronave())

    encontrada = repositorio.buscar("PT-MVA")

    assert encontrada.prefixo == "PT-MVA"
    assert encontrada.esta_disponivel(HOJE) is True


def test_buscar_prefixo_inexistente_devolve_none(repositorio):
    assert repositorio.buscar("NAO-EXISTE") is None


def test_salvar_aeronave_ja_existente_atualiza_em_vez_de_duplicar(repositorio):
    aeronave = nova_aeronave()
    repositorio.salvar(aeronave)

    aeronave.abrir_ordem_manutencao("Revisao do motor")
    repositorio.salvar(aeronave)

    encontrada = repositorio.buscar("PT-MVA")

    assert len(encontrada.ordens_manutencao) == 1
    assert encontrada.esta_disponivel(HOJE) is False


def test_concluir_ordem_e_salvar_libera_a_aeronave(repositorio):
    aeronave = nova_aeronave()
    ordem = aeronave.abrir_ordem_manutencao("Revisao do motor")
    repositorio.salvar(aeronave)

    aeronave.concluir_ordem_manutencao(ordem)
    repositorio.salvar(aeronave)

    encontrada = repositorio.buscar("PT-MVA")

    assert encontrada.ordens_manutencao[0].status == StatusOrdemManutencao.CONCLUIDA
    assert encontrada.esta_disponivel(HOJE) is True
