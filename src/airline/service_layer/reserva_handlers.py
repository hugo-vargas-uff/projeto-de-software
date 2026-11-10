from abc import ABC, abstractmethod

from airline.domain.exception import (
    PassageiroNaoEncontrado,
    VooNaoEncontrado
)


class ReservaValidationHandler(ABC):
    def __init__(self):
        self._proximo = None

    def definir_proximo(self, handler):
        self._proximo = handler
        return handler

    def validar_proximo(self, voo_id, passageiro_id):
        if self._proximo is not None:
            self._proximo.validar(voo_id, passageiro_id)

    @abstractmethod
    def validar(self, voo_id, passageiro_id):
        pass


class VerificarPassageiroHandler(ReservaValidationHandler):
    def __init__(self, passageiro_repository):
        super().__init__()
        self.passageiro_repository = passageiro_repository

    def validar(self, voo_id, passageiro_id):
        passageiro = self.passageiro_repository.buscar_por_id(passageiro_id)

        if passageiro is None:
            raise PassageiroNaoEncontrado("Passageiro nao encontrado")

        self.validar_proximo(voo_id, passageiro_id)


class VerificarVooHandler(ReservaValidationHandler):
    def __init__(self, voo_repository):
        super().__init__()
        self.voo_repository = voo_repository

    def validar(self, voo_id, passageiro_id):
        voo = self.voo_repository.buscar(voo_id)

        if voo is None:
            raise VooNaoEncontrado("Voo nao encontrado")

        self.validar_proximo(voo_id, passageiro_id)
