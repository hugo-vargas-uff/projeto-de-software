from airline.domain.exception import CpfInvalidoException
from airline.domain.model import Passageiro, CPF
import pytest

def test_deve_criar_passageiro():
    passageiro = Passageiro("Pedro Paulo", CPF("637.678.520-47"))

    assert passageiro.nome == "Pedro Paulo"
    assert passageiro.cpf.valor == "63767852047"


def test_deve_normalizar_cpf():
    cpf = CPF("637.678.520-47")

    assert cpf.valor == "63767852047"


def test_deve_rejeitar_cpf_com_quantidade_incorreta_de_digitos():
    with pytest.raises(CpfInvalidoException):
        CPF("123456")


def test_deve_rejeitar_cpf_com_digitos_repetidos():
    with pytest.raises(CpfInvalidoException):
        CPF("111.111.111-11")