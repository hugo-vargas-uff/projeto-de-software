from airline.domain.model import Voo, StatusVoo, Trecho

def test_deve_criar_voo_agendado():
    trecho_ida = Trecho(origem="RJ", destino="SP")
    voo = Voo(numero_voo="MV-2019", trecho=trecho_ida)

    assert voo.numero_voo == "MV-2019"
    assert voo.trecho.origem =="RJ"
    assert voo.trecho.destino =="SP"
    assert voo.status == StatusVoo.AGENDADO

def test_deve_criar_trecho():
    trecho = Trecho(origem="RJ", destino="SP")
    assert trecho.origem == "RJ"
    assert trecho.destino == "SP"

def test_igualdade_de_trechos():
    trecho1 = Trecho(origem="RJ", destino="SP")
    trecho2 = Trecho(origem="RJ", destino="SP")
    assert trecho1==trecho2 #iguais
    trechoDif= Trecho(origem="SP", destino="SC")
    assert trechoDif!=trecho1 #sim, sao diferentes