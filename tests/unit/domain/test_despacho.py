
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

