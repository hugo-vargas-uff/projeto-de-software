import uuid
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyTripulanteRepository, SqlAlchemyEscalaRepository
from airline.service_layer.services import TripulanteService, EscalaService
from airline.domain.model import CargoTripulante, ErroRegraTripulacao

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


# --- Despacho

from airline.adapters.repository import SqlAlchemyDespachoRepository
from airline.service_layer.services import DespachoService
from airline.domain.model import ErroRegraDespacho
from airline.domain.exception import DespachoNaoEncontrado


@app.route("/despachos", methods=["POST"])
def abrir_despacho():
    data = request.get_json()
    session = SessionFactory()
    repo = SqlAlchemyDespachoRepository(session)
    service = DespachoService(repo)

    try:
        despacho = service.abrir_despacho(
            voo_id=data["voo_id"],
            carga_maxima=float(data["carga_maxima"])
        )
        return jsonify({
            "id": str(despacho.id),
            "voo_id": despacho.voo_id,
            "carga_maxima": despacho.carga_maxima,
            "peso_total": despacho.peso_total(),
            "peso_disponivel": despacho.peso_disponivel()
        }), 201
    except ErroRegraDespacho as e:
        return jsonify({"mensagem": str(e)}), 400


@app.route("/despachos/<despacho_id>/volumes", methods=["POST"])
def adicionar_volume(despacho_id):
    data = request.get_json()
    session = SessionFactory()
    repo = SqlAlchemyDespachoRepository(session)
    service = DespachoService(repo)

    try:
        despacho = service.adicionar_volume(uuid.UUID(despacho_id), peso=float(data["peso"]))
        return jsonify({
            "id": str(despacho.id),
            "voo_id": despacho.voo_id,
            "carga_maxima": despacho.carga_maxima,
            "peso_total": despacho.peso_total(),
            "peso_disponivel": despacho.peso_disponivel()
        }), 201
    except DespachoNaoEncontrado as e:
        return jsonify({"mensagem": str(e)}), 404
    except ErroRegraDespacho as e:
        return jsonify({"mensagem": str(e)}), 400


@app.route("/despachos/<despacho_id>", methods=["GET"])
def consultar_despacho(despacho_id):
    session = SessionFactory()
    repo = SqlAlchemyDespachoRepository(session)
    service = DespachoService(repo)

    try:
        despacho = service.consultar_despacho(uuid.UUID(despacho_id))
    except DespachoNaoEncontrado as e:
        return jsonify({"mensagem": str(e)}), 404

    return jsonify({
        "id": str(despacho.id),
        "voo_id": despacho.voo_id,
        "carga_maxima": despacho.carga_maxima,
        "volumes": [volume.peso for volume in despacho.volumes],
        "peso_total": despacho.peso_total(),
        "peso_disponivel": despacho.peso_disponivel()
    }), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)