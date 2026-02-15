from flask import Flask, render_template, redirect, jsonify, request, url_for, flash, send_from_directory, send_file
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from decimal import Decimal
import ast, operator as op
import configparser
import requests
import secrets
import string
import base64
import random
import json
import io
import os

# Operatori per formule
allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

drivers = {
    "sqlite": "sqlite:///",
    "postgresql": "postgresql://",
    "mariadb": "mysql+pymysql://",
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

# Inizializza app e servizi
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "index"

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)
        app.config["SECRET_KEY"] = "test-secret"
    else:
        db_type = os.environ["DB_TYPE"]

        if db_type not in drivers:
            app.logger.info("Tipo di database non supportato")
            raise RuntimeError("Tipo di database non supportato")

        if db_type == "sqlite":
            uri = f"{drivers[db_type]}{os.environ['DB_NAME']}"
        else:
            uri = (
                f"{drivers[db_type]}"
                f"{os.environ['DB_USER']}:"
                f"{os.environ['DB_PASSWORD']}@"
                f"{os.environ['DB_HOST']}:"
                f"{os.environ['DB_PORT']}/"
                f"{os.environ['DB_NAME']}"
            )

        app.logger.info("DB Configurato con successo")
        app.config["SQLALCHEMY_DATABASE_URI"] =  uri
        app.config["SECRET_KEY"] = secrets.token_hex()

    db.init_app(app)
    login_manager.init_app(app)
    from routes import init_routes
    init_routes(app)
    return app

from models import User, GruppiUser, SysOption, TipoEvento, TipoTransazione, TipoVariabile, Evento, Transazione

app = create_app()

@app.cli.command("init-db")
def init_db():
    db.create_all()
    db.session.add(GruppiUser(name="admin", permessi=["MY_EVENTS","ALL_EVENTS","DASHBOARD","EVENTS","SETTINGS","ACCOUNT"]))

    db.session.add(SysOption(key="id_ente", value="Nome Ente"))
    db.session.add(SysOption(key="nome_iro", value="Nome"))
    db.session.add(SysOption(key="cognome_iro", value="Cognome"))
    db.session.add(SysOption(key="smtp_server", value="smtp.gmail.com"))
    db.session.add(SysOption(key="smtp_port", value=587))
    db.session.add(SysOption(key="mail_indirizzo", value="mail@esempio.it"))
    db.session.add(SysOption(key="mail_passwd", value="PASSWORD"))

    db.session.add(TipoTransazione(nome="E1", tipo="E", descrizione="E1 - anticipo da segreteria", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="E2", tipo="E", descrizione="E2 - quota saldo iscritti (al campo)", calcolata=True, formula="[[quota_saldo]]*[[partecipanti]]"))
    db.session.add(TipoTransazione(nome="E3", tipo="E", descrizione="E3 - quota campo staff", calcolata=True, formula="[[staff]]*[[quota_staff]]"))
    db.session.add(TipoTransazione(nome="E4", tipo="E", descrizione="E4 - altre entrate", calcolata=False, formula=""))

    db.session.add(TipoTransazione(nome="U1", tipo="U", descrizione="U1 - pernottamento", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="U2", tipo="U", descrizione="U2 - viveri", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="U3", tipo="U", descrizione="U3 - spostamenti", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="U4", tipo="U", descrizione="U4 - materiale", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="U5", tipo="U", descrizione="U5 - rimborsi staff", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="U6", tipo="U", descrizione="U6 - spese sostenute da segreteria", calcolata=False, formula=""))
    db.session.add(TipoTransazione(nome="U7", tipo="U", descrizione="U7 - spese sostenute da segreteria detratte dall'anticipo'", calcolata=False, formula=""))

    db.session.add(TipoVariabile(nome="num_quote_segreteria", formula="[[iscritti]]"))
    db.session.add(TipoVariabile(nome="quota_staff", formula="([[quota_acconto]]+[[quota_saldo]])/2"))
    db.session.add(TipoVariabile(nome="U6_U7", formula="[[U6]]+[[U7]]"))

    db.session.commit()
    print("Database inizializzato")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": "error", "response": "not_found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "error", "response": "internal_error"}), 500

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
