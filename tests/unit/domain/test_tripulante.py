import pytest
from airline.domain.model import Tripulante, CargoTripulante, ErroRegraTripulacao


def test_deve_criar_tripulante_com_horas_zeradas():
    tripulante = Tripulante(
        nome="Carlos Silva",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )

    assert tripulante.nome == "Carlos Silva"
    assert tripulante.cargo == CargoTripulante.PILOTO
    assert tripulante.teto_horas == 85.0
    assert tripulante.horas_de_voo == 0.0


def test_deve_acumular_horas_de_voo_dentro_do_teto():
    tripulante = Tripulante(
        nome="Carlos Silva",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )

    tripulante.registrar_horas_de_voo(10.5)

    assert tripulante.horas_de_voo == 10.5


def test_erro_ao_ultrapassar_teto_regulamentar_de_horas():
    tripulante = Tripulante(
        nome="Carlos Silva",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )
    tripulante.registrar_horas_de_voo(80.0)

    with pytest.raises(ErroRegraTripulacao, match="Teto regulamentar de horas ultrapassado"):
        tripulante.registrar_horas_de_voo(10.0)

    assert tripulante.horas_de_voo == 80.0