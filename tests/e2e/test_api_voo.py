from datetime import date, timedelta

from airline.adapters.repository import SqlAlchemyAeronaveRepository
from airline.domain.model import Aeronave


def cadastrar_aeronave(session_factory, prefixo="PR-400", capacidade=150):
    session = session_factory()
    
    aeronave = Aeronave( prefixo=prefixo, modelo="Airbus A320",
        capacidade=capacidade, validade_vistoria=date.today() + timedelta(days=365),
    )
    
    SqlAlchemyAeronaveRepository(session).salvar(aeronave)
    session.commit()  # salva mesmo se o repo da aeronave não der commit
    session.close()


def agendar(client, numero_voo):
    return client.post("/voos", json={
        "numero_voo": numero_voo,
        "origem": "GRU",
        "destino": "GIG",
        "aeronave": "PR-400",
    })


def test_agendar_e_consultar_voo_pela_api(client, session_factory):
    cadastrar_aeronave(session_factory, capacidade=150)

    resposta = agendar(client, "MV-100")
    assert resposta.status_code == 201
    assert resposta.get_json()["numero_voo"] == "MV-100"

    resposta = client.get("/voos/MV-100")
    assert resposta.status_code == 200
    
    dados = resposta.get_json()
    assert dados["origem"] == "GRU"
    assert dados["destino"] == "GIG"
    assert dados["assentos_disponiveis"] == 150
    assert dados["status"] == "AGENDADO"
