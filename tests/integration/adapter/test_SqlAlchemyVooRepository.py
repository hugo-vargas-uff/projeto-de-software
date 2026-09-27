import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from airline.domain.model import Voo, Trecho
from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyVooRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    sessao = Session()
    yield sessao
    sessao.close()


def test_salvar_voo_no_banco(session):
    voo = Voo(
        numero_voo="MV-100",
        trecho=Trecho("GRU", "GIG"),
        aeronave_id="PR-325",
        capacidade_assentos=180,
    )

    repo = SqlAlchemyVooRepository(session)
    repo.salvar(voo)
    session.commit()

    #checa direto no banco pra ter certeza que gravou
    query = text("""
        SELECT numero_voo, origem, destino 
        FROM voos 
        WHERE numero_voo = 'MV-100'
    """)
    linha = session.execute(query).fetchone()

    assert linha is not None
    assert linha[0] == "MV-100"
    assert linha[1] == "GRU"
    assert linha[2] == "GIG"


def test_buscar_voo_do_banco(session):
    #insere no banco a mao para testar se o metodo acha certinho
    query = text("""
        INSERT INTO voos (numero_voo, origem, destino, aeronave_id, assentos_disponiveis, status)
        VALUES ('MV-200', 'CNF', 'SSA', 'PR-355', 200, 'AGENDADO')
    """)
    session.execute(query)
    session.commit()

    repo = SqlAlchemyVooRepository(session)
    voo = repo.buscar("MV-200")

    assert voo is not None
    assert voo.numero_voo == "MV-200"
    assert voo.trecho.origem == "CNF"
    assert voo.trecho.destino == "SSA"
    assert voo.aeronave_id == "PR-355"
    assert voo.assentos_disponiveis == 200


def test_buscar_voo_inexistente(session):
    repo = SqlAlchemyVooRepository(session)
    resultado = repo.buscar("NAO-EXISTE")
    
    assert resultado is None


def test_salvar_voo_existente_atualiza_status(session):
    repo = SqlAlchemyVooRepository(session)
    repo.salvar(Voo( numero_voo="MV-300",trecho=Trecho("GRU", "POA"),
    aeronave_id="PR-400", capacidade_assentos=150,))
    session.commit()

    #busca,muda pelo metodo do dominio e salva de novo
    voo = repo.buscar("MV-300")
    voo.cancelar()
    repo.salvar(voo)
    session.commit()

    #confere direto no banco se foi atualizado, e nao duplicado
    query = text("""
    SELECT status 
    FROM voos WHERE numero_voo = 'MV-300'
    """)
    linhas = session.execute(query).fetchall()

    assert len(linhas) == 1
    assert linhas[0][0] == "CANCELADO"

