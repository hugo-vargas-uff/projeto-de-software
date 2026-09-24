from airline.domain.model import Reserva, Passageiro
from airline.domain.repositories import ReservaRepository, PassageiroRepository

class ReservaService:

    def __init__(self, reserva_repository: ReservaRepository):
        self.reserva_repository = reserva_repository

    def criar_reserva(self, voo_id, passageiro_id):

        reserva = Reserva(voo_id=voo_id, passageiro_id=passageiro_id)

        self.reserva_repository.salvar(reserva)

        return reserva


class PassageiroService:

    def __init__(self, passageiro_repository: PassageiroRepository):
        self.passageiro_repository = passageiro_repository

    def criar_passageiro(self, nome, cpf):

        passageiro = Passageiro(nome=nome,cpf=cpf)

        self.passageiro_repository.salvar(passageiro)

        return passageiro