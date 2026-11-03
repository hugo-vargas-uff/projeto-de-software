def test_deve_criar_passageiro(client):

    response = client.post("/passageiros", json={"nome": "João", "cpf": "717.774.400-25"})

    assert response.status_code == 201

    body = response.get_json()

    assert "id" in body
    assert body["nome"] == "João"
    assert body["cpf"] == "71777440025"

def test_nao_deve_criar_passageiro_com_cpf_existente(client):

    client.post("/passageiros",json={"nome": "João", "cpf": "717.774.400-25"})

    response = client.post("/passageiros",json={"nome": "Pedro", "cpf": "717.774.400-25"})

    assert response.status_code == 409

    body = response.get_json()

    assert body["mensagem"] == (
        "Já existe um passageiro cadastrado com este CPF."
    )

def test_deve_buscar_passageiro(client):

    response_criacao = client.post("/passageiros",json={"nome": "João","cpf": "717.774.400-25"})

    assert response_criacao.status_code == 201

    passageiro_criado = response_criacao.get_json()

    response = client.get("/passageiros/717.774.400-25")

    assert response.status_code == 200

    body = response.get_json()

    assert body["id"] == passageiro_criado["id"]
    assert body["nome"] == "João"
    assert body["cpf"] == "71777440025"

def test_deve_retornar_404_quando_passageiro_nao_existir(client):

    response = client.get("/passageiros/717.774.400-25")

    assert response.status_code == 404

    body = response.get_json()

    assert body["mensagem"] == "Passageiro nao encontrado"

def test_deve_retornar_400_quando_cpf_tiver_menos_de_11_digitos(client):
    resposta = client.post("/passageiros",json={
            "nome": "João",
            "cpf": "123456789"
        }
    )

    assert resposta.status_code == 400
    assert resposta.json["erro"] == "CPF deve possuir 11 dígitos."

def test_deve_retornar_400_quando_cpf_tiver_digitos_iguais(client):
    resposta = client.post("/passageiros", json={
            "nome": "João",
            "cpf": "11111111111"
        }
    )

    assert resposta.status_code == 400
    assert resposta.json["erro"] == "CPF inválido."