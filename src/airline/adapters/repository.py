from airline.domain.model import Reserva, Passageiro
from airline.service_layer.services import (
    ReservaRepository,
    PassageiroRepository
)
from airline.adapters.orm import ReservaModel, PassageiroModel

class SqlAlchemyReservaRepository(ReservaRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, reserva: Reserva) -> None:
        reserva_model = ReservaModel(
                id = str(reserva.id),
                voo_id = str(reserva.voo_id),
                passageiro_id = str(reserva.passageiro_id),
                status = reserva.status
        )

        self.session.add(reserva_model)
        self.session.commit()

    def buscar(self, reserva_id):
        ...

    def contar_reservas_por_voo(self, voo_id):
        ...


class SqlAlchemyPassageiroRepository(PassageiroRepository):

    def __init__(self, session):
        self.session = session

    def salvar(self, passageiro: Passageiro) -> None:
        passageiro_model = PassageiroModel(
            id = str(passageiro.id),
            nome = passageiro.nome,
            cpf = passageiro.cpf
        )

        self.session.add(passageiro_model)
        self.session.commit()

    def buscar(self, passageiro_id):
        ...
