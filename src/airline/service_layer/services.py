from airline.domain.model import (
    Reserva,
    Passageiro,
    Aeronave,
    Tripulante,
    CargoTripulante,
    Escala,
    ErroRegraTripulacao
)
from airline.domain.repositories import (
    ReservaRepository,
    PassageiroRepository,
    AeronaveRepository,
    TripulanteRepository,
    EscalaRepository
)
from airline.domain.exception import CpfJaCadastradoException, PassageiroNaoEncontrado
from airline.domain.model import Voo, Trecho
from airline.domain.repositories import VooRepository
from airline.domain.exception import VooJaExiste, VooNaoEncontrado, AeronaveNaoEncontrada, AeronaveIndisponivel

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

        passageiro = Passageiro(nome=nome, cpf=cpf)
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

        escala = self.escala_repo.buscar_por_voo(voo_id)
        if escala is None:
            escala = Escala(voo_id=voo_id)

        tripulante.registrar_horas_de_voo(duracao_horas_voo)
        escala.adicionar_tripulante(tripulante_id)

        self.tripulante_repo.salvar(tripulante)
        self.escala_repo.salvar(escala)

        return escala

    def consultar_escala(self, voo_id: str):
        return self.escala_repo.buscar_por_voo(voo_id)


# --- Serviço de Aeronave

class AeronaveService:

    def __init__(self, aeronave_repository: AeronaveRepository):
        self.aeronave_repository = aeronave_repository

    def cadastrar_aeronave(self, prefixo, modelo, capacidade, validade_vistoria):
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
            (ordem for ordem in aeronave.ordens_manutencao if ordem.descricao == descricao),
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


# --- Serviço Voo

class VooService:

    def __init__(self, voo_repository: VooRepository, aeronave_repository: AeronaveRepository, session):
        self.voo_repository = voo_repository
        self.aeronave_repository = aeronave_repository
        self.session = session

    def agendar_voo(self, numero_voo, origem, destino, prefixo_aeronave, hoje):
        if self.voo_repository.buscar(numero_voo) is not None:
            raise VooJaExiste(f"Ja existe um voo com o numero {numero_voo}")

        aeronave = self.aeronave_repository.buscar(prefixo_aeronave)
        if aeronave is None:
            raise AeronaveNaoEncontrada(f"Aeronave {prefixo_aeronave} nao encontrada")

        if not aeronave.esta_disponivel(hoje):
            raise AeronaveIndisponivel(f"Aeronave {prefixo_aeronave} esta indisponivel")

        voo = Voo(
            numero_voo=numero_voo,
            trecho=Trecho(origem, destino),
            aeronave_id=prefixo_aeronave,
            capacidade_assentos=aeronave.capacidade,
        )

        self.voo_repository.salvar(voo)
        self.session.commit()
        return voo.numero_voo

    def cancelar_voo(self, numero_voo):
        voo = self._buscar_voo(numero_voo)
        voo.cancelar()  #se o voo ja foi realizado ou cancelado, Voo lanca ErroRegraVoo
        self.voo_repository.salvar(voo)
        self.session.commit()
        return voo.status.value

    def _buscar_voo(self, numero_voo):
        #busca usada por varios casos de uso, se nao achar, avisa com um erro claro
        voo = self.voo_repository.buscar(numero_voo)
        if voo is None:
            raise VooNaoEncontrado(f"Voo {numero_voo} nao encontrado")
        return voo
