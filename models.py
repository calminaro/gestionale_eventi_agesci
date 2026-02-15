from app import db, UserMixin

# Classi Database
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    nome = db.Column(db.String(128), nullable=False)
    cognome = db.Column(db.String(128), nullable=False)
    mail = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(512), nullable=False)
    gruppo = db.Column(db.Integer, db.ForeignKey("gruppi_user.id"), nullable=False)

class GruppiUser(db.Model):
    __tablename__ = "gruppi_user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    permessi = db.Column(db.JSON, nullable=False)

class SysOption(db.Model):
    __tablename__ = "system_option"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), nullable=False, unique=True)
    value = db.Column(db.JSON, nullable=False)

class TipoEvento(db.Model):
    __tablename__ = "tipi_eventi"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)

class TipoTransazione(db.Model):
    __tablename__ = "tipi_transazioni"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False, unique=True)
    tipo = db.Column(db.String(16), nullable=False)
    descrizione = db.Column(db.String(128), nullable=False)
    calcolata = db.Column(db.JSON, nullable=False)
    formula = db.Column(db.TEXT)

class TipoVariabile(db.Model):
    __tablename__ = "tipi_variabili"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False, unique=True)
    formula = db.Column(db.TEXT)

class Evento(db.Model):
    __tablename__ = "eventi"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    tipo = db.Column(db.Integer, db.ForeignKey("tipi_eventi.id"), nullable=False)
    responsabile = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    stato = db.Column(db.String(128), nullable=False)
    data_inizio = db.Column(db.Date, nullable=False)
    data_fine = db.Column(db.Date, nullable=True)
    localita = db.Column(db.String(128), nullable=False)
    iscritti = db.Column(db.Integer, nullable=False)
    partecipanti = db.Column(db.Integer, nullable=False)
    quota_acconto = db.Column(db.Integer, nullable=False)
    quota_saldo = db.Column(db.Integer, nullable=False)
    staff = db.Column(db.Integer, nullable=False)
    iban = db.Column(db.String(128), nullable=False)

class Transazione(db.Model):
    __tablename__ = "transazioni"
    id = db.Column(db.Integer, primary_key=True)
    tipo_transazione = db.Column(db.Integer, db.ForeignKey("tipi_transazioni.id"), nullable=False)
    evento = db.Column(db.Integer, db.ForeignKey("eventi.id"), nullable=False)
    descrizione = db.Column(db.String(128), nullable=False)
    data = db.Column(db.Date, nullable=False)
    importo = db.Column(db.Integer, nullable=False)