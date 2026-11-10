import uuid

from sqlalchemy import Column, String, Enum, Integer, Date, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from airline.domain.model import Reserva, Passageiro, StatusReserva, StatusOrdemManutencao, Tripulante, CargoTripulante, \
    Escala, CPF, Aeronave, OrdemManutencao

Base = declarative_base()

class ReservaModel(Base):
    __tablename__ = "reservas"

    voo_id = Column(String, primary_key=True)
    passageiro_id = Column(String, primary_key=True)
    status = Column(Enum(StatusReserva), nullable=False)

    @classmethod
    def from_domain(cls, reserva: Reserva):
        return cls(
            voo_id=str(reserva.voo_id),
            passageiro_id=str(reserva.passageiro_id),
            status=reserva.status
        )

    def to_domain(self):
        return Reserva.restaurar(
            voo_id=self.voo_id,
            passageiro_id=self.passageiro_id,
            status=self.status
        )


class PassageiroModel(Base):
    __tablename__ = "passageiros"

    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)

    @classmethod
    def from_domain(cls, passageiro):
        return cls(
            id=str(passageiro.id),
            nome=passageiro.nome,
            cpf=passageiro.cpf.valor
        )

    def to_domain(self):
        return Passageiro.restaurar(
            id=uuid.UUID(str(self.id)),
            nome=self.nome,
            cpf=CPF(str(self.cpf))
        )

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

    @classmethod
    def from_domain(cls, aeronave: Aeronave):
        model = cls(
            prefixo=aeronave.prefixo,
            modelo=aeronave.modelo,
            capacidade=aeronave.capacidade,
            validade_vistoria=aeronave.validade_vistoria
        )
        for ordem in aeronave.ordens_manutencao:
            model.ordens_manutencao.append(OrdemManutencaoModel.from_domain(ordem))
        return model

    def to_domain(self):
        aeronave = Aeronave(
            prefixo=self.prefixo,
            modelo=self.modelo,
            capacidade=self.capacidade,
            validade_vistoria=self.validade_vistoria
        )
        # as ordens voltam pelos metodos da propria aeronave, que continua
        # sendo a unica a abrir e concluir ordens (ADR 0004)
        for ordem_model in self.ordens_manutencao:
            ordem = aeronave.abrir_ordem_manutencao(ordem_model.descricao)
            if ordem_model.status == StatusOrdemManutencao.CONCLUIDA:
                aeronave.concluir_ordem_manutencao(ordem)
        return aeronave


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

    @classmethod
    def from_domain(cls, ordem: OrdemManutencao):
        return cls(descricao=ordem.descricao, status=ordem.status)




class TripulanteModel(Base):
    __tablename__ = "tripulantes"

    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    teto_horas = Column(Float, nullable=False)
    horas_de_voo = Column(Float, nullable=False)

    @classmethod
    def from_domain(cls, tripulante: Tripulante):
        return cls(
            id=str(tripulante.id),
            nome=tripulante.nome,
            cargo=tripulante.cargo.value,
            teto_horas=tripulante.teto_horas,
            horas_de_voo=tripulante.horas_de_voo
        )

    def to_domain(self):
        return Tripulante.restaurar(
            id=uuid.UUID(str(self.id)),
            nome=self.nome,
            cargo=CargoTripulante(self.cargo),
            teto_horas=self.teto_horas,
            horas_de_voo=self.horas_de_voo
        )


class EscalaTripulanteModel(Base):
    __tablename__ = "escala_tripulantes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    escala_id = Column(String, ForeignKey("escalas.id"), nullable=False)
    tripulante_id = Column(String, nullable=False)

    escala = relationship("EscalaModel", back_populates="tripulantes")


class EscalaModel(Base):
    __tablename__ = "escalas"

    id = Column(String, primary_key=True)
    voo_id = Column(String, nullable=False)

    tripulantes = relationship(
        "EscalaTripulanteModel",
        back_populates="escala",
        cascade="all, delete-orphan"
    )

    @classmethod
    def from_domain(cls, escala: Escala):
        model = cls(id=str(escala.id), voo_id=str(escala.voo_id))
        for t_id in escala.tripulantes_ids:
            model.tripulantes.append(EscalaTripulanteModel(tripulante_id=str(t_id)))
        return model

    def to_domain(self):
        tripulantes_ids = [uuid.UUID(t.tripulante_id) for t in self.tripulantes]
        return Escala.restaurar(
            id=uuid.UUID(str(self.id)),
            voo_id=self.voo_id,
            tripulantes_ids=tripulantes_ids
        )


# --- Despacho

from airline.domain.model import Despacho, Volume, Conteiner


class VolumeDespachoModel(Base):
    # guarda a arvore do Composite numa tabela so: cada linha aponta para o conteiner pai
    __tablename__ = "despacho_volumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    despacho_id = Column(String, ForeignKey("despachos.id"), nullable=False)
    tipo = Column(String(10), nullable=False, default="VOLUME", server_default="VOLUME")
    codigo = Column(String(20), nullable=True)
    peso = Column(Float, nullable=False)  # no conteiner, guarda a tara
    pai_id = Column(Integer, ForeignKey("despacho_volumes.id"), nullable=True)

    despacho = relationship("DespachoModel", back_populates="volumes")
    pai = relationship("VolumeDespachoModel", remote_side=[id])


def itens_para_models(itens, pai=None):
    models = []
    for item in itens:
        if isinstance(item, Conteiner):
            model = VolumeDespachoModel(tipo="CONTEINER", codigo=item.codigo, peso=item.tara, pai=pai)
            models.append(model)
            models.extend(itens_para_models(item.itens, pai=model))
        else:
            models.append(VolumeDespachoModel(tipo="VOLUME", peso=item.peso, pai=pai))
    return models


def models_para_itens(linhas, pai_id=None):
    itens = []
    for linha in linhas:
        if linha.pai_id != pai_id:
            continue
        if linha.tipo == "CONTEINER":
            itens.append(Conteiner(
                codigo=linha.codigo,
                tara=linha.peso,
                itens=models_para_itens(linhas, pai_id=linha.id)
            ))
        else:
            itens.append(Volume(peso=linha.peso))
    return itens


class DespachoModel(Base):
    __tablename__ = "despachos"

    id = Column(String, primary_key=True)
    voo_id = Column(String, nullable=False)
    carga_maxima = Column(Float, nullable=False)

    volumes = relationship(
        "VolumeDespachoModel",
        back_populates="despacho",
        cascade="all, delete-orphan",
        order_by="VolumeDespachoModel.id"
    )

    @classmethod
    def from_domain(cls, despacho: Despacho):
        model = cls(
            id=str(despacho.id),
            voo_id=despacho.voo_id,
            carga_maxima=despacho.carga_maxima
        )
        model.volumes.extend(itens_para_models(despacho.volumes))
        return model

    def to_domain(self):
        return Despacho.restaurar(
            id=uuid.UUID(str(self.id)),
            voo_id=self.voo_id,
            carga_maxima=self.carga_maxima,
            volumes=models_para_itens(self.volumes)
        )
