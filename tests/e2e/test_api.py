import uuid
import pytest
from airline.entrypoints.flask_app import app, engine
from airline.adapters.orm import Base


@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Limpa e recria o banco para cada teste rodar isolado e limpo
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with app.test_client() as client:
        yield client


def test_api_deve_cadastrar_tripulante(client):
    response = client.post("/tripulantes", json={
        "nome": "Fernando Dias",
        "cargo": "PILOTO",
        "teto_horas": 85.0
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["nome"] == "Fernando Dias"
    assert data["cargo"] == "PILOTO"
    assert "id" in data


def test_api_deve_escalar_tripulante_para_voo(client):
    # Cadastra o tripulante primeiro
    resp_t = client.post("/tripulantes", json={
        "nome": "Beatriz Lima",
        "cargo": "COPILOTO",
        "teto_horas": 85.0
    })
    tripulante_id = resp_t.get_json()["id"]

    # Faz o escalonamento para o voo
    response = client.post("/escalas", json={
        "voo_id": "MV-3000",
        "tripulante_id": tripulante_id,
        "duracao_horas_voo": 4.5
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["voo_id"] == "MV-3000"
    assert data["total_tripulantes"] == 1


def test_api_erro_ao_escalar_com_horas_acima_do_teto(client):
    resp_t = client.post("/tripulantes", json={
        "nome": "Marcos Paulo",
        "cargo": "PILOTO",
        "teto_horas": 10.0
    })
    tripulante_id = resp_t.get_json()["id"]

    # Voo de 12 horas estourando o teto de 10h
    response = client.post("/escalas", json={
        "voo_id": "MV-4000",
        "tripulante_id": tripulante_id,
        "duracao_horas_voo": 12.0
    })

    assert response.status_code == 400
    assert "Teto regulamentar de horas ultrapassado" in response.get_json()["mensagem"]