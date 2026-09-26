from datetime import date
from airline.domain.model import Aeronave
from airline.domain.repositories import AeronaveRepository


class FakeAeronaveRepository(AeronaveRepository):

    def __init__(self):
        self.aeronaves = {}

    def salvar(self, aeronave):
        self.aeronaves[aeronave.prefixo] = aeronave

    def buscar(self, prefixo):
        return self.aeronaves.get(prefixo)


#----testes

def test_salvar_e_buscar_aeronave_por_prefixo():
    repositorio = FakeAeronaveRepository()

    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    repositorio.salvar(aeronave)

    encontrada = repositorio.buscar("PT-MVA")

    assert encontrada == aeronave

def test_buscar_aeronave_inexistente_retorna_none():
    repositorio = FakeAeronaveRepository()

    encontrada = repositorio.buscar("PT-XXX")

    assert encontrada is None