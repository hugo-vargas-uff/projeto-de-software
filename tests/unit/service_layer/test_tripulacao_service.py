import uuid
from airline.domain.model import Tripulante, CargoTripulante, Escala
from airline.domain.repositories import TripulanteRepository, EscalaRepository


class FakeTripulanteRepository(TripulanteRepository):
    def __init__(self):
        self._tripulantes = {}

    def salvar(self, tripulante: Tripulante) -> None:
        self._tripulantes[tripulante.id] = tripulante

    def buscar_por_id(self, tripulante_id):
        return self._tripulantes.get(tripulante_id)


class FakeEscalaRepository(EscalaRepository):
    def __init__(self):
        self._escalas = {}

    def salvar(self, escala: Escala) -> None:
        self._escalas[escala.voo_id] = escala

    def buscar_por_voo(self, voo_id: str):
        return self._escalas.get(voo_id)


# --- Testes com os repositórios Fake

def test_fake_salvar_e_buscar_tripulante():
    repo = FakeTripulanteRepository()
    tripulante = Tripulante(
        nome="Mariana Costa",
        cargo=CargoTripulante.COPILOTO,
        teto_horas=80.0
    )

    repo.salvar(tripulante)
    recuperado = repo.buscar_por_id(tripulante.id)

    assert recuperado is not None
    assert recuperado.nome == "Mariana Costa"
    assert recuperado.cargo == CargoTripulante.COPILOTO


def test_fake_buscar_tripulante_inexistente_retorna_none():
    repo = FakeTripulanteRepository()
    id_qualquer = uuid.uuid4()

    assert repo.buscar_por_id(id_qualquer) is None


def test_fake_salvar_e_buscar_escala_por_voo():
    repo = FakeEscalaRepository()
    escala = Escala(voo_id="MV-2019")
    tripulante_id = uuid.uuid4()
    escala.adicionar_tripulante(tripulante_id)

    repo.salvar(escala)
    recuperada = repo.buscar_por_voo("MV-2019")

    assert recuperada is not None
    assert recuperada.voo_id == "MV-2019"
    assert tripulante_id in recuperada.tripulantes_ids


def test_fake_buscar_escala_inexistente_retorna_none():
    repo = FakeEscalaRepository()

    assert repo.buscar_por_voo("VOO-INEXISTENTE") is None



# --- Testes da Camada de Serviço (Casos de Uso)

from airline.service_layer.services import TripulanteService, EscalaService
from airline.domain.model import ErroRegraTripulacao
import pytest


def test_servico_deve_cadastrar_tripulante():
    repo = FakeTripulanteRepository()
    servico = TripulanteService(repo)

    tripulante = servico.cadastrar_tripulante(
        nome="Roberto Mendes",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )

    assert tripulante.id is not None
    assert repo.buscar_por_id(tripulante.id) == tripulante


def test_servico_deve_escalar_tripulante_com_sucesso():
    tripulante_repo = FakeTripulanteRepository()
    escala_repo = FakeEscalaRepository()

    tripulante = Tripulante(
        nome="Lucas Andrade",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )
    tripulante_repo.salvar(tripulante)

    servico = EscalaService(escala_repo=escala_repo, tripulante_repo=tripulante_repo)

    escala = servico.escalar_tripulante(
        voo_id="MV-2019",
        tripulante_id=tripulante.id,
        duracao_horas_voo=5.0
    )

    assert escala.total_tripulantes() == 1
    assert tripulante.horas_de_voo == 5.0


def test_servico_nao_deve_escalar_tripulante_se_estourar_teto_de_horas():
    tripulante_repo = FakeTripulanteRepository()
    escala_repo = FakeEscalaRepository()

    tripulante = Tripulante(
        nome="Lucas Andrade",
        cargo=CargoTripulante.PILOTO,
        teto_horas=85.0
    )
    tripulante.registrar_horas_de_voo(82.0)  # já tem 82h
    tripulante_repo.salvar(tripulante)

    servico = EscalaService(escala_repo=escala_repo, tripulante_repo=tripulante_repo)

    # Voo de 5h estouraria o teto de 85h
    with pytest.raises(ErroRegraTripulacao, match="Teto regulamentar de horas ultrapassado"):
        servico.escalar_tripulante(
            voo_id="MV-2019",
            tripulante_id=tripulante.id,
            duracao_horas_voo=5.0
        )

