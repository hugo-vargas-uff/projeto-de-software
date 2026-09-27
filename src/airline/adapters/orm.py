from sqlalchemy import Column, String, Enum, Integer, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from airline.domain.model import StatusReserva, StatusOrdemManutencao

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





#---Aeronave


class AeronaveModel(Base):
    __tablename__ = "aeronaves"

    prefixo = Column(String(20), primary_key=True)
    modelo = Column(String(100), nullable=False)
    capacidade = Column(Integer, nullable=False)
    validade_vistoria = Column(Date, nullable=False)

    ordens_manutencao = relationship(
        "OrdemManutencaoModel",
        back_populates="aeronave",
        cascade="all, delete-orphan"
    )


class OrdemManutencaoModel(Base):
    __tablename__ = "ordens_manutencao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aeronave_prefixo = Column(
        String(20),
        ForeignKey("aeronaves.prefixo"),
        nullable=False
    )
    descricao = Column(String(255), nullable=False)
    status = Column(Enum(StatusOrdemManutencao), nullable=False)

    aeronave = relationship(
        "AeronaveModel",
        back_populates="ordens_manutencao"
    )

