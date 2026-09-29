from airline.domain.model import Reserva, Passageiro, StatusReserva, Trecho, Voo
from airline.service_layer.services import ReservaService
from airline.service_layer.services import ReservaRepository
from airline.domain.exception import PassageiroNaoEncontrado
from test_passageiro_service import FakePassageiroRepository
from test_voo_service import FakeVooRepository

import pytest

class FakeReservaRepository(ReservaRepository):

    def __init__(self):
        self.reservas = {}

    def salvar(self, reserva: Reserva) -> None:
        chave = (reserva.voo_id, reserva.passageiro_id)
        self.reservas[chave] = reserva

    def buscar(self, voo_id, passageiro_id):
        chave = (voo_id, passageiro_id)
        return self.reservas.get(chave)

    def contar_reservas_por_voo(self, voo_id):
        return sum(
            1
            for reserva in self.reservas.values()
            if reserva.voo_id == voo_id
            and reserva.status == StatusReserva.CONFIRMADA
        )

def test_deve_criar_reserva():

    reserva_repository = FakeReservaRepository()
    passageiro_repository = FakePassageiroRepository()
    voo_repository = FakeVooRepository()

    service = ReservaService(
        reserva_repository,
        passageiro_repository,
        voo_repository
    )

    passageiro = Passageiro(nome="pedro",cpf="717.774.400-25")

    trecho = Trecho(origem="Rio de Janeiro",destino="São Paulo")

    voo = Voo(
        numero_voo="voo-123",
        trecho=trecho,
        aeronave_id="PT-ABC",
        capacidade_assentos=180
    )

    passageiro_repository.salvar(passageiro)
    voo_repository.salvar(voo)

    reserva = service.criar_reserva(voo_id="voo-123",passageiro_id=passageiro.id)

    assert reserva.voo_id == "voo-123"
    assert reserva.passageiro_id == passageiro.id
    assert reserva.status == StatusReserva.CONFIRMADA

def test_buscar_reserva():

    reserva_repository = FakeReservaRepository()
    passageiro_repository = FakePassageiroRepository()
    voo_repository = FakeVooRepository()

    service = ReservaService(
        reserva_repository,
        passageiro_repository,
        voo_repository
    )

    passageiro = Passageiro(nome="pedro",cpf="717.774.400-25")

    trecho = Trecho(origem="Rio de Janeiro",destino="São Paulo")

    voo = Voo(
        numero_voo="voo-123",
        trecho=trecho,
        aeronave_id="PT-ABC",
        capacidade_assentos=180
    )

    reserva = Reserva(voo_id="voo-123",passageiro_id=passageiro.id)

    passageiro_repository.salvar(passageiro)
    voo_repository.salvar(voo)
    reserva_repository.salvar(reserva)

    reserva_salva = service.buscar(voo_id=reserva.voo_id,passageiro_id=reserva.passageiro_id)

    assert reserva_salva is not None
    assert reserva_salva.voo_id == "voo-123"
    assert reserva_salva.passageiro_id == passageiro.id
    assert reserva_salva.status == StatusReserva.CONFIRMADA

def test_contar_reservas_por_voo():
    passageiro = Passageiro(nome="pedro", cpf="717.774.400-25")
    passageiro1 = Passageiro(nome="ana", cpf="575.568.540-19")
    passageiro2 = Passageiro(nome="henrique", cpf="282.154.860-53")
    passageiro3 = Passageiro(nome="joao", cpf="418.268.960-74")

    reserva1 = Reserva(voo_id="voo-123", passageiro_id=passageiro.id)
    reserva2 = Reserva(voo_id="voo-123", passageiro_id=passageiro1.id)
    reserva3 = Reserva(voo_id="voo-123", passageiro_id=passageiro2.id)
    reserva4 = Reserva(voo_id="voo-123", passageiro_id=passageiro3.id)

    reserva_repository = FakeReservaRepository()
    passageiro_repository = FakePassageiroRepository()
    voo_repository = FakeVooRepository()

    service = ReservaService(
        reserva_repository,
        passageiro_repository,
        voo_repository
    )

    reserva_repository.salvar(reserva1)
    reserva_repository.salvar(reserva2)
    reserva_repository.salvar(reserva3)
    reserva_repository.salvar(reserva4)

    numero_de_reservas = service.contar_reservas_por_voo(voo_id="voo-123")

    assert numero_de_reservas == 4

def test_lanca_excecao_tentando_criar_reserva_sem_passageiro():

    reserva_repository = FakeReservaRepository()
    passageiro_repository = FakePassageiroRepository()
    voo_repository = FakeVooRepository()

    service = ReservaService(
        reserva_repository,
        passageiro_repository,
        voo_repository
    )

    with pytest.raises(PassageiroNaoEncontrado, match="Passageiro nao encontrado"):
        service.criar_reserva(voo_id="voo-123", passageiro_id="ID-NAO-EXISTENTE")