from abc import ABC, abstractmethod
from airline.domain.model import Reserva, Passageiro

class ReservaRepository(ABC):

    @abstractmethod
    def salvar(self, reserva: Reserva) -> None:
        pass

    @abstractmethod
    def buscar(self, reserva_id):
        pass

    @abstractmethod
    def contar_reservas_por_voo(self, voo_id):
        pass


class PassageiroRepository(ABC):

    @abstractmethod
    def salvar(self, passageiro: Passageiro) -> None:
        pass

    @abstractmethod
    def buscar(self, passageiro_id):
        pass