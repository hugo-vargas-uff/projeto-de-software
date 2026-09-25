from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyPassageiroRepository
from airline.domain.model import Passageiro
from airline.adapters.orm import PassageiroModel

def test_deve_salvar_reserva():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyPassageiroRepository(session)

    passageiro = Passageiro(nome="joão", cpf="717.774.400-25")

    repository.salvar(passageiro)

    passageiro_model = session.query(PassageiroModel).first()

    assert passageiro_model is not None
    assert passageiro_model.id == str(passageiro.id)
    assert passageiro_model.nome == "joão"
    assert passageiro_model.cpf == "717.774.400-25"