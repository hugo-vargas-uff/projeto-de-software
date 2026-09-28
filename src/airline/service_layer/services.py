from airline.domain.model import Reserva, Passageiro, Tripulante, CargoTripulante, Escala, ErroRegraTripulacao
from airline.domain.repositories import ReservaRepository, PassageiroRepository, TripulanteRepository, EscalaRepository
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

    

# --- Serviços de Tripulação e Escala

class TripulanteService:

    def __init__(self, tripulante_repository: TripulanteRepository):
        self.tripulante_repository = tripulante_repository

    def cadastrar_tripulante(self, nome: str, cargo: CargoTripulante, teto_horas: float = 85.0) -> Tripulante:
        tripulante = Tripulante(nome=nome, cargo=cargo, teto_horas=teto_horas)
        self.tripulante_repository.salvar(tripulante)
        return tripulante

    def buscar_por_id(self, tripulante_id):
        return self.tripulante_repository.buscar_por_id(tripulante_id)


class EscalaService:

    def __init__(self, escala_repo: EscalaRepository, tripulante_repo: TripulanteRepository):
        self.escala_repo = escala_repo
        self.tripulante_repo = tripulante_repo

    def escalar_tripulante(self, voo_id: str, tripulante_id, duracao_horas_voo: float) -> Escala:
        tripulante = self.tripulante_repo.buscar_por_id(tripulante_id)
        if tripulante is None:
            raise ErroRegraTripulacao("Tripulante nao encontrado")

        # Verifica se já existe escala para este voo ou cria nova
        escala = self.escala_repo.buscar_por_voo(voo_id)
        if escala is None:
            escala = Escala(voo_id=voo_id)

        # Regras de negócio
        tripulante.registrar_horas_de_voo(duracao_horas_voo)
        escala.adicionar_tripulante(tripulante_id)

        # Persistência
        self.tripulante_repo.salvar(tripulante)
        self.escala_repo.salvar(escala)

        return escala

    def consultar_escala(self, voo_id: str):
        return self.escala_repo.buscar_por_voo(voo_id)