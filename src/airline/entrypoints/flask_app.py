import uuid
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyTripulanteRepository, SqlAlchemyEscalaRepository
from airline.service_layer.services import TripulanteService, EscalaService
from airline.domain.model import CargoTripulante, ErroRegraTripulacao

from datetime import date
from airline.adapters.repository import SqlAlchemyVooRepository, SqlAlchemyAeronaveRepository
from airline.service_layer.services import VooService
from airline.domain.model import ErroRegraVoo
from airline.domain.exception import VooJaExiste, VooNaoEncontrado, AeronaveNaoEncontrada, AeronaveIndisponivel

app = Flask(__name__)

engine = create_engine("sqlite:///airline.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionFactory = sessionmaker(bind=engine)


@app.route("/tripulantes", methods=["POST"])
def cadastrar_tripulante():
    data = request.get_json()
    session = SessionFactory()
    repo = SqlAlchemyTripulanteRepository(session)
    service = TripulanteService(repo)

    cargo = CargoTripulante(data["cargo"])
    teto = float(data.get("teto_horas", 85.0))
    tripulante = service.cadastrar_tripulante(nome=data["nome"], cargo=cargo, teto_horas=teto)

    return jsonify({
        "id": str(tripulante.id),
        "nome": tripulante.nome,
        "cargo": tripulante.cargo.value,
        "teto_horas": tripulante.teto_horas,
        "horas_de_voo": tripulante.horas_de_voo
    }), 201


@app.route("/tripulantes/<tripulante_id>", methods=["GET"])
def buscar_tripulante(tripulante_id):
    session = SessionFactory()
    repo = SqlAlchemyTripulanteRepository(session)
    service = TripulanteService(repo)

    tripulante = service.buscar_por_id(uuid.UUID(tripulante_id))
    if tripulante is None:
        return jsonify({"mensagem": "Tripulante nao encontrado"}), 404

    return jsonify({
        "id": str(tripulante.id),
        "nome": tripulante.nome,
        "cargo": tripulante.cargo.value,
        "teto_horas": tripulante.teto_horas,
        "horas_de_voo": tripulante.horas_de_voo
    }), 200


@app.route("/escalas", methods=["POST"])
def escalar_tripulante():
    data = request.get_json()
    session = SessionFactory()
    escala_repo = SqlAlchemyEscalaRepository(session)
    tripulante_repo = SqlAlchemyTripulanteRepository(session)
    service = EscalaService(escala_repo=escala_repo, tripulante_repo=tripulante_repo)

    try:
        escala = service.escalar_tripulante(
            voo_id=data["voo_id"],
            tripulante_id=uuid.UUID(data["tripulante_id"]),
            duracao_horas_voo=float(data["duracao_horas_voo"])
        )
        return jsonify({
            "id": str(escala.id),
            "voo_id": escala.voo_id,
            "total_tripulantes": escala.total_tripulantes()
        }), 201
    except ErroRegraTripulacao as e:
        return jsonify({"mensagem": str(e)}), 400


@app.route("/escalas/<voo_id>", methods=["GET"])
def consultar_escala(voo_id):
    session = SessionFactory()
    escala_repo = SqlAlchemyEscalaRepository(session)
    service = EscalaService(escala_repo=escala_repo, tripulante_repo=SqlAlchemyTripulanteRepository(session))

    escala = service.consultar_escala(voo_id)
    if escala is None:
        return jsonify({"mensagem": "Escala nao encontrada"}), 404

    return jsonify({
        "id": str(escala.id),
        "voo_id": escala.voo_id,
        "tripulantes_ids": [str(t_id) for t_id in escala.tripulantes_ids]
    }), 200


# voo
def montar_voo_service(session):
    #liga as pecas reais: repositorios SQLAlchemy usando a mesma sessao que o servico vai confirmar
    return VooService(
        SqlAlchemyVooRepository(session),
        SqlAlchemyAeronaveRepository(session),
        session,
    )


@app.route("/voos", methods=["POST"])
def agendar_voo():
    dados = request.get_json()
    session = SessionFactory()
    try:
        numero_voo = montar_voo_service(session).agendar_voo(
            numero_voo=dados["numero_voo"],
            origem=dados["origem"],
            destino=dados["destino"],
            prefixo_aeronave=dados["aeronave"],
            hoje=date.today(),
        )
    except AeronaveNaoEncontrada as erro:
        return {"mensagem": str(erro)}, 404
    except (VooJaExiste, AeronaveIndisponivel) as erro:
        return {"mensagem": str(erro)}, 400
    finally:
        session.close()  #roda sempre, com ou sem erro

    return {"numero_voo": numero_voo}, 201


@app.route("/voos/<numero_voo>", methods=["GET"])
def consultar_voo(numero_voo):
    session = SessionFactory()
    try:
        voo = montar_voo_service(session).consultar_voo(numero_voo)
    except VooNaoEncontrado as erro:
        return {"mensagem": str(erro)}, 404
    finally:
        session.close()

    #a rota so traduz o Voo para um dicionario, que o Flask devolve como JSON
    return {
        "numero_voo": voo.numero_voo,
        "origem": voo.trecho.origem,
        "destino": voo.trecho.destino,
        "aeronave": voo.aeronave_id,
        "assentos_disponiveis": voo.assentos_disponiveis,
        "status": voo.status.value,
    }, 200

@app.route("/voos/<numero_voo>/cancelar", methods=["POST"])
def cancelar_voo(numero_voo):
    session = SessionFactory()
    try:
        status = montar_voo_service(session).cancelar_voo(numero_voo)
    except VooNaoEncontrado as erro:
        return {"mensagem": str(erro)}, 404
    except ErroRegraVoo as erro:  #regra do dominio, por exemplo cancelar um voo ja realizado
        return {"mensagem": str(erro)}, 400
    finally:
        session.close()

    return {"numero_voo": numero_voo, "status": status}, 200


@app.route("/voos/<numero_voo>/realizar", methods=["POST"])
def realizar_voo(numero_voo):
    session = SessionFactory()
    try:
        status = montar_voo_service(session).realizar_voo(numero_voo)
    except VooNaoEncontrado as erro:
        return {"mensagem": str(erro)}, 404
    except ErroRegraVoo as erro:
        return {"mensagem": str(erro)}, 400
    finally:
        session.close()

    return {"numero_voo": numero_voo, "status": status}, 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)