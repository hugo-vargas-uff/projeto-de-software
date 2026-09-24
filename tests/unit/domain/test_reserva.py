from airline.domain.model import Reserva, StatusReserva

def test_deve_criar_reserva_confirmada():
    voo_id = "voo-123"
    passageiro_id = "passageiro-123"

    reserva = Reserva(voo_id=voo_id, passageiro_id=passageiro_id)

    assert reserva.voo_id == voo_id
    assert reserva.passageiro_id == passageiro_id
    assert reserva.status == StatusReserva.CONFIRMADA

def test_deve_cancelar_uma_reserva():
    voo_id = "voo-123"
    passageiro_id = "passageiro-123"

    reserva = Reserva(voo_id=voo_id, passageiro_id=passageiro_id)

    reserva.cancelar()

    assert reserva.voo_id == voo_id
    assert reserva.passageiro_id == passageiro_id
    assert reserva.status == StatusReserva.CANCELADA