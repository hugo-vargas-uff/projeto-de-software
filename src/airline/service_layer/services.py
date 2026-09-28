from airline.domain.model import Reserva, Passageiro
from airline.domain.repositories import ReservaRepository, PassageiroRepository
from airline.domain.exception import CpfJaCadastradoException, PassageiroNaoEncontrado

class ReservaService:

    def __init__(self, reserva_repository: ReservaRepository, passageiro_repository: PassageiroRepository):
        self.reserva_repository = reserva_repository
        self.passageiro_repository = passageiro_repository

    def criar_reserva(self, voo_id, passageiro_id):
        if self.passageiro_repository.buscar_por_id(passageiro_id) is None:
            raise PassageiroNaoEncontrado("Passageiro nao encontrado")

        reserva = Reserva(voo_id=voo_id, passageiro_id=passageiro_id)

        self.reserva_repository.salvar(reserva)

        return reserva

    def buscar(self, voo_id, passageiro_id):
        if self.passageiro_repository.buscar_por_id(passageiro_id) is None:
            raise PassageiroNaoEncontrado("Passageiro nao encontrado")

        return self.reserva_repository.buscar(voo_id, passageiro_id)

    def contar_reservas_por_voo(self, voo_id):
        return self.reserva_repository.contar_reservas_por_voo(voo_id)


class PassageiroService:

    def __init__(self, passageiro_repository: PassageiroRepository):
        self.passageiro_repository = passageiro_repository

    def criar_passageiro(self, nome, cpf):
        if self.passageiro_repository.buscar_por_cpf(cpf) is not None:
            raise CpfJaCadastradoException("Já existe um passageiro cadastrado com este CPF.")

        passageiro = Passageiro(nome=nome,cpf=cpf)

        self.passageiro_repository.salvar(passageiro)

        return passageiro

    def buscar(self, cpf):
        return self.passageiro_repository.buscar_por_cpf(cpf)