import uuid
import pytest

from airline.domain.model import Despacho, Volume, ErroRegraDespacho
from airline.domain.repositories import DespachoRepository
from airline.domain.exception import DespachoNaoEncontrado
from airline.service_layer.services import DespachoService


class FakeDespachoRepository(DespachoRepository):

    def __init__(self):
        self.despachos = {}

    def salvar(self, despacho):
        self.despachos[despacho.id] = despacho

    def buscar_por_id(self, despacho_id):
        return self.despachos.get(despacho_id)

    def buscar_por_voo(self, voo_id):
        for despacho in self.despachos.values():
            if despacho.voo_id == voo_id:
                return despacho
        return None


#----testes

def test_abrir_despacho():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    despacho = service.abrir_despacho(voo_id="MV-3000", carga_maxima=1000)

    encontrado = repo.buscar_por_id(despacho.id)

    assert encontrado == despacho
    assert encontrado.voo_id == "MV-3000"
    assert encontrado.carga_maxima == 1000
    assert encontrado.peso_total() == 0


def test_nao_deve_abrir_dois_despachos_para_o_mesmo_voo():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    service.abrir_despacho(voo_id="MV-3000", carga_maxima=1000)

    with pytest.raises(ErroRegraDespacho):
        service.abrir_despacho(voo_id="MV-3000", carga_maxima=500)

    assert len(repo.despachos) == 1


def test_adicionar_volume():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    despacho = service.abrir_despacho(voo_id="MV-3000", carga_maxima=1000)

    service.adicionar_volume(despacho.id, peso=150)

    encontrado = repo.buscar_por_id(despacho.id)
    assert encontrado.volumes == [Volume(peso=150)]
    assert encontrado.peso_total() == 150


def test_adicionar_volume_acima_da_carga_maxima():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    despacho = service.abrir_despacho(voo_id="MV-3000", carga_maxima=1000)
    service.adicionar_volume(despacho.id, peso=900)

    with pytest.raises(ErroRegraDespacho):
        service.adicionar_volume(despacho.id, peso=200)

    assert repo.buscar_por_id(despacho.id).peso_total() == 900


def test_adicionar_volume_em_despacho_inexistente():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    with pytest.raises(DespachoNaoEncontrado):
        service.adicionar_volume(uuid.uuid4(), peso=100)


def test_consultar_despacho():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    despacho = Despacho(voo_id="MV-3000", carga_maxima=1000)
    despacho.adicionar_volume(Volume(peso=300))
    repo.salvar(despacho)

    encontrado = service.consultar_despacho(despacho.id)

    assert encontrado == despacho
    assert encontrado.peso_total() == 300


def test_consultar_despacho_inexistente():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    with pytest.raises(DespachoNaoEncontrado):
        service.consultar_despacho(uuid.uuid4())


def test_consultar_peso_disponivel():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    despacho = service.abrir_despacho(voo_id="MV-3000", carga_maxima=1000)
    service.adicionar_volume(despacho.id, peso=250)

    assert service.consultar_peso_disponivel(despacho.id) == 750


def test_consultar_peso_disponivel_de_despacho_inexistente():
    repo = FakeDespachoRepository()
    service = DespachoService(repo)

    with pytest.raises(DespachoNaoEncontrado):
        service.consultar_peso_disponivel(uuid.uuid4())
