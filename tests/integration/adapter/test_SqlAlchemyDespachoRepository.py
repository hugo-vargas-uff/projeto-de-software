import uuid
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from airline.domain.model import Despacho, Volume
from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyDespachoRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    sessao = Session()

    yield sessao

    sessao.close()


def test_salvar_despacho_no_banco(session):
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Volume(peso=100))
    despacho.adicionar_volume(Volume(peso=250))

    repo = SqlAlchemyDespachoRepository(session)
    repo.salvar(despacho)

    query_despacho = text("""
        SELECT id, voo_id, carga_maxima
        FROM despachos
    """)

    linha = session.execute(query_despacho).fetchone()

    assert linha is not None
    assert linha[0] == str(despacho.id)
    assert linha[1] == "MV-3000"
    assert linha[2] == 1000

    query_volumes = text("""
        SELECT peso
        FROM despacho_volumes
        WHERE despacho_id = :despacho_id
    """)

    volumes = session.execute(query_volumes, {"despacho_id": str(despacho.id)}).fetchall()

    assert sorted(volume[0] for volume in volumes) == [100, 250]


def test_salvar_despacho_existente_atualiza_volumes(session):
    repo = SqlAlchemyDespachoRepository(session)

    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Volume(peso=100))
    repo.salvar(despacho)

    despacho = repo.buscar_por_id(despacho.id)
    despacho.adicionar_volume(Volume(peso=300))
    repo.salvar(despacho)

    despachos = session.execute(text("SELECT id FROM despachos")).fetchall()
    assert len(despachos) == 1

    volumes = session.execute(text("SELECT peso FROM despacho_volumes")).fetchall()
    assert sorted(volume[0] for volume in volumes) == [100, 300]


def test_buscar_despacho_por_id_do_banco(session):
    despacho_id = uuid.uuid4()

    session.execute(text("""
        INSERT INTO despachos (id, voo_id, carga_maxima)
        VALUES (:id, 'MV-4000', 500)
    """), {"id": str(despacho_id)})

    session.execute(text("""
        INSERT INTO despacho_volumes (despacho_id, peso)
        VALUES (:id, 120), (:id, 80)
    """), {"id": str(despacho_id)})

    session.commit()

    repo = SqlAlchemyDespachoRepository(session)

    despacho = repo.buscar_por_id(despacho_id)

    assert despacho is not None
    assert despacho.id == despacho_id
    assert despacho.voo_id == "MV-4000"
    assert despacho.carga_maxima == 500
    assert despacho.peso_total() == 200
    assert despacho.peso_disponivel() == 300


def test_buscar_despacho_por_voo_do_banco(session):
    despacho_id = uuid.uuid4()

    session.execute(text("""
        INSERT INTO despachos (id, voo_id, carga_maxima)
        VALUES (:id, 'MV-5000', 800)
    """), {"id": str(despacho_id)})

    session.execute(text("""
        INSERT INTO despacho_volumes (despacho_id, peso)
        VALUES (:id, 400)
    """), {"id": str(despacho_id)})

    session.commit()

    repo = SqlAlchemyDespachoRepository(session)

    despacho = repo.buscar_por_voo("MV-5000")

    assert despacho is not None
    assert despacho.id == despacho_id
    assert despacho.volumes == [Volume(peso=400)]


def test_buscar_despacho_inexistente(session):
    repo = SqlAlchemyDespachoRepository(session)

    assert repo.buscar_por_id(uuid.uuid4()) is None
    assert repo.buscar_por_voo("NAO-EXISTE") is None


# ---- Composite: o conteiner e gravado como linha pai dos seus volumes

from airline.domain.model import Conteiner


def test_salvar_despacho_com_conteiner_grava_a_arvore(session):
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Volume(peso=100))
    despacho.adicionar_volume(
        Conteiner(codigo="AKE12345AA", tara=80, itens=[Volume(peso=23), Volume(peso=32)])
    )

    SqlAlchemyDespachoRepository(session).salvar(despacho)

    linhas = session.execute(text("""
        SELECT v.tipo, v.codigo, v.peso, pai.codigo
        FROM despacho_volumes v
        LEFT JOIN despacho_volumes pai ON pai.id = v.pai_id
        ORDER BY v.id
    """)).fetchall()

    assert [tuple(linha) for linha in linhas] == [
        ("VOLUME", None, 100, None),
        ("CONTEINER", "AKE12345AA", 80, None),
        ("VOLUME", None, 23, "AKE12345AA"),
        ("VOLUME", None, 32, "AKE12345AA"),
    ]


def test_buscar_despacho_reconstroi_conteiner_aninhado(session):
    despacho_id = uuid.uuid4()

    session.execute(text("""
        INSERT INTO despachos (id, voo_id, carga_maxima)
        VALUES (:id, 'MV-6000', 2000)
    """), {"id": str(despacho_id)})

    session.execute(text("""
        INSERT INTO despacho_volumes (id, despacho_id, tipo, codigo, peso, pai_id) VALUES
            (1, :id, 'CONTEINER', 'PMC00001AA', 120, NULL),
            (2, :id, 'CONTEINER', 'AKE00001AA', 80, 1),
            (3, :id, 'VOLUME', NULL, 20, 2),
            (4, :id, 'VOLUME', NULL, 40, 1),
            (5, :id, 'VOLUME', NULL, 15, NULL)
    """), {"id": str(despacho_id)})

    session.commit()

    despacho = SqlAlchemyDespachoRepository(session).buscar_por_id(despacho_id)

    assert despacho.volumes == [
        Conteiner(
            codigo="PMC00001AA",
            tara=120,
            itens=[Conteiner(codigo="AKE00001AA", tara=80, itens=[Volume(peso=20)]), Volume(peso=40)]
        ),
        Volume(peso=15),
    ]
    assert despacho.peso_total() == 120 + 80 + 20 + 40 + 15
    assert despacho.quantidade_volumes() == 3


def test_salvar_de_novo_despacho_com_conteiner_nao_duplica_linhas(session):
    repo = SqlAlchemyDespachoRepository(session)

    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Conteiner(codigo="AKE12345AA", tara=80, itens=[Volume(peso=20)]))
    repo.salvar(despacho)

    despacho = repo.buscar_por_id(despacho.id)
    despacho.adicionar_volume(Volume(peso=50))
    repo.salvar(despacho)

    total = session.execute(text("SELECT COUNT(*) FROM despacho_volumes")).scalar()
    assert total == 3
    assert repo.buscar_por_id(despacho.id).peso_total() == 150
