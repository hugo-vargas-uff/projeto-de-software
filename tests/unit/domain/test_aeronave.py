from airline.domain.model import Aeronave


def test_deve_criar_aeronave():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180
    )

    assert aeronave.prefixo == "PT-MVA"
    assert aeronave.modelo == "Boeing 737"
    assert aeronave.capacidade == 180


def test_igualdade_de_aeronaves():
    aeronave1 = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180
    )

    aeronave2 = Aeronave(
        prefixo="PT-MVA",
        modelo="Airbus A320",
        capacidade=200
    )

    assert aeronave1 == aeronave2


def test_aeronaves_diferentes():
    aeronave1 = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180
    )

    aeronave2 = Aeronave(
        prefixo="PT-MVB",
        modelo="Boeing 737",
        capacidade=180
    )

    assert aeronave1 != aeronave2


def test_aeronave_nova_deve_estar_disponivel():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180
    )

    assert aeronave.disponivel is True

def test_aeronaves_com_mesmo_prefixo_tem_mesmo_hash():
    aeronave1 = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180
    )

    aeronave2 = Aeronave(
        prefixo="PT-MVA",
        modelo="Airbus A320",
        capacidade=200
    )

    assert hash(aeronave1) == hash(aeronave2)