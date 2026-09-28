import pytest
from airline.domain.model import Passageiro
from airline.service_layer.services import PassageiroService
from airline.service_layer.services import PassageiroRepository
from airline.domain.exception import CpfJaCadastradoException

class FakePassageiroRepository(PassageiroRepository):

    def __init__(self):
        self.passageiros_id = {}
        self.passageiros_cpf = {}

    def salvar(self, passageiro: Passageiro) -> None:
        self.passageiros_id[passageiro.id] = passageiro
        self.passageiros_cpf[passageiro.cpf] = passageiro.cpf

    def buscar_por_id(self, passageiro_id):
        return self.passageiros_id.get(passageiro_id)

    def buscar_por_cpf(self, cpf):
        return self.passageiros_cpf.get(cpf)

def test_deve_criar_passageiro():

    repository = FakePassageiroRepository()
    service = PassageiroService(repository)

    passageiro = service.criar_passageiro(nome="João", cpf="12345678900")

    assert passageiro.nome == "João"
    assert passageiro.cpf == "12345678900"

def test_nao_deve_criar_passageiro_com_cpf_existente():

    repository = FakePassageiroRepository()
    service = PassageiroService(repository)

    service.criar_passageiro(nome="Pedro",cpf="717.774.400-25")

    with pytest.raises(CpfJaCadastradoException, match="Já existe um passageiro cadastrado com este CPF."):
        service.criar_passageiro(nome="João",cpf="717.774.400-25")