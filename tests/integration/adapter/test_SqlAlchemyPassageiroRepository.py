from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyPassageiroRepository
from airline.domain.model import Passageiro, CPF
from airline.adapters.orm import PassageiroModel

def test_deve_salvar_passageiro():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyPassageiroRepository(session)

    passageiro = Passageiro(nome="joão", cpf=CPF("717.774.400-25"))

    repository.salvar(passageiro)

    passageiro_salvo = session.query(PassageiroModel).first()

    assert passageiro_salvo is not None
    assert passageiro_salvo.id == str(passageiro.id)
    assert passageiro_salvo.nome == "joão"
    assert passageiro_salvo.cpf == "71777440025"

def test_deve_buscar_passageiro_por_id():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyPassageiroRepository(session)

    passageiro = Passageiro(nome="joão", cpf=CPF("717.774.400-25"))

    session.add(PassageiroModel.from_domain(passageiro))
    session.commit()

    passageiro_salvo = repository.buscar_por_id(passageiro.id)

    assert passageiro_salvo is not None
    assert passageiro_salvo.id == passageiro.id
    assert passageiro_salvo.nome == "joão"
    assert passageiro_salvo.cpf.valor == "71777440025"

def test_deve_buscar_passageiro_por_cpf():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    repository = SqlAlchemyPassageiroRepository(session)

    passageiro = Passageiro(nome="joão", cpf=CPF("717.774.400-25"))

    session.add(PassageiroModel.from_domain(passageiro))
    session.commit()

    passageiro_salvo = repository.buscar_por_cpf(passageiro.cpf.valor)

    assert passageiro_salvo is not None
    assert passageiro_salvo.id == passageiro.id
    assert passageiro_salvo.nome == "joão"
    assert passageiro_salvo.cpf.valor == "71777440025"