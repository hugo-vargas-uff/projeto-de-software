from abc import ABC, abstractmethod
from airline.domain.model import StatusReserva

class ObservadorDeVoo(ABC):
    #o VooService chama este metodo sempre que um voo e cancelado
    @abstractmethod
    def voo_cancelado(self, numero_voo: str) -> None:
        pass

class CancelaReservasDoVoo(ObservadorDeVoo):
    #cancela as reservas confirmadas do voo que foi cancelado
    def __init__(self, reserva_repository):
        self.reserva_repository = reserva_repository

    def voo_cancelado(self, numero_voo):
        for reserva in self.reserva_repository.listar_por_voo(numero_voo):
            if reserva.status == StatusReserva.CONFIRMADA:
                reserva.cancelar()
                self.reserva_repository.salvar(reserva)
