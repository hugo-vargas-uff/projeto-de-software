def test_deve_cadastrar_aeronave(client):
    response = client.post("/aeronaves", json={
        "prefixo": "PT-MVA",
        "modelo": "Boeing 737",
        "capacidade": 180,
        "validade_vistoria": "2026-12-31"
    })

    assert response.status_code == 201

    body = response.get_json()

    assert body["prefixo"] == "PT-MVA"
    assert body["modelo"] == "Boeing 737"
    assert body["capacidade"] == 180
    assert body["validade_vistoria"] == "2026-12-31"


def test_deve_consultar_aeronave_disponivel(client):
    client.post("/aeronaves", json={
        "prefixo": "PT-MVA",
        "modelo": "Boeing 737",
        "capacidade": 180,
        "validade_vistoria": "2026-12-31"
    })

    response = client.get(
        "/aeronaves/PT-MVA/disponibilidade"
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["prefixo"] == "PT-MVA"
    assert body["disponivel"] is True


def test_deve_retornar_404_quando_aeronave_nao_existir(client):
    response = client.get(
        "/aeronaves/NAO-EXISTE/disponibilidade"
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body["erro"] == "Aeronave nao encontrada"