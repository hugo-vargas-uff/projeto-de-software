import pytest

from datetime import date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from airline.domain.model import (
    Aeronave,
    StatusOrdemManutencao
)

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyAeronaveRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    sessao = Session()

    yield sessao

    sessao.close()


def test_salvar_aeronave_no_banco(session):
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    ordem_pendente = aeronave.abrir_ordem_manutencao(
        "Revisao do motor"
    )

    ordem_concluida = aeronave.abrir_ordem_manutencao(
        "Troca de oleo"
    )

    aeronave.concluir_ordem_manutencao(ordem_concluida)

    repo = SqlAlchemyAeronaveRepository(session)
    repo.salvar(aeronave)

    query_aeronave = text("""
        SELECT prefixo, modelo, capacidade, validade_vistoria
        FROM aeronaves
        WHERE prefixo = 'PT-MVA'
    """)

    linha = session.execute(query_aeronave).fetchone()

    assert linha is not None
    assert linha[0] == "PT-MVA"
    assert linha[1] == "Boeing 737"
    assert linha[2] == 180
    assert str(linha[3]) == "2026-12-31"

    query_ordens = text("""
        SELECT descricao, status
        FROM ordens_manutencao
        WHERE aeronave_prefixo = 'PT-MVA'
    """)

    ordens = session.execute(query_ordens).fetchall()

    assert len(ordens) == 2

    status_por_descricao = {
        ordem[0]: ordem[1]
        for ordem in ordens
    }

    assert status_por_descricao["Revisao do motor"] == "PENDENTE"
    assert status_por_descricao["Troca de oleo"] == "CONCLUIDA"


def test_buscar_aeronave_do_banco(session):
    query_aeronave = text("""
        INSERT INTO aeronaves
            (prefixo, modelo, capacidade, validade_vistoria)
        VALUES
            ('PT-MVB', 'Airbus A320', 186, '2026-12-31')
    """)

    session.execute(query_aeronave)

    query_ordem = text("""
        INSERT INTO ordens_manutencao
            (aeronave_prefixo, descricao, status)
        VALUES
            ('PT-MVB', 'Inspecao dos freios', 'PENDENTE')
    """)

    session.execute(query_ordem)
    session.commit()

    repo = SqlAlchemyAeronaveRepository(session)

    aeronave = repo.buscar("PT-MVB")

    assert aeronave is not None
    assert aeronave.prefixo == "PT-MVB"
    assert aeronave.modelo == "Airbus A320"
    assert aeronave.capacidade == 186
    assert aeronave.validade_vistoria == date(2026, 12, 31)

    assert len(aeronave.ordens_manutencao) == 1
    assert aeronave.ordens_manutencao[0].descricao == "Inspecao dos freios"
    assert aeronave.ordens_manutencao[0].status == StatusOrdemManutencao.PENDENTE

    assert aeronave.esta_disponivel(date(2026, 9, 27)) is False


def test_buscar_aeronave_inexistente(session):
    repo = SqlAlchemyAeronaveRepository(session)

    resultado = repo.buscar("NAO-EXISTE")

    assert resultado is None