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