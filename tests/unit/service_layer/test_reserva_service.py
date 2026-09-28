from airline.domain.model import Reserva, Passageiro, StatusReserva
from airline.service_layer.services import ReservaService
from airline.service_layer.services import ReservaRepository

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

    passageiro = Passageiro("pedro", "717.774.400-25")

    repository = FakeReservaRepository()
    service = ReservaService(repository)

    reserva = service.criar_reserva(voo_id="voo-123", passageiro_id=passageiro.id)

    assert reserva.voo_id == "voo-123"
    assert reserva.passageiro_id == passageiro.id
    assert reserva.status == StatusReserva.CONFIRMADA

def test_buscar_reserva():
    passageiro = Passageiro("pedro", "717.774.400-25")

    reserva = Reserva(voo_id="voo-123", passageiro_id=passageiro.id)

    repository = FakeReservaRepository()

    repository.salvar(reserva)

    service = ReservaService(repository)

    reserva_salva = service.buscar(voo_id=reserva.voo_id, passageiro_id=reserva.passageiro_id)

    assert reserva_salva.voo_id == "voo-123"
    assert reserva_salva.passageiro_id == passageiro.id
    assert reserva_salva.status == StatusReserva.CONFIRMADA

def test_contar_reservas_por_voo():
    passageiro = Passageiro("pedro", "717.774.400-25")
    passageiro1 = Passageiro("ana", "575.568.540-19")
    passageiro2 = Passageiro("henrique", "282.154.860-53")
    passageiro3 = Passageiro("joao", "418.268.960-74")

    reserva1 = Reserva(voo_id="voo-123", passageiro_id=passageiro.id)
    reserva2 = Reserva(voo_id="voo-123", passageiro_id=passageiro1.id)
    reserva3 = Reserva(voo_id="voo-123", passageiro_id=passageiro2.id)
    reserva4 = Reserva(voo_id="voo-123", passageiro_id=passageiro3.id)

    repository = FakeReservaRepository()

    repository.salvar(reserva1)
    repository.salvar(reserva2)
    repository.salvar(reserva3)
    repository.salvar(reserva4)

    service = ReservaService(repository)

    numero_de_reservas = service.contar_reservas_por_voo(voo_id="voo-123")

    assert numero_de_reservas == 4
