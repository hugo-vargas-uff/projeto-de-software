from airline.domain.model import Reserva, StatusReserva
from airline.service_layer.services import ReservaService
from airline.service_layer.services import ReservaRepository

class FakeReservaRepository(ReservaRepository):

    def __init__(self):
        self.reservas = {}

    def salvar(self, reserva: Reserva) -> None:
        self.reservas[reserva.id] = reserva

    def buscar(self, reserva_id):
        return self.reservas.get(reserva_id)

    def contar_reservas_por_voo(self, voo_id):
        return sum(
            1
            for reserva in self.reservas.values()
            if reserva.voo_id == voo_id
            and reserva.status == StatusReserva.CONFIRMADA
        )

def test_deve_criar_reserva():

    repository = FakeReservaRepository()
    service = ReservaService(repository)

    reserva = service.criar_reserva(voo_id="voo-123", passageiro_id="passageiro-123")

    assert reserva.voo_id == "voo-123"
    assert reserva.passageiro_id == "passageiro-123"
    assert reserva.status == StatusReserva.CONFIRMADA