import uuid
import pytest
from airline.domain.model import Escala, ErroRegraTripulacao


def test_deve_criar_escala_vazia_para_um_voo():
    voo_id = "MV-2019"
    escala = Escala(voo_id=voo_id)

    assert escala.voo_id == "MV-2019"
    assert escala.tripulantes_ids == []
    assert escala.total_tripulantes() == 0


def test_deve_adicionar_tripulante_na_escala():
    escala = Escala(voo_id="MV-2019")
    tripulante_id = uuid.uuid4()

    escala.adicionar_tripulante(tripulante_id)

    assert escala.total_tripulantes() == 1
    assert tripulante_id in escala.tripulantes_ids


def test_erro_ao_adicionar_tripulante_duplicado_na_mesma_escala():
    escala = Escala(voo_id="MV-2019")
    tripulante_id = uuid.uuid4()

    escala.adicionar_tripulante(tripulante_id)

    with pytest.raises(ErroRegraTripulacao, match="Tripulante ja escalado para este voo"):
        escala.adicionar_tripulante(tripulante_id)

    assert escala.total_tripulantes() == 1


def test_deve_remover_tripulante_da_escala():
    escala = Escala(voo_id="MV-2019")
    tripulante_id = uuid.uuid4()

    escala.adicionar_tripulante(tripulante_id)
    assert escala.total_tripulantes() == 1

    escala.remover_tripulante(tripulante_id)
    assert escala.total_tripulantes() == 0


# --- Testes do Padrão GoF State (Ciclo de Vida da Escala)

def test_escala_inicia_no_estado_aberta():
    escala = Escala(voo_id="MV-2019")
    assert escala.estado == "ABERTA"


def test_nao_deve_confirmar_escala_sem_tripulantes():
    escala = Escala(voo_id="MV-2019")
    with pytest.raises(ErroRegraTripulacao, match="Nao e possivel confirmar uma escala sem tripulantes"):
        escala.confirmar()


def test_escala_confirmada_bloqueia_adicao_e_remocao_de_tripulantes():
    escala = Escala(voo_id="MV-2019")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    escala.adicionar_tripulante(t1)
    escala.confirmar()
    assert escala.estado == "CONFIRMADA"

    with pytest.raises(ErroRegraTripulacao, match="Nao e permitido alterar uma escala confirmada"):
        escala.adicionar_tripulante(t2)

    with pytest.raises(ErroRegraTripulacao, match="Nao e permitido alterar uma escala confirmada"):
        escala.remover_tripulante(t1)


def test_escala_confirmada_pode_ser_reaberta_para_edicao():
    escala = Escala(voo_id="MV-2019")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    escala.adicionar_tripulante(t1)
    escala.confirmar()

    escala.reabrir()
    assert escala.estado == "ABERTA"
    escala.adicionar_tripulante(t2)
    assert escala.total_tripulantes() == 2


def test_escala_realizada_bloqueia_qualquer_alteracao_e_imutabilidade():
    escala = Escala(voo_id="MV-2019")
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    escala.adicionar_tripulante(t1)
    escala.confirmar()
    escala.realizar()
    assert escala.estado == "REALIZADA"

    with pytest.raises(ErroRegraTripulacao, match="Nao e permitido alterar uma escala de voo ja realizado"):
        escala.adicionar_tripulante(t2)

    with pytest.raises(ErroRegraTripulacao, match="Nao e permitido alterar uma escala de voo ja realizado"):
        escala.remover_tripulante(t1)

    with pytest.raises(ErroRegraTripulacao, match="Nao e possivel reabrir uma escala de voo ja realizado"):
        escala.reabrir()


def test_escala_aberta_nao_pode_ser_realizada_diretamente():
    escala = Escala(voo_id="MV-2019")
    escala.adicionar_tripulante(uuid.uuid4())
    with pytest.raises(ErroRegraTripulacao, match="So e possivel realizar uma escala previamente confirmada"):
        escala.realizar()
