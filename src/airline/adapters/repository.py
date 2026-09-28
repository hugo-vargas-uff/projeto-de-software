from airline.domain.model import Reserva, Passageiro, Voo, Aeronave, Trecho, StatusVoo, StatusOrdemManutencao, StatusReserva
from airline.domain.repositories import VooRepository

from airline.adapters.orm import ReservaModel, PassageiroModel, VooModel, AeronaveModel, OrdemManutencaoModel

from airline.domain.repositories import AeronaveRepository, ReservaRepository, PassageiroRepository

class SqlAlchemyReservaRepository(ReservaRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, reserva: Reserva) -> None:
        reserva_model = ReservaModel.from_domain(reserva)

        self.session.add(reserva_model)
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
        aeronave_model = AeronaveModel(
            prefixo=aeronave.prefixo,
            modelo=aeronave.modelo,
            capacidade=aeronave.capacidade,
            validade_vistoria=aeronave.validade_vistoria
        )

        for ordem in aeronave.ordens_manutencao:
            ordem_model = OrdemManutencaoModel(
                descricao=ordem.descricao,
                status=ordem.status
            )

            aeronave_model.ordens_manutencao.append(ordem_model)

        self.session.add(aeronave_model)
        self.session.commit()

    def buscar(self, prefixo):
        aeronave_model = (
            self.session.query(AeronaveModel)
            .filter_by(prefixo=prefixo)
            .first()
        )

        if aeronave_model is None:
            return None

        aeronave = Aeronave(
            prefixo=aeronave_model.prefixo,
            modelo=aeronave_model.modelo,
            capacidade=aeronave_model.capacidade,
            validade_vistoria=aeronave_model.validade_vistoria
        )

        for ordem_model in aeronave_model.ordens_manutencao:
            ordem = aeronave.abrir_ordem_manutencao(
                ordem_model.descricao
            )

            if ordem_model.status == StatusOrdemManutencao.CONCLUIDA:
                aeronave.concluir_ordem_manutencao(ordem)

        return aeronave

