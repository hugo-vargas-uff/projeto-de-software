import pytest

from airline.domain.model import Reserva, StatusReserva,ErroRegraVoo
from airline.service_layer.observadores_voo import ObservadorDeVoo, CancelaReservasDoVoo
from test_voo_service import montar_servico, novo_voo
from test_reserva_service import FakeReservaRepository

class ObservadorEspiao(ObservadorDeVoo):
    def __init__(self):
        self.voos_cancelados = []

    def voo_cancelado(self, numero_voo):
        self.voos_cancelados.append(numero_voo)

def test_cancelar_voo_avisa_todos_os_observadores():
    servico, voos, aeronaves, session = montar_servico()
    voos.salvar(novo_voo("MV-100"))
    primeiro, segundo = ObservadorEspiao(), ObservadorEspiao()
    servico.inscrever(primeiro)
    servico.inscrever(segundo)

    servico.cancelar_voo("MV-100")

    assert primeiro.voos_cancelados == ["MV-100"]
    assert segundo.voos_cancelados == ["MV-100"]

def test_cancelamento_recusado_nao_avisa_ninguem():
    servico, voos, aeronaves, session = montar_servico()
    voo = novo_voo("MV-100")
    voo.realizar()
    voos.salvar(voo)
    espiao = ObservadorEspiao()
    servico.inscrever(espiao)

    #voo realizado nao pode ser cancelado, entao nao ha o que avisar
    with pytest.raises(ErroRegraVoo):
        servico.cancelar_voo("MV-100")

    assert espiao.voos_cancelados == []

def test_cancela_so_as_reservas_confirmadas_do_voo():
    reservas = FakeReservaRepository()
    reservas.salvar(Reserva(voo_id="MV-100", passageiro_id="P1"))
    reservas.salvar(Reserva(voo_id="MV-100", passageiro_id="P2"))
    reservas.salvar(Reserva(voo_id="MV-200", passageiro_id="P1"))

    CancelaReservasDoVoo(reservas).voo_cancelado("MV-100")

    assert reservas.buscar("MV-100", "P1").status == StatusReserva.CANCELADA
    assert reservas.buscar("MV-100", "P2").status == StatusReserva.CANCELADA
    assert reservas.buscar("MV-200", "P1").status == StatusReserva.CONFIRMADA  #outro voo, nao muda
