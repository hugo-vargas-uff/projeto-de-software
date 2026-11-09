from abc import ABC, abstractmethod

class ObservadorDeVoo(ABC):
    #o VooService chama este metodo sempre que um voo e cancelado

    @abstractmethod
    def voo_cancelado(self, numero_voo: str) -> None:
        pass
