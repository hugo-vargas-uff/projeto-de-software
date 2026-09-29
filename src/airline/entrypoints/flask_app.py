import uuid
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from airline.adapters.orm import Base
from airline.adapters.repository import SqlAlchemyTripulanteRepository, SqlAlchemyEscalaRepository, \
    SqlAlchemyReservaRepository
from airline.service_layer.services import TripulanteService, EscalaService, ReservaService
from airline.domain.model import CargoTripulante, ErroRegraTripulacao

from datetime import date
from airline.adapters.repository import SqlAlchemyVooRepository, SqlAlchemyAeronaveRepository
from airline.service_layer.services import VooService, AeronaveService
from airline.domain.model import ErroRegraVoo
from airline.domain.exception import VooJaExiste, VooNaoEncontrado, AeronaveNaoEncontrada, AeronaveJaExiste, AeronaveIndisponivel, \
    PassageiroNaoEncontrado, CpfJaCadastradoException
from airline.adapters.repository import SqlAlchemyPassageiroRepository
from airline.service_layer.services import PassageiroService


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


# voo
def montar_voo_service(session):
    # liga as pecas reais: repositorios SQLAlchemy usando a mesma sessao que o servico vai confirmar
    return VooService(
        SqlAlchemyVooRepository(session),
        SqlAlchemyAeronaveRepository(session),
        session,
    )

def montar_aeronave_service(session):
    repository = SqlAlchemyAeronaveRepository(session)
    return AeronaveService(repository)


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
        session.close()  # roda sempre, com ou sem erro

    return {"numero_voo": numero_voo}, 201

@app.post("/aeronaves")
def cadastrar_aeronave():
    dados = request.get_json()

    session = SessionFactory()

    try:
        service = montar_aeronave_service(session)

        aeronave = service.cadastrar_aeronave(
            prefixo=dados["prefixo"],
            modelo=dados["modelo"],
            capacidade=dados["capacidade"],
            validade_vistoria=date.fromisoformat(
                dados["validade_vistoria"]
            )
        )

        return {
            "prefixo": aeronave.prefixo,
            "modelo": aeronave.modelo,
            "capacidade": aeronave.capacidade,
            "validade_vistoria": aeronave.validade_vistoria.isoformat()
        }, 201

    except AeronaveJaExiste as erro:
        return {
            "mensagem": str(erro)
        }, 400

    finally:
        session.close()

@app.get("/aeronaves/<prefixo>/disponibilidade")
def consultar_disponibilidade_aeronave(prefixo):
    session = SessionFactory()

    try:
        service = montar_aeronave_service(session)

        disponivel = service.consultar_disponibilidade(
            prefixo=prefixo,
            hoje=date.today()
        )

        if disponivel is None:
            return {
                "erro": "Aeronave nao encontrada"
            }, 404

        return {
            "prefixo": prefixo,
            "disponivel": disponivel
        }, 200

    finally:
        session.close()


@app.route("/voos/<numero_voo>", methods=["GET"])
def consultar_voo(numero_voo):
    session = SessionFactory()
    try:
        voo = montar_voo_service(session).consultar_voo(numero_voo)
    except VooNaoEncontrado as erro:
        return {"mensagem": str(erro)}, 404
    finally:
        session.close()

    # a rota so traduz o Voo para um dicionario, que o Flask devolve como JSON
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
    except ErroRegraVoo as erro:  # regra do dominio, por exemplo cancelar um voo ja realizado
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

@app.route("/voos/<numero_voo>/assentos", methods=["POST"])
def alocar_assento(numero_voo):
    session = SessionFactory()
    try:
        assentos = montar_voo_service(session).alocar_assento(numero_voo)
    except VooNaoEncontrado as erro:
        return {"mensagem": str(erro)}, 404
    except ErroRegraVoo as erro:  #voo lotado ou nao agendado
        return {"mensagem": str(erro)}, 400
    finally:
        session.close()

    return {"numero_voo": numero_voo, "assentos_disponiveis": assentos}, 200

@app.post("/passageiros")
def criar_passageiro():
    data = request.get_json()

    session = SessionFactory()

    try:
        repository = SqlAlchemyPassageiroRepository(session)
        service = PassageiroService(repository)

        passageiro = service.criar_passageiro(nome=data["nome"], cpf=data["cpf"])

        return jsonify({
            "id": str(passageiro.id),
            "nome": passageiro.nome,
            "cpf": passageiro.cpf
        }), 201

    except CpfJaCadastradoException as e:
        return jsonify({ "mensagem": str(e) }), 409

    finally:
        session.close()

@app.get("/passageiros/<cpf>")
def buscar_passageiro(cpf):

    session = SessionFactory()

    try:
        repository = SqlAlchemyPassageiroRepository(session)
        service = PassageiroService(repository)

        passageiro = service.buscar(cpf)

        return jsonify({
            "id": str(passageiro.id),
            "nome": passageiro.nome,
            "cpf": passageiro.cpf
        }), 200

    except PassageiroNaoEncontrado as e:
        return jsonify({ "mensagem": str(e) }), 404

    finally:
        session.close()

@app.post("/reservas")
def criar_reserva():
    data = request.get_json()

    session = SessionFactory()

    try:
        reserva_repository = SqlAlchemyReservaRepository(session)
        passageiro_repository = SqlAlchemyPassageiroRepository(session)
        voo_repository = SqlAlchemyVooRepository(session)

        service = ReservaService(
            reserva_repository=reserva_repository,
            passageiro_repository=passageiro_repository,
            voo_repository=voo_repository
        )

        reserva = service.criar_reserva(voo_id=data["voo_id"], passageiro_id=uuid.UUID(data["passageiro_id"]))

        return jsonify({
            "voo_id": reserva.voo_id,
            "passageiro_id": str(reserva.passageiro_id),
            "status": reserva.status.value
        }), 201

    except PassageiroNaoEncontrado as e:
        return jsonify({ "mensagem": str(e) }), 404

    except VooNaoEncontrado as e:
        return jsonify({ "mensagem": str(e) }), 404

    finally:
        session.close()

@app.get("/reservas/<voo_id>/<passageiro_id>")
def buscar_reserva(voo_id, passageiro_id):

    session = SessionFactory()

    try:
        reserva_repository = SqlAlchemyReservaRepository(session)

        reserva = reserva_repository.buscar(voo_id=voo_id,passageiro_id=uuid.UUID(passageiro_id))

        if reserva is None:
            return jsonify({ "mensagem": "Reserva nao encontrada" }), 404

        return jsonify({
            "voo_id": reserva.voo_id,
            "passageiro_id": str(reserva.passageiro_id),
            "status": reserva.status.value
        }), 200

    finally:
        session.close()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
