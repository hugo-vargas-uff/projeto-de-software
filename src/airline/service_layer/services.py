from airline.domain.model import Reserva, Passageiro, Aeronave
from airline.domain.repositories import ReservaRepository, PassageiroRepository, AeronaveRepository
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


#---aeronave

class AeronaveService:

    def __init__(self, aeronave_repository: AeronaveRepository):
        self.aeronave_repository = aeronave_repository

    def cadastrar_aeronave(
        self,
        prefixo,
        modelo,
        capacidade,
        validade_vistoria
    ):
        aeronave = Aeronave(
            prefixo=prefixo,
            modelo=modelo,
            capacidade=capacidade,
            validade_vistoria=validade_vistoria
        )

        self.aeronave_repository.salvar(aeronave)

        return aeronave

    def abrir_ordem_manutencao(self, prefixo, descricao):
        aeronave = self.aeronave_repository.buscar(prefixo)

        if aeronave is None:
            return None

        ordem = aeronave.abrir_ordem_manutencao(descricao)

        self.aeronave_repository.salvar(aeronave)

        return ordem

    def concluir_ordem_manutencao(self, prefixo, descricao):
        aeronave = self.aeronave_repository.buscar(prefixo)

        if aeronave is None:
            return None

        ordem = next(
            (
                ordem
                for ordem in aeronave.ordens_manutencao
                if ordem.descricao == descricao
            ),
            None
        )

        if ordem is None:
            return None

        aeronave.concluir_ordem_manutencao(ordem)
        self.aeronave_repository.salvar(aeronave)

        return ordem

    def consultar_disponibilidade(self, prefixo, hoje):
        aeronave = self.aeronave_repository.buscar(prefixo)

        if aeronave is None:
            return None

        return aeronave.esta_disponivel(hoje)
