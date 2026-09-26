from sqlalchemy import Column, String, Enum, Integer
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


class VooModel(Base):
    __tablename__ = "voos"

    numero_voo = Column(String(20), primary_key=True)
    origem = Column(String(3), nullable=False)
    destino = Column(String(3),nullable=False)
    aeronave_id = Column(String(20), nullable=False)
    assentos_disponiveis = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)

