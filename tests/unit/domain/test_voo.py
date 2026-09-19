from airline.domain.model import Voo, StatusVoo

def test_deve_criar_voo_agendado():
    voo = Voo(numero_voo="MV-2019")

    assert voo.numero_voo == "MV-2019"
    assert voo.status == StatusVoo.AGENDADO
