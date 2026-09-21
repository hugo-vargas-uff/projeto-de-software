from airline.domain.model import Aeronave
from datetime import date
from airline.domain.model import OrdemManutencao, StatusOrdemManutencao

def test_deve_criar_aeronave():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    assert aeronave.prefixo == "PT-MVA"
    assert aeronave.modelo == "Boeing 737"
    assert aeronave.capacidade == 180


def test_igualdade_de_aeronaves():
    aeronave1 = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    aeronave2 = Aeronave(
        prefixo="PT-MVA",
        modelo="Airbus A320",
        capacidade=200,
        validade_vistoria=date(2026, 12, 31)
    )

    assert aeronave1 == aeronave2


def test_aeronaves_diferentes():
    aeronave1 = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    aeronave2 = Aeronave(
        prefixo="PT-MVB",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    assert aeronave1 != aeronave2


def test_aeronaves_com_mesmo_prefixo_tem_mesmo_hash():
    aeronave1 = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    aeronave2 = Aeronave(
        prefixo="PT-MVA",
        modelo="Airbus A320",
        capacidade=200,
        validade_vistoria=date(2026, 12, 31)
    )

    assert hash(aeronave1) == hash(aeronave2)


def test_aeronave_com_vistoria_vencida_fica_indisponivel():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 9, 20)
    )

    hoje = date(2026, 9, 21)

    assert aeronave.esta_disponivel(hoje) is False


def test_aeronave_disponivel_no_ultimo_dia_da_vistoria():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 9, 21)
    )

    hoje = date(2026, 9, 21)

    assert aeronave.esta_disponivel(hoje) is True







#-------Ordem Manutenção

def test_deve_criar_ordem_manutencao_pendente():
    ordem = OrdemManutencao(
        descricao="Troca do trem de pouso"
    )

    assert ordem.descricao == "Troca do trem de pouso"
    assert ordem.status == StatusOrdemManutencao.PENDENTE


def test_deve_concluir_ordem_manutencao():
    ordem = OrdemManutencao(
        descricao="Troca do trem de pouso"
    )

    ordem.concluir()

    assert ordem.status == StatusOrdemManutencao.CONCLUIDA


def test_aeronave_com_ordem_pendente_fica_indisponivel():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    hoje = date(2026, 9, 21)

    aeronave.abrir_ordem_manutencao("Troca do trem de pouso")

    assert aeronave.esta_disponivel(hoje) is False


def test_aeronave_volta_a_ficar_disponivel_apos_concluir_ordem():
    aeronave = Aeronave(
        prefixo="PT-MVA",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2026, 12, 31)
    )

    hoje = date(2026, 9, 21)

    ordem = aeronave.abrir_ordem_manutencao("Troca do trem de pouso")

    aeronave.concluir_ordem_manutencao(ordem)

    assert aeronave.esta_disponivel(hoje) is True