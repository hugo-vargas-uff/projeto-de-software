from airline.domain.model import Voo, Trecho
from airline.domain.repositories import VooRepository

class FakeVooRepository(VooRepository):
    def __init__(self):
        self._voos = []

    def salvar(self, voo: Voo) -> None:
        self._voos.append(voo)

    def buscar(self, numero_voo: str):
        for voo in self._voos:
            if voo.numero_voo == numero_voo:
                return voo
        return None

def test_fake_salvar_e_buscar():
    repo = FakeVooRepository()
    voo = Voo(numero_voo="MV-999", trecho=Trecho("GIG", "BSB"), aeronave_id="PR-999", capacidade_assentos=100)
    
    repo.salvar(voo)
    voo_salvo = repo.buscar("MV-999")
    
    assert voo_salvo is not None
    assert voo_salvo.numero_voo == "MV-999"
