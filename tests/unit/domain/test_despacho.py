
import uuid
import pytest

from airline.domain.model import Despacho, Volume, ErroRegraDespacho


def test_deve_criar_despacho_com_peso_total_zero():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)

    assert despacho.peso_total() == 0


def test_deve_adicionar_volume_dentro_do_limite():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    volume = Volume(peso=150)

    despacho.adicionar_volume(volume)

    assert despacho.peso_total() == 150


def test_despacho_deve_ter_id_e_referenciar_voo_por_id():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)

    assert isinstance(despacho.id, uuid.UUID)
    assert despacho.voo_id == "MV-3000"


def test_nao_deve_adicionar_volume_acima_da_carga_maxima():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Volume(peso=900))

    with pytest.raises(ErroRegraDespacho):
        despacho.adicionar_volume(Volume(peso=200))

    assert despacho.peso_total() == 900
    assert len(despacho.volumes) == 1


def test_deve_permitir_completar_exatamente_a_carga_maxima():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)

    despacho.adicionar_volume(Volume(peso=600))
    despacho.adicionar_volume(Volume(peso=400))

    assert despacho.peso_total() == 1000


def test_deve_calcular_peso_disponivel():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Volume(peso=250))

    assert despacho.peso_disponivel() == 750


def test_volumes_com_mesmo_peso_sao_iguais():
    assert Volume(peso=150) == Volume(peso=150)


def test_despachos_com_mesmo_id_sao_iguais():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    mesmo_despacho = Despacho.restaurar(
        id=despacho.id,
        voo_id="MV-3000",
        carga_maxima=1000,
        volumes=[]
    )

    assert despacho == mesmo_despacho
    assert despacho != Despacho(voo_id="MV-3000", carga_maxima=1000)


def test_deve_restaurar_despacho():
    despacho_id = uuid.uuid4()

    despacho = Despacho.restaurar(
        id=despacho_id,
        voo_id="MV-3000",
        carga_maxima=1000,
        volumes=[Volume(peso=100), Volume(peso=200)]
    )

    assert despacho.id == despacho_id
    assert despacho.voo_id == "MV-3000"
    assert despacho.carga_maxima == 1000
    assert despacho.peso_total() == 300



# ---- Composite: Volume (folha) e Conteiner (composto)

from dataclasses import FrozenInstanceError

from airline.domain.model import Conteiner, ItemDespacho


def test_volume_e_conteiner_sao_itens_do_despacho():
    assert isinstance(Volume(peso=20), ItemDespacho)
    assert isinstance(Conteiner(codigo="AKE12345AA", tara=80), ItemDespacho)


def test_peso_do_conteiner_soma_a_tara_e_os_volumes():
    conteiner = Conteiner(
        codigo="AKE12345AA",
        tara=80,
        itens=[Volume(peso=23), Volume(peso=32), Volume(peso=15)]
    )

    assert conteiner.peso_total() == 150
    assert conteiner.quantidade_volumes() == 3


def test_conteiner_vazio_pesa_so_a_tara():
    conteiner = Conteiner(codigo="AKE12345AA", tara=80)

    assert conteiner.peso_total() == 80
    assert conteiner.quantidade_volumes() == 0


def test_conteiner_dentro_de_conteiner_soma_recursivamente():
    conteiner_a = Conteiner(codigo="AKE00001AA", tara=80, itens=[Volume(peso=20), Volume(peso=30)])
    conteiner_b = Conteiner(codigo="AKE00002AA", tara=80, itens=[Volume(peso=10)])
    palete = Conteiner(codigo="PMC00001AA", tara=120, itens=[conteiner_a, conteiner_b, Volume(peso=40)])

    assert palete.peso_total() == 120 + (80 + 50) + (80 + 10) + 40
    assert palete.quantidade_volumes() == 4


def test_despacho_trata_volume_e_conteiner_do_mesmo_jeito():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)

    despacho.adicionar_volume(Volume(peso=100))
    despacho.adicionar_volume(
        Conteiner(codigo="AKE12345AA", tara=80, itens=[Volume(peso=20), Volume(peso=30)])
    )

    assert despacho.peso_total() == 230
    assert despacho.peso_disponivel() == 770
    assert despacho.quantidade_volumes() == 3


def test_tara_do_conteiner_conta_na_carga_maxima():
    despacho = Despacho(voo_id="MV-3000", carga_maxima=200)
    # os volumes somam 150, mas com a tara de 80 o conteiner pesa 230
    conteiner = Conteiner(codigo="AKE12345AA", tara=80, itens=[Volume(peso=100), Volume(peso=50)])

    with pytest.raises(ErroRegraDespacho):
        despacho.adicionar_volume(conteiner)

    assert despacho.peso_total() == 0
    assert despacho.volumes == []


def test_conteiner_nao_aceita_volume_depois_de_criado():
    conteiner = Conteiner(codigo="AKE12345AA", tara=80, itens=[Volume(peso=20)])

    assert isinstance(conteiner.itens, tuple)
    with pytest.raises(FrozenInstanceError):
        conteiner.itens = (Volume(peso=20), Volume(peso=500))
