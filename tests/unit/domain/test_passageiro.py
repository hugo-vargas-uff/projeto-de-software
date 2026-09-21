from airline.domain.model import Passageiro

def test_deve_criar_passageiro():
    passageiro = Passageiro("Pedro Paulo", "637.678.520-47")

    assert passageiro.nome == "Pedro Paulo"
    assert passageiro.cpf == "637.678.520-47"