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


def test_tripulante_pode_voar_quando_dentro_do_teto():
    tripulante = Tripulante(
        nome="Mariana Souza",
        cargo=CargoTripulante.COPILOTO,
        teto_horas=85.0
    )
    tripulante.registrar_horas_de_voo(70.0)

    assert tripulante.pode_voar(10.0) is True
    assert tripulante.pode_voar(15.0) is True
    assert tripulante.pode_voar(15.1) is False


def test_deve_permitir_acumular_horas_exatamente_ate_o_teto():
    tripulante = Tripulante(
        nome="Carlos Silva",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )
    tripulante.registrar_horas_de_voo(85.0)

    assert tripulante.horas_de_voo == 85.0
    assert tripulante.pode_voar(0.1) is False
