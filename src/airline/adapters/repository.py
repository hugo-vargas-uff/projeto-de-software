from airline.domain.model import Reserva, Passageiro, Voo, Aeronave, Trecho, StatusVoo, StatusOrdemManutencao, StatusReserva, Tripulante, CargoTripulante, Escala
from airline.domain.repositories import VooRepository, TripulanteRepository, EscalaRepository 

from airline.adapters.orm import ReservaModel, PassageiroModel, VooModel, AeronaveModel, OrdemManutencaoModel, TripulanteModel, EscalaModel, EscalaTripulanteModel
import uuid
from airline.domain.repositories import AeronaveRepository, ReservaRepository, PassageiroRepository

class SqlAlchemyReservaRepository(ReservaRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, reserva: Reserva) -> None:
        reserva_model = self.session.query(ReservaModel).filter_by(
            voo_id=str(reserva.voo_id), passageiro_id=str(reserva.passageiro_id)
        ).first()
        if reserva_model is None:
            self.session.add(ReservaModel.from_domain(reserva))
        else:
            # a reserva ja existe, entao so o status pode ter mudado
            reserva_model.status = reserva.status
        self.session.commit()

    def buscar(self, voo_id, passageiro_id):
        reserva_model = self.session.query(ReservaModel).filter_by(
            voo_id=str(voo_id),passageiro_id=str(passageiro_id)
        ).first()

        if reserva_model is None:
            return None

        return reserva_model.to_domain()

    def contar_reservas_por_voo(self, voo_id):
        return self.session.query(ReservaModel).filter_by(
            voo_id=str(voo_id),status=StatusReserva.CONFIRMADA
        ).count()

    def listar_por_voo(self, voo_id):
        reserva_models = self.session.query(ReservaModel).filter_by(voo_id=str(voo_id)).all()
        return [reserva_model.to_domain() for reserva_model in reserva_models]



class SqlAlchemyPassageiroRepository(PassageiroRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, passageiro: Passageiro) -> None:
        passageiro_model = PassageiroModel.from_domain(passageiro)

        self.session.add(passageiro_model)
        self.session.commit()

    def buscar_por_id(self, passageiro_id):
        passageiro_model = self.session.query(PassageiroModel).filter_by(
            id=str(passageiro_id)
        ).first()
        
        if passageiro_model is None:
            return None

        return passageiro_model.to_domain()

    def buscar_por_cpf(self, cpf):
        passageiro_model = (
            self.session.query(PassageiroModel)
            .filter_by(cpf=cpf)
            .first()
        )

        if passageiro_model is None:
            return None

        return passageiro_model.to_domain()



class SqlAlchemyVooRepository(VooRepository):
    
    def __init__(self, session):
        self.session = session

    def salvar(self, voo: Voo) -> None:
        voo_model = self.session.query(VooModel).filter_by(numero_voo=voo.numero_voo).first()

        if voo_model is None:
            voo_model = VooModel(numero_voo=voo.numero_voo)
            self.session.add(voo_model)

        voo_model.origem = voo.trecho.origem
        voo_model.destino = voo.trecho.destino
        voo_model.aeronave_id = voo.aeronave_id
        voo_model.assentos_disponiveis = voo.assentos_disponiveis
        voo_model.status = voo.status.value #enum vira string


    def buscar(self, numero_voo: str):
        voo_model = self.session.query(VooModel).filter_by(numero_voo=numero_voo).first()
        
        if voo_model is None: #teste1
            return None

        voo_reconstruido = Voo( #teste2
            numero_voo=voo_model.numero_voo,
            trecho=Trecho(voo_model.origem, voo_model.destino),
            aeronave_id=voo_model.aeronave_id,
            capacidade_assentos=voo_model.assentos_disponiveis,
        )
        
        voo_reconstruido.status = StatusVoo(voo_model.status) 
        
        return voo_reconstruido


#--Aeronave

class SqlAlchemyAeronaveRepository(AeronaveRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, aeronave: Aeronave) -> None:
        model = self.session.query(AeronaveModel).filter_by(prefixo=aeronave.prefixo).first()
        if model is None:
            model = AeronaveModel.from_domain(aeronave)
            self.session.add(model)
        else:
            # mesmo contrato do repositorio falso: salvar uma aeronave que ja
            # existe atualiza, nao insere de novo
            model.modelo = aeronave.modelo
            model.capacidade = aeronave.capacidade
            model.validade_vistoria = aeronave.validade_vistoria
            # a ordem nao tem identidade no dominio, entao as ordens sao
            # regravadas; o delete-orphan apaga as antigas
            model.ordens_manutencao.clear()
            for ordem in aeronave.ordens_manutencao:
                model.ordens_manutencao.append(OrdemManutencaoModel.from_domain(ordem))
        self.session.commit()

    def buscar(self, prefixo):
        model = self.session.query(AeronaveModel).filter_by(prefixo=prefixo).first()
        if model is None:
            return None
        return model.to_domain()

    

# --- Tripulante e Escala

class SqlAlchemyTripulanteRepository(TripulanteRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, tripulante: Tripulante) -> None:
        model = self.session.query(TripulanteModel).filter_by(id=str(tripulante.id)).first()
        if model is None:
            model = TripulanteModel.from_domain(tripulante)
            self.session.add(model)
        else:
            model.nome = tripulante.nome
            model.cargo = tripulante.cargo.value
            model.teto_horas = tripulante.teto_horas
            model.horas_de_voo = tripulante.horas_de_voo
        self.session.commit()

    def buscar_por_id(self, tripulante_id):
        model = self.session.query(TripulanteModel).filter_by(id=str(tripulante_id)).first()
        if model is None:
            return None
        return model.to_domain()


class SqlAlchemyEscalaRepository(EscalaRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, escala: Escala) -> None:
        model = self.session.query(EscalaModel).filter_by(id=str(escala.id)).first()
        if model is None:
            model = EscalaModel.from_domain(escala)
            self.session.add(model)
        else:
            model.voo_id = escala.voo_id
            model.tripulantes.clear()
            for t_id in escala.tripulantes_ids:
                model.tripulantes.append(EscalaTripulanteModel(tripulante_id=str(t_id)))
        self.session.commit()

    def buscar_por_voo(self, voo_id: str):
        model = self.session.query(EscalaModel).filter_by(voo_id=str(voo_id)).first()
        if model is None:
            return None
        return model.to_domain()


# --- Despacho

from airline.domain.model import Despacho
from airline.domain.repositories import DespachoRepository
from airline.adapters.orm import DespachoModel, VolumeDespachoModel


class SqlAlchemyDespachoRepository(DespachoRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, despacho: Despacho) -> None:
        model = self.session.query(DespachoModel).filter_by(id=str(despacho.id)).first()
        if model is None:
            model = DespachoModel.from_domain(despacho)
            self.session.add(model)
        else:
            model.voo_id = despacho.voo_id
            model.carga_maxima = despacho.carga_maxima
            model.volumes.clear()
            for volume in despacho.volumes:
                model.volumes.append(VolumeDespachoModel(peso=volume.peso))
        self.session.commit()

    def buscar_por_id(self, despacho_id):
        model = self.session.query(DespachoModel).filter_by(id=str(despacho_id)).first()
        if model is None:
            return None
        return model.to_domain()

    def buscar_por_voo(self, voo_id: str):
        model = self.session.query(DespachoModel).filter_by(voo_id=str(voo_id)).first()
        if model is None:
            return None
        return model.to_domain()
