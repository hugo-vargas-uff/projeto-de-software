
from airline.domain.model import Despacho, Volume, ErroRegraDespacho


def test_deve_criar_despacho_com_peso_total_zero():
    despacho = Despacho(carga_maxima=1000)

    assert despacho.peso_total() == 0


def test_deve_adicionar_volume_dentro_do_limite():
    despacho = Despacho(carga_maxima=1000)
    volume = Volume(peso=150)

    despacho.adicionar_volume(volume)

    assert despacho.peso_total() == 150

