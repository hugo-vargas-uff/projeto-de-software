from datetime import date

from airline.domain.model import Aeronave
from airline.adapters.repository import SqlAlchemyAeronaveRepository
from airline.entrypoints.flask_app import SessionFactory

def criar_aeronave_teste():
    session = SessionFactory()

    aeronave = Aeronave(
        prefixo="PT-ABC",
        modelo="Boeing 737",
        capacidade=180,
        validade_vistoria=date(2030, 12, 31)
    )

    repository = SqlAlchemyAeronaveRepository(session)
    repository.salvar(aeronave)

    session.close()

def test_deve_criar_reserva(client):

    # cria passageiro
    response_passageiro = client.post("/passageiros", json={"nome": "João","cpf": "717.774.400-25"})

    assert response_passageiro.status_code == 201

    passageiro = response_passageiro.get_json()

    criar_aeronave_teste()

    # cria voo
    response_voo = client.post("/voos", json={
            "numero_voo": "LA123",
            "origem": "GIG",
            "destino": "GRU",
            "aeronave": "PT-ABC"
        })

    assert response_voo.status_code == 201

    # cria reserva
    response = client.post("/reservas",json={"voo_id": "LA123","passageiro_id": passageiro["id"]})

    assert response.status_code == 201

    body = response.get_json()

    assert body["voo_id"] == "LA123"
    assert body["passageiro_id"] == passageiro["id"]
    assert body["status"] == "CONFIRMADA"

def test_deve_buscar_reserva(client):

    # passageiro
    response_passageiro = client.post("/passageiros",json={"nome": "João","cpf": "717.774.400-25"})

    passageiro = response_passageiro.get_json()

    criar_aeronave_teste()

    # voo
    response_voo = client.post("/voos",json={
            "numero_voo": "LA123",
            "origem": "GIG",
            "destino": "GRU",
            "aeronave": "PT-ABC"
    })

    assert response_voo.status_code == 201

    # reserva
    response_reserva = client.post("/reservas",json={"voo_id": "LA123","passageiro_id": passageiro["id"]})

    assert response_reserva.status_code == 201

    # busca
    response = client.get(f"/reservas/LA123/{passageiro['id']}")

    assert response.status_code == 200

    body = response.get_json()

    assert body["voo_id"] == "LA123"
    assert body["passageiro_id"] == passageiro["id"]
    assert body["status"] == "CONFIRMADA"

def test_deve_retornar_404_quando_reserva_nao_existir(client):

    # cria passageiro
    response_passageiro = client.post("/passageiros",json={"nome": "João","cpf": "717.774.400-25"})

    passageiro = response_passageiro.get_json()

    criar_aeronave_teste()

    # cria voo
    response_voo = client.post("/voos",json={
            "numero_voo": "LA123",
            "origem": "GIG",
            "destino": "GRU",
            "aeronave": "PT-ABC"
        })

    assert response_voo.status_code == 201

    # não cria reserva

    response = client.get(f"/reservas/LA123/{passageiro['id']}")

    assert response.status_code == 404

    body = response.get_json()

    assert body["mensagem"] == "Reserva nao encontrada"

def test_nao_deve_criar_reserva_com_passageiro_inexistente(client):

    criar_aeronave_teste()

    # cria voo
    response_voo = client.post("/voos",json={
            "numero_voo": "LA123",
            "origem": "GIG",
            "destino": "GRU",
            "aeronave": "PT-ABC"
        })

    assert response_voo.status_code == 201

    response = client.post("/reservas",json={"voo_id": "LA123","passageiro_id": "00000000-0000-0000-0000-000000000000"})

    assert response.status_code == 404

    body = response.get_json()

    assert body["mensagem"] == "Passageiro nao encontrado"

def test_nao_deve_criar_reserva_com_voo_inexistente(client):

    response_passageiro = client.post("/passageiros",json={"nome": "João","cpf": "717.774.400-25"})

    assert response_passageiro.status_code == 201

    passageiro = response_passageiro.get_json()

    response = client.post("/reservas",json={"voo_id": "VOO-INEXISTENTE","passageiro_id": passageiro["id"]})

    assert response.status_code == 404

    body = response.get_json()

    assert body["mensagem"] == "Voo nao encontrado"