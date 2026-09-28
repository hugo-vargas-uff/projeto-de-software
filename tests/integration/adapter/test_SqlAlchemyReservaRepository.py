from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyReservaRepository
from airline.domain.model import Reserva, StatusReserva, Passageiro
from airline.adapters.orm import ReservaModel

def test_deve_salvar_reserva():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyReservaRepository(session)

    passageiro = Passageiro("pedro", "717.774.400-25")

    reserva = Reserva(voo_id="voo-123", passageiro_id=passageiro.id)

    repository.salvar(reserva)

    reserva_model = session.query(ReservaModel).first()

    assert reserva_model is not None
    assert reserva_model.voo_id == "voo-123"
    assert reserva_model.passageiro_id == passageiro.id.__str__()
    assert reserva_model.status == StatusReserva.CONFIRMADA

def test_deve_buscar_reserva():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyReservaRepository(session)

    passageiro = Passageiro(nome="pedro", cpf="717.774.400-25")

    reserva_model = ReservaModel(
        voo_id="voo-123",
        passageiro_id=str(passageiro.id),
        status=StatusReserva.CONFIRMADA
    )

    session.add(reserva_model)
    session.commit()

    reserva = repository.buscar(voo_id="voo-123", passageiro_id=passageiro.id)

    assert reserva is not None
    assert reserva.voo_id == "voo-123"
    assert reserva.passageiro_id == str(passageiro.id)
    assert reserva.status == StatusReserva.CONFIRMADA

def test_contar_reservas_por_voo():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyReservaRepository(session)

    passageiro = Passageiro(nome="pedro", cpf="717.774.400-25")
    passageiro1 = Passageiro(nome="pedro", cpf="575.568.540-19")
    passageiro2 = Passageiro(nome="pedro", cpf="282.154.860-53")
    passageiro3 = Passageiro(nome="pedro", cpf="418.268.960-74")

    reserva1 = Reserva(voo_id="voo-123", passageiro_id=passageiro.id)
    reserva2 = Reserva(voo_id="voo-123", passageiro_id=passageiro1.id)
    reserva3 = Reserva(voo_id="voo-123", passageiro_id=passageiro2.id)
    reserva4 = Reserva(voo_id="voo-123", passageiro_id=passageiro3.id)

    session.add_all([
        ReservaModel.from_domain(reserva1),
        ReservaModel.from_domain(reserva2),
        ReservaModel.from_domain(reserva3),
        ReservaModel.from_domain(reserva4)
    ])

    session.commit()

    numero_de_reservas = repository.contar_reservas_por_voo(voo_id="voo-123")

    assert numero_de_reservas == 4

def test_contar_apenas_reservas_confirmadas():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyReservaRepository(session)

    passageiro1 = Passageiro(nome="pedro", cpf="717.774.400-25")
    passageiro2 = Passageiro(nome="pedro", cpf="575.568.540-19")

    reserva1 = Reserva(voo_id="voo-123", passageiro_id=passageiro1.id)
    reserva2 = Reserva(voo_id="voo-123", passageiro_id=passageiro2.id)

    reserva2.cancelar()

    session.add_all([
        ReservaModel.from_domain(reserva1),
        ReservaModel.from_domain(reserva2)
    ])

    session.commit()

    numero_de_reservas = repository.contar_reservas_por_voo("voo-123")

    assert numero_de_reservas == 1