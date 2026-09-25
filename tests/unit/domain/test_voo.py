import pytest
from airline.domain.model import Voo, StatusVoo, Trecho, ErroRegraVoo

def test_deve_criar_voo_agendado():
    trecho_ida = Trecho(origem="RJ", destino="SP")
    voo = Voo(numero_voo="MV-2019", trecho=trecho_ida, aeronave_id="A11", capacidade_assentos=100)

    assert voo.numero_voo == "MV-2019"
    assert voo.trecho.origem =="RJ"
    assert voo.trecho.destino =="SP"
    assert voo.status == StatusVoo.AGENDADO
    assert voo.aeronave_id == "A11"
    assert voo.assentos_disponiveis == 100

def test_deve_criar_trecho():
    trecho = Trecho(origem="RJ", destino="SP")
    assert trecho.origem == "RJ"
    assert trecho.destino == "SP"

def test_igualdade_de_trechos():
    trecho1 = Trecho(origem="RJ", destino="SP")
    trecho2 = Trecho(origem="RJ", destino="SP")
    assert trecho1==trecho2 #iguais
    trechoDif= Trecho(origem="SP", destino="SC")
    assert trechoDif != trecho1 #sim, sao diferentes

def test_cancelar_voo():
    rota = Trecho(origem="SP", destino="RJ")
    voo = Voo(numero_voo="DOG-1", trecho=rota, aeronave_id="A11", capacidade_assentos=100)

    assert voo.status == StatusVoo.AGENDADO #para evitar falso positivo, verifica antes se ja nao estava cancelado
    voo.cancelar()
    assert voo.status == StatusVoo.CANCELADO

def test_realizar_voo():
    rota = Trecho(origem="RJ", destino="SP")
    voo = Voo(numero_voo="DOG-2", trecho=rota, aeronave_id="A11", capacidade_assentos=100)
    
    assert voo.status == StatusVoo.AGENDADO #tem que estar agendado primeiro
    voo.realizar()
    assert voo.status == StatusVoo.REALIZADO

def test_erro_realizar_um_voo_ja_cancelado():
    voo = Voo(numero_voo="MV-777", trecho=Trecho(origem="SP", destino="RJ"), aeronave_id="A11", capacidade_assentos=100)
    voo.cancelar() #primeiro cancela o voo
    #tenta realizar e espera que de erro
    with pytest.raises(ErroRegraVoo):
        voo.realizar()

def test_erro_cancelar_um_voo_ja_realizado():
    rota = Trecho(origem="SP", destino="RJ")
    decolado = Voo(numero_voo="MV-999", trecho=rota, aeronave_id="A11", capacidade_assentos=100)
    
    decolado.realizar() #realiza o voo primeiro
    #espera erro ao cancelar
    with pytest.raises(ErroRegraVoo):
        decolado.cancelar()
