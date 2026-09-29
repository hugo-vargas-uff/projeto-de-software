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
