"""
Testes do padrao Strategy aplicado a disponibilidade da Aeronave.

Cada regra e uma estrategia: recebe a aeronave e a data e responde se permite
o voo. A Aeronave (contexto) aplica todas as regras da sua lista.
"""
from datetime import date

from airline.domain.model import (
    Aeronave,
    RegraDisponibilidade,
    SemManutencaoPendente,
    VistoriaValida,
)

HOJE = date(2026, 11, 9)


def nova_aeronave(validade_vistoria=date(2026, 12, 31), **extras):
    return Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=validade_vistoria,
        **extras,
    )


# --- VistoriaValida

def test_vistoria_valida_permite_voo_com_vistoria_em_dia():
    aeronave = nova_aeronave(validade_vistoria=date(2026, 12, 31))

    assert VistoriaValida().permite_voo(aeronave, HOJE) is True


def test_vistoria_valida_permite_voo_no_ultimo_dia_da_validade():
    aeronave = nova_aeronave(validade_vistoria=HOJE)

    assert VistoriaValida().permite_voo(aeronave, HOJE) is True


def test_vistoria_valida_nega_voo_com_vistoria_vencida():
    aeronave = nova_aeronave(validade_vistoria=date(2026, 11, 8))

    assert VistoriaValida().permite_voo(aeronave, HOJE) is False


# --- SemManutencaoPendente

def test_sem_manutencao_pendente_permite_voo_sem_ordens():
    assert SemManutencaoPendente().permite_voo(nova_aeronave(), HOJE) is True


def test_sem_manutencao_pendente_nega_voo_com_ordem_pendente():
    aeronave = nova_aeronave()
    aeronave.abrir_ordem_manutencao("Revisao do motor")

    assert SemManutencaoPendente().permite_voo(aeronave, HOJE) is False


def test_sem_manutencao_pendente_permite_voo_com_ordem_concluida():
    aeronave = nova_aeronave()
    ordem = aeronave.abrir_ordem_manutencao("Revisao do motor")
    aeronave.concluir_ordem_manutencao(ordem)

    assert SemManutencaoPendente().permite_voo(aeronave, HOJE) is True


# --- as regras sao estrategias intercambiaveis

def test_as_regras_concretas_sao_estrategias_de_disponibilidade():
    assert isinstance(VistoriaValida(), RegraDisponibilidade)
    assert isinstance(SemManutencaoPendente(), RegraDisponibilidade)


# --- a Aeronave (contexto) aplica as regras da sua lista

def test_aeronave_usa_por_padrao_vistoria_valida_e_sem_manutencao_pendente():
    aeronave = nova_aeronave()

    tipos = [type(regra) for regra in aeronave.regras]

    assert tipos == [VistoriaValida, SemManutencaoPendente]


def test_aeronave_so_esta_disponivel_quando_todas_as_regras_permitem():
    aeronave = nova_aeronave(validade_vistoria=date(2026, 11, 8))

    # a vistoria venceu, mesmo sem nenhuma ordem pendente
    assert aeronave.esta_disponivel(HOJE) is False
