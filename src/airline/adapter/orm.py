from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import declarative_base
from airline.domain.model import StatusReserva

Base = declarative_base()

class ReservaModel(Base):
    __tablename__ = "reservas"

    id = Column(String, primary_key=True)
    voo_id = Column(String, nullable=False)
    passageiro_id = Column(String, nullable=False)
    status = Column(Enum(StatusReserva), nullable=False)


class PassageiroModel(Base):
    __tablename__ = "passageiros"

    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False)