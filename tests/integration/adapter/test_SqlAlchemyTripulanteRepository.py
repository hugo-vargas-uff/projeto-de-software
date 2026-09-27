import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base, TripulanteModel, EscalaModel
from airline.adapters.repository import SqlAlchemyTripulanteRepository, SqlAlchemyEscalaRepository
from airline.domain.model import Tripulante, CargoTripulante, Escala


def test_deve_salvar_tripulante_no_banco():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    repo = SqlAlchemyTripulanteRepository(session)
    tripulante = Tripulante(
        nome="Lucas Andrade",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )

    repo.salvar(tripulante)

    salvo = session.query(TripulanteModel).first()
    assert salvo is not None
    assert salvo.id == str(tripulante.id)
    assert salvo.nome == "Lucas Andrade"
    assert salvo.cargo == "PILOTO"
    assert salvo.teto_horas == 85.0


def test_deve_buscar_tripulante_por_id_do_banco():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    repo = SqlAlchemyTripulanteRepository(session)
    tripulante = Tripulante(
        nome="Ana Paula",
        cargo=CargoTripulante.COMISSARIO,
        teto_horas=75.0
    )

    session.add(TripulanteModel.from_domain(tripulante))
    session.commit()

    recuperado = repo.buscar_por_id(tripulante.id)
    assert recuperado is not None
    assert recuperado.id == tripulante.id
    assert recuperado.nome == "Ana Paula"
    assert recuperado.cargo == CargoTripulante.COMISSARIO


def test_deve_salvar_e_buscar_escala_no_banco():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    repo = SqlAlchemyEscalaRepository(session)
    escala = Escala(voo_id="MV-999")
    id_tripulante = uuid.uuid4()
    escala.adicionar_tripulante(id_tripulante)

    repo.salvar(escala)

    recuperada = repo.buscar_por_voo("MV-999")
    assert recuperada is not None
    assert recuperada.voo_id == "MV-999"
    assert id_tripulante in recuperada.tripulantes_ids