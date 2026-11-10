import pytest
from unittest.mock import Mock

from airline.domain.exception import (
    PassageiroNaoEncontrado,
    VooNaoEncontrado
)

from airline.service_layer.reserva_handlers import (
    VerificarPassageiroHandler,
    VerificarVooHandler
)


def criar_cadeia(passageiro_repository, voo_repository):
    passageiro_handler = VerificarPassageiroHandler(passageiro_repository)

    voo_handler = VerificarVooHandler(voo_repository)

    passageiro_handler.definir_proximo(voo_handler)

    return passageiro_handler


def test_deve_executar_todos_os_handlers_quando_referencias_existirem():
    passageiro_repository = Mock()
    voo_repository = Mock()

    passageiro_repository.buscar_por_id.return_value = object()
    voo_repository.buscar.return_value = object()

    cadeia = criar_cadeia(passageiro_repository,voo_repository)

    cadeia.validar("voo-1", "passageiro-1")

    passageiro_repository.buscar_por_id.assert_called_once_with("passageiro-1")

    voo_repository.buscar.assert_called_once_with("voo-1")


def test_nao_deve_continuar_cadeia_quando_passageiro_nao_existir():
    passageiro_repository = Mock()
    voo_repository = Mock()

    passageiro_repository.buscar_por_id.return_value = None

    cadeia = criar_cadeia(
        passageiro_repository,
        voo_repository
    )

    with pytest.raises(PassageiroNaoEncontrado):
        cadeia.validar("voo-1", "passageiro-1")

    voo_repository.buscar.assert_not_called()


def test_deve_interromper_cadeia_quando_voo_nao_existir():
    passageiro_repository = Mock()
    voo_repository = Mock()

    passageiro_repository.buscar_por_id.return_value = object()
    voo_repository.buscar.return_value = None

    cadeia = criar_cadeia(
        passageiro_repository,
        voo_repository
    )

    with pytest.raises(VooNaoEncontrado):
        cadeia.validar("voo-1", "passageiro-1")

    passageiro_repository.buscar_por_id.assert_called_once()
    voo_repository.buscar.assert_called_once()
