from abc import ABC, abstractmethod
from airline.domain.model import Reserva, Passageiro, Aeronave, Voo


class ReservaRepository(ABC):

    @abstractmethod
    def salvar(self, reserva: Reserva) -> None:
        pass

    @abstractmethod
    def buscar(self, voo_id, passageiro_id):
        pass

    @abstractmethod
    def contar_reservas_por_voo(self, voo_id):
        pass


class PassageiroRepository(ABC):

    @abstractmethod
    def salvar(self, passageiro: Passageiro) -> None:
        pass

    @abstractmethod
    def buscar_por_id(self, passageiro_id):
        pass

    @abstractmethod
    def buscar_por_cpf(self, cpf):
        pass


class AeronaveRepository(ABC):

    @abstractmethod
    def salvar(self, aeronave: Aeronave) -> None:
        pass

    @abstractmethod
    def buscar(self, prefixo: str):
        pass


class VooRepository(ABC):

    @abstractmethod
    def salvar(self, voo: Voo) -> None:
        pass

    @abstractmethod
    def buscar(self, numero_voo: str):
        pass




from airline.domain.model import Tripulante, Escala


class TripulanteRepository(ABC):

    @abstractmethod
    def salvar(self, tripulante: Tripulante) -> None:
        pass

    @abstractmethod
    def buscar_por_id(self, tripulante_id) -> Tripulante:
        pass


class EscalaRepository(ABC):

    @abstractmethod
    def salvar(self, escala: Escala) -> None:
        pass

    @abstractmethod
    def buscar_por_voo(self, voo_id: str) -> Escala:
        pass


from airline.domain.model import Despacho


class DespachoRepository(ABC):

    @abstractmethod
    def salvar(self, despacho: Despacho) -> None:
        pass

    @abstractmethod
    def buscar_por_id(self, despacho_id):
        pass

    @abstractmethod
    def buscar_por_voo(self, voo_id: str):
        pass
