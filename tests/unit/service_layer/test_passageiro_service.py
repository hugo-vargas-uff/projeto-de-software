from airline.domain.model import Passageiro
from airline.service_layer.services import PassageiroService
from airline.service_layer.services import PassageiroRepository

class FakePassageiroRepository(PassageiroRepository):

    def __init__(self):
        self.passageiros = {}

    def salvar(self, passageiro: Passageiro) -> None:
        self.passageiros[passageiro.id] = passageiro

    def buscar(self, cpf):
        return self.passageiros.get(cpf)

def test_deve_criar_passageiro():

    repository = FakePassageiroRepository()
    service = PassageiroService(repository)

    passageiro = service.criar_passageiro(nome="João", cpf="12345678900")

    assert passageiro.nome == "João"
    assert passageiro.cpf == "12345678900"