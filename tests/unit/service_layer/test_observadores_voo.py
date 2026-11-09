import pytest

from airline.domain.model import ErroRegraVoo
from airline.service_layer.observadores_voo import ObservadorDeVoo
from test_voo_service import montar_servico, novo_voo

class ObservadorEspiao(ObservadorDeVoo):
    def __init__(self):
        self.voos_cancelados = []

    def voo_cancelado(self, numero_voo):
        self.voos_cancelados.append(numero_voo)

def test_cancelar_voo_avisa_todos_os_observadores():
    servico, voos, aeronaves, session = montar_servico()
    voos.salvar(novo_voo("MV-100"))
    primeiro, segundo = ObservadorEspiao(), ObservadorEspiao()
    servico.inscrever(primeiro)
    servico.inscrever(segundo)

    servico.cancelar_voo("MV-100")

    assert primeiro.voos_cancelados == ["MV-100"]
    assert segundo.voos_cancelados == ["MV-100"]

def test_cancelamento_recusado_nao_avisa_ninguem():
    servico, voos, aeronaves, session = montar_servico()
    voo = novo_voo("MV-100")
    voo.realizar()
    voos.salvar(voo)
    espiao = ObservadorEspiao()
    servico.inscrever(espiao)

    #voo realizado nao pode ser cancelado, entao nao ha o que avisar
    with pytest.raises(ErroRegraVoo):
        servico.cancelar_voo("MV-100")

    assert espiao.voos_cancelados == []
