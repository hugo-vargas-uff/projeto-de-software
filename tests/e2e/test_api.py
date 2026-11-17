import uuid
import pytest
from sqlalchemy import text
from airline.entrypoints.flask_app import app, engine, SessionFactory
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


def gravar_voo_agendado(numero_voo="MV-3000"):
    # o despacho agora so abre para voo agendado; o voo e gravado direto na tabela
    session = SessionFactory()
    session.execute(text("""
        INSERT INTO voos (numero_voo, origem, destino, aeronave_id, assentos_disponiveis, status)
        VALUES (:numero, 'GRU', 'GIG', 'PR-400', 150, 'AGENDADO')
    """), {"numero": numero_voo})
    session.commit()
    session.close()


def test_api_deve_abrir_despacho(client):
    gravar_voo_agendado()
    response = client.post("/despachos", json={
        "voo_id": "MV-3000",
        "carga_maxima": 1000
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["voo_id"] == "MV-3000"
    assert data["carga_maxima"] == 1000
    assert data["peso_total"] == 0
    assert "id" in data


def test_api_erro_ao_abrir_dois_despachos_para_o_mesmo_voo(client):
    gravar_voo_agendado()
    client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 1000})

    response = client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 500})

    assert response.status_code == 400
    assert "Ja existe um despacho aberto para este voo" in response.get_json()["mensagem"]


def test_api_deve_adicionar_volume_no_despacho(client):
    gravar_voo_agendado()
    resp_d = client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 1000})
    despacho_id = resp_d.get_json()["id"]

    response = client.post(f"/despachos/{despacho_id}/volumes", json={"peso": 150})

    assert response.status_code == 201
    data = response.get_json()
    assert data["peso_total"] == 150
    assert data["peso_disponivel"] == 850


def test_api_erro_ao_adicionar_volume_acima_da_carga_maxima(client):
    gravar_voo_agendado()
    resp_d = client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 1000})
    despacho_id = resp_d.get_json()["id"]

    client.post(f"/despachos/{despacho_id}/volumes", json={"peso": 900})
    response = client.post(f"/despachos/{despacho_id}/volumes", json={"peso": 200})

    assert response.status_code == 400
    assert "ultrapassa a carga maxima do despacho" in response.get_json()["mensagem"]


def test_api_erro_ao_adicionar_volume_em_despacho_inexistente(client):
    response = client.post(f"/despachos/{uuid.uuid4()}/volumes", json={"peso": 100})

    assert response.status_code == 404


def test_api_deve_consultar_despacho(client):
    gravar_voo_agendado()
    resp_d = client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 1000})
    despacho_id = resp_d.get_json()["id"]
    client.post(f"/despachos/{despacho_id}/volumes", json={"peso": 100})
    client.post(f"/despachos/{despacho_id}/volumes", json={"peso": 250})

    response = client.get(f"/despachos/{despacho_id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == despacho_id
    assert data["voo_id"] == "MV-3000"
    assert data["volumes"] == [100, 250]
    assert data["peso_total"] == 350
    assert data["peso_disponivel"] == 650


def test_api_erro_ao_consultar_despacho_inexistente(client):
    response = client.get(f"/despachos/{uuid.uuid4()}")

    assert response.status_code == 404


def test_api_deve_adicionar_conteiner_no_despacho(client):
    gravar_voo_agendado()
    resp_d = client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 1000})
    despacho_id = resp_d.get_json()["id"]
    client.post(f"/despachos/{despacho_id}/volumes", json={"peso": 100})

    response = client.post(f"/despachos/{despacho_id}/conteineres", json={
        "codigo": "AKE12345AA",
        "tara": 80,
        "volumes": [23, 32]
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["peso_total"] == 235
    assert data["quantidade_volumes"] == 3

    consulta = client.get(f"/despachos/{despacho_id}").get_json()
    assert consulta["volumes"] == [100, 135]
    assert consulta["peso_disponivel"] == 765


def test_api_erro_quando_tara_do_conteiner_passa_da_carga_maxima(client):
    gravar_voo_agendado()
    resp_d = client.post("/despachos", json={"voo_id": "MV-3000", "carga_maxima": 200})
    despacho_id = resp_d.get_json()["id"]

    response = client.post(f"/despachos/{despacho_id}/conteineres", json={
        "codigo": "AKE12345AA",
        "tara": 80,
        "volumes": [100, 50]
    })

    assert response.status_code == 400
    assert "ultrapassa a carga maxima do despacho" in response.get_json()["mensagem"]


def test_api_erro_ao_abrir_despacho_para_voo_inexistente(client):
    response = client.post("/despachos", json={"voo_id": "XX-999", "carga_maxima": 1000})

    assert response.status_code == 400
    assert "nao esta agendado" in response.get_json()["mensagem"]
