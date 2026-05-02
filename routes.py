from models import db, User, GruppiUser, SysOption, TipoEvento, TipoTransazione, TipoVariabile, Evento, Transazione
from flask import render_template, redirect, jsonify, request, url_for, flash, send_from_directory, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from decimal import Decimal
import ast, operator as op
import requests
import secrets
import string
import base64
import random
import json
import io

# Operatori per formule
allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def eval_expr(expr):
    node = ast.parse(expr, mode='eval').body

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return allowed_operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](_eval(node.operand))
        else:
            raise ValueError(f"Operatore non consentito: {node}")
    return _eval(node)

def calcola_formula(formula, variabili):
    for nome, valore in variabili.items():
        formula = formula.replace(f"[[{nome}]]", str(valore))
    return eval_expr(formula)

def init_routes(app):
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("index.html")
        
    @app.route("/dashboard")
    @login_required
    def dashboard():
        if "DASHBOARD" and "EVENTS" in GruppiUser.query.filter_by(id=current_user.gruppo).first().permessi:
            return render_template("dashboard.html")
        return redirect(url_for("index"))

    @app.route("/evento/<evento_id>")
    @login_required
    def evento(evento_id):
        tmp_evento = Evento.query.filter_by(id=int(evento_id)).first()
        evento = {
            "id": tmp_evento.id,
            "nome": tmp_evento.nome,
            "tipo": TipoEvento.query.filter_by(id=tmp_evento.tipo).first().nome,
            "stato": tmp_evento.stato
            }
        return render_template("evento.html", evento=evento, page="eventi")

    @app.route("/account")
    @login_required
    def account():
        return render_template("account.html")

    @app.route("/impostazioni")
    @login_required
    def impostazioni():
        return render_template("impostazioni.html")

    @app.route("/sidebardata")
    @login_required
    def sidebardata():
        id_ente = SysOption.query.filter_by(key="id_ente").first().value
        return jsonify({"status": "success", "response": {"username": current_user.username, "id_ente": id_ente}})

    @app.route("/eventi_list", methods=["GET", "POST"])
    @login_required
    def eventi_list():
        if request.method == "POST":
            evento = Evento(nome=request.json["nome"], tipo=request.json["tipo_evento"], responsabile=request.json["account_responsabile"], stato="PENDING", data_inizio=datetime.today().date(), localita="ignota", iscritti=0, partecipanti=0, quota_acconto=0, quota_saldo=0, staff=1)
            db.session.add(evento)
            db.session.commit()
            return jsonify({"status": "success", "response": "ok"})
        elenco_eventi = []
        tmp_eventi = Evento.query.all()
        for i in tmp_eventi:
            tmp_responsabile = User.query.filter_by(id=i.responsabile).first()
            tmp_tipo = TipoEvento.query.filter_by(id=i.tipo).first()
            evento = {
                "id": i.id,
                "nome": i.nome,
                "tipo": tmp_tipo.nome,
                "responsabile": f"{tmp_responsabile.nome} - {tmp_responsabile.cognome}",
                "stato": i.stato
                }
            elenco_eventi.append(evento)
        return jsonify({"status": "success", "response": elenco_eventi})

    @app.route("/evento_data/<evento_id>", methods=["GET", "POST", "DELETE"])
    @login_required
    def evento_edit(evento_id):
        richiesta = request.args.get("tipo")
        print(richiesta)
        if request.method == "DELETE":
            if richiesta == "elimina":
                evento = Evento.query.filter_by(id=int(evento_id)).first()
                db.session.delete(evento)
                db.session.commit()
                return jsonify({"status": "success", "response": "ok"})
        if request.method == "POST":
            if richiesta == "attiva":
                evento = Evento.query.filter_by(id=int(evento_id)).first()
                evento.stato = "ACTIVE"
                db.session.commit()
                return jsonify({"status": "success", "response": "ok"})
            if richiesta == "sottometti":
                evento = Evento.query.filter_by(id=int(evento_id)).first()
                evento.stato = "SUBMIT"
                db.session.commit()
                return jsonify({"status": "success", "response": "ok"})
            if richiesta == "update":
                try:
                    tmp_quota_acconto = float(str(request.json["quota_acconto"]).replace(",", "."))
                    tmp_quota_saldo = float(str(request.json["quota_saldo"]).replace(",", "."))
                except:
                    return jsonify({"status": "error", "response": 'importo non valido'})
                evento = Evento.query.filter_by(id=int(evento_id)).first()
                evento.nome = request.json["nome_evento"]
                evento.tipo = request.json["tipo_evento"]
                evento.responsabile = request.json["responsabile"]
                evento.data_inizio = datetime.strptime(request.json["data_inizio"], "%Y-%m-%d")
                evento.data_fine = datetime.strptime(request.json["data_fine"], "%Y-%m-%d")
                evento.localita = request.json["localita"]
                evento.iscritti = int(request.json["iscritti"])
                evento.partecipanti = int(request.json["partecipanti"])
                evento.quota_acconto = tmp_quota_acconto
                evento.quota_saldo = tmp_quota_saldo
                evento.staff = int(request.json["staff"])
                evento.iban = request.json["iban"]
                db.session.commit()
                return jsonify({"status": "success", "response": "ok"})
            evento = Evento(nome=request.json["nome"], tipo=request.json["tipo_evento"], responsabile=request.json["account_responsabile"], stato="PENDING", data_inizio=datetime.today().date(), localita="ignota", iscritti=0, partecipanti=0, quota_acconto=0, staff=1)
            db.session.add(evento)
            db.session.commit()
            return jsonify({"status": "success", "response": "ok"})
        tmp_evento = Evento.query.filter_by(id=int(evento_id)).first()
        try:
            tmp_data_fine = tmp_evento.data_fine.strftime("%Y-%m-%d")
        except:
            tmp_data_fine = ""
        transazioni = []
        if richiesta == "transazioni":
            tmp_transazioni = Transazione().query.filter_by(evento=int(evento_id))
            for i in tmp_transazioni:
                transazione = {
                    "id": i.id,
                    "data": i.data,
                    "tipo": TipoTransazione().query.filter_by(id=i.tipo_transazione).first().tipo,
                    "tipo_transazione": TipoTransazione().query.filter_by(id=i.tipo_transazione).first().descrizione,
                    "data": i.data.strftime("%Y-%m-%d"),
                    "descrizione": i.descrizione,
                    "importo": i.importo
                    }
                transazioni.append(transazione)
        if richiesta == "rendiconto":
            tipi_transazioni = TipoTransazione().query.all()
            for i in tipi_transazioni:
                tipo_transazione = {
                    "id": i.id,
                    "tipo": i.tipo,
                    "descrizione": i.descrizione,
                    "calcolata": i.calcolata,
                    "importo": 0
                    }
                if not i.calcolata:
                    for y in Transazione().query.filter_by(evento=int(evento_id)).filter_by(tipo_transazione=i.id):
                        tipo_transazione["importo"] = Decimal(tipo_transazione["importo"]) + Decimal(str(y.importo).replace(",", "."))
                transazioni.append(tipo_transazione)
        evento = {
            "id": tmp_evento.id,
            "nome": tmp_evento.nome,
            "tipo": tmp_evento.tipo,
            "stato": True,
            "responsabile": tmp_evento.responsabile,
            "data_inizio": tmp_evento.data_inizio.strftime("%Y-%m-%d"),
            "data_fine": tmp_data_fine,
            "localita": tmp_evento.localita,
            "iscritti": tmp_evento.iscritti,
            "partecipanti": tmp_evento.partecipanti,
            "quota_acconto": tmp_evento.quota_acconto,
            "quota_saldo": tmp_evento.quota_saldo,
            "staff": tmp_evento.staff,
            "iban": tmp_evento.iban,
            "tot_entrate": 0,
            "tot_uscite": 0,
            "transazioni": transazioni
            }
        try:
            evento["quote_pagate"] = calcola_formula(TipoVariabile.query.filter_by(nome="num_quote_segreteria").first().formula, evento)
            evento["quota_staff"] = calcola_formula(TipoVariabile.query.filter_by(nome="quota_staff").first().formula, evento)
        except:
            evento["quote_pagate"] = 0
            evento["quota_staff"] = 0
        try:
            if richiesta == "rendiconto":
                for i in evento["transazioni"]:
                    if i["calcolata"]:
                        try:
                            i["importo"] = Decimal(calcola_formula(TipoTransazione.query.filter_by(id=i["id"]).first().formula, evento))
                        except Exception as e:
                            print(e)
                tmp_totale = Decimal(0.0)
                tmp_entrate = Decimal(0.0)
                tmp_uscite = Decimal(0.0)
                for i in evento["transazioni"]:
                    if i["tipo"] == "E":
                        tmp_entrate = tmp_entrate + i["importo"]
                    elif i["tipo"] == "U":
                        tmp_uscite = tmp_uscite + i["importo"]
                evento["tot_entrate"] = tmp_entrate
                evento["tot_uscite"] = tmp_uscite
                tmp_totale = tmp_entrate - tmp_uscite
                if tmp_totale < 0:
                    evento["stato"] = False
        except Exception as e:
            print(e)
        return jsonify({"status": "success", "response": evento})

    @app.route("/transazioni/<evento_id>", methods=["POST"])
    @login_required
    def transazioni(evento_id):
        try:
            tmp_importo = float(request.json["importo"].replace(",", "."))
        except:
            return jsonify({"status": "error", "response": f'importo {request.json["importo"]} non valido'})
        transazione = Transazione(tipo_transazione=request.json["tipo_transazione"], evento=int(evento_id), descrizione=request.json["descrizione"], data=datetime.strptime(request.json["data"], "%Y-%m-%d"), importo=tmp_importo)
        db.session.add(transazione)
        db.session.commit()
        return jsonify({"status": "success", "response": "ok"})

    @app.route("/system_option", methods=["GET", "POST"])
    @login_required
    def system_option():
        if request.method == "POST":
            SysOption.query.filter_by(key="id_ente")[0].value = request.json["id_ente"]
            SysOption.query.filter_by(key="nome_iro")[0].value = request.json["nome_iro"]
            SysOption.query.filter_by(key="cognome_iro")[0].value = request.json["cognome_iro"]
            SysOption.query.filter_by(key="smtp_server")[0].value = request.json["smtp_server"]
            SysOption.query.filter_by(key="smtp_port")[0].value = int(request.json["smtp_port"])
            SysOption.query.filter_by(key="mail_indirizzo")[0].value = request.json["mail_indirizzo"]
            SysOption.query.filter_by(key="mail_passwd")[0].value = request.json["mail_passwd"]
            db.session.commit()
        tmp_sysop = SysOption.query.all()
        elenco_sysop = {}
        for i in tmp_sysop:
            elenco_sysop[i.key] = i.value
        return jsonify({"status": "success", "response": elenco_sysop})

    @app.route("/user", methods=["GET", "POST", "DELETE"])
    @login_required
    def user():
        if request.method == "DELETE":
            return jsonify({"status": "success", "response": "ok"})
        if request.method == "POST":
            return jsonify({"status": "success", "response": "ok"})
        tmp_user = User.query.all()
        elenco_user = []
        for i in tmp_user:
            utente = {
                "id": i.id,
                "username": i.username,
                "nome": i.nome,
                "cognome": i.cognome,
                "mail": i.mail,
                "gruppo": i.gruppo
                }
            elenco_user.append(utente)
        return jsonify({"status": "success", "response": elenco_user})

    @app.route("/tipi_transazioni/<tipo>")
    @login_required
    def tipi_transazioni(tipo):
        if tipo == "entrata":
            tmp_transazione = TipoTransazione.query.filter_by(tipo="E")
        elif tipo == "uscita":
            tmp_transazione = TipoTransazione.query.filter_by(tipo="U")
        elif tipo == "manuali":
            tmp_transazione = TipoTransazione.query.filter_by(calcolata="false")
        elif tipo == "all":
            tmp_transazione = TipoTransazione.query.all()
        else:
            return jsonify({"status": "error", "response": f"tipo {tipo} non valido"})
        elenco_tipi = []
        for i in tmp_transazione:
            evento = {
                "id": i.id,
                "nome": i.nome,
                "descrizione": i.descrizione,
                "calcolata": i.calcolata
                }
            elenco_tipi.append(evento)
        return jsonify({"status": "success", "response": elenco_tipi})

    @app.route("/tipi_eventi", methods=["GET", "POST", "DELETE"])
    @login_required
    def tipi_eventi():
        if request.method == "DELETE":
            return jsonify({"status": "success", "response": "ok"})
        if request.method == "POST":
            return jsonify({"status": "success", "response": "ok"})
        tmp_eventi = TipoEvento.query.all()
        elenco_tipi = []
        for i in tmp_eventi:
            evento = {
                "id": i.id,
                "nome": i.nome
                }
            elenco_tipi.append(evento)
        return jsonify({"status": "success", "response": elenco_tipi})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if len(User.query.all()) == 0:
            return jsonify({"status": "success", "response": "no_user"})
        if request.method == "POST":
            utente = User.query.filter_by(username=request.json["username"]).first()
            if utente:
                if check_password_hash(utente.password, request.json["passwd"]):
                    password = generate_password_hash(request.json["passwd"])
                    utente.password = password
                    db.session.commit()
                    login_user(utente)
                    app.logger.info("L'utente %s ha fatto login", utente.username)
                    return jsonify({"status": "success", "response": "success"})
                else:
                    return jsonify({"status": "success", "response": "invalid"})
            else:
                return jsonify({"status": "success", "response": "invalid"})
        return jsonify({"status": "success", "response": "error"})

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))
