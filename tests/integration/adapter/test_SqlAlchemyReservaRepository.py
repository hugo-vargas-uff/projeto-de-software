from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyReservaRepository
from airline.domain.model import Reserva, StatusReserva
from airline.adapters.orm import ReservaModel

def test_deve_salvar_reserva():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyReservaRepository(session)

    reserva = Reserva(voo_id="voo-123", passageiro_id="passageiro-123")

    repository.salvar(reserva)

    reserva_model = session.query(ReservaModel).first()

    assert reserva_model is not None
    assert reserva_model.id == str(reserva.id)
    assert reserva_model.voo_id == "voo-123"
    assert reserva_model.passageiro_id == "passageiro-123"
    assert reserva_model.status == StatusReserva.CONFIRMADA