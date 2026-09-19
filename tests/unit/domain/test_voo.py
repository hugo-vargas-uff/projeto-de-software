from airline.domain.model import Voo, StatusVoo, Trecho

def test_deve_criar_voo_agendado():
    voo = Voo(numero_voo="MV-2019")

    assert voo.numero_voo == "MV-2019"
    assert voo.status == StatusVoo.AGENDADO

def test_deve_criar_trecho():
    trecho = Trecho(origem="GRU", destino="GIG")
    assert trecho.origem == "GRU"
    assert trecho.destino == "GIG"