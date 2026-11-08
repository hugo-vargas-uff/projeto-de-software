"""
Trava o comportamento atual de Aeronave.esta_disponivel antes da refatoracao
para o padrao Strategy (checkpoint 3).

A tabela cobre as combinacoes de vistoria e ordens de manutencao. Os valores
esperados estao escritos a mao, e nao calculados pela mesma logica do codigo,
para que um erro na refatoracao nao passe despercebido.
"""
from datetime import date

import pytest

from airline.domain.model import Aeronave

HOJE = date(2026, 11, 8)

VISTORIA_VALIDA = date(2026, 12, 31)
VISTORIA_NO_ULTIMO_DIA = HOJE
VISTORIA_VENCIDA = date(2026, 11, 7)


def aeronave_com(validade_vistoria, ordens):
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=validade_vistoria,
    )
    for numero, situacao in enumerate(ordens, start=1):
        ordem = aeronave.abrir_ordem_manutencao(f"Ordem {numero}")
        if situacao == "concluida":
            aeronave.concluir_ordem_manutencao(ordem)
    return aeronave


@pytest.mark.parametrize(
    "validade_vistoria, ordens, esperado",
    [
        (VISTORIA_VALIDA, [], True),
        (VISTORIA_VALIDA, ["pendente"], False),
        (VISTORIA_VALIDA, ["concluida"], True),
        (VISTORIA_VALIDA, ["concluida", "pendente"], False),
        (VISTORIA_NO_ULTIMO_DIA, [], True),
        (VISTORIA_VENCIDA, [], False),
        (VISTORIA_VENCIDA, ["concluida"], False),
        (VISTORIA_VENCIDA, ["pendente"], False),
    ],
    ids=[
        "vistoria valida, sem ordens",
        "vistoria valida, ordem pendente",
        "vistoria valida, ordem concluida",
        "vistoria valida, uma concluida e uma pendente",
        "vistoria vence hoje, sem ordens",
        "vistoria vencida, sem ordens",
        "vistoria vencida, ordem concluida",
        "vistoria vencida, ordem pendente",
    ],
)
def test_disponibilidade_por_combinacao_de_vistoria_e_ordens(
    validade_vistoria, ordens, esperado
):
    aeronave = aeronave_com(validade_vistoria, ordens)

    assert aeronave.esta_disponivel(HOJE) is esperado
