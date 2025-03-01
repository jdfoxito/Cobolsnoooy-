"""SERVICIO FLASK SERVIDOR, desde Enero 2023

Funcionalidades:
-   Define todas las clases a usar en el servicio

COMPORTAMIENTO:

fn(load_user)       funcion que utiliza flask_login para recargar un usuario

+-------------+-----------+---------------------------------------------------+
| Fecha       | Modifier  | Descripcion                                       |
+-------------+-----------+---------------------------------------------------+
| 05ENE2023   | jagonzaj  |   se utiliza sin ssl                              |
| 25JUL2023   | jagonzaj  |   se cambia a ssl, proteccion de algunas          |
|             |           |      vulnerabilidades web                         |
+-------------+-----------+---------------------------------------------------+

ESTANDAR PEP8
poetry run py sri_papeles_trabajo/__init__.py

"""

from flask import Flask, request, redirect, session, g, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from cachelib.file import FileSystemCache
from .config import Config
from model import CadenaFachada
from flask_compress import Compress
from flask_cors import CORS
from os import urandom
import random
from tempfile import mkdtemp
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect


from flask_talisman import Talisman
from datetime import timedelta
import secrets

params = {
    "param1": 'nupy',
    "param2": 'dummy',
    "param3": 'dummy',
    "usuario": 'usuario',
    "param4": 'dummy',
}

csp = {
    'style-src': [
            '\'unsafe-inline\'',
            '\'self\'',
        ]
}

fox = CadenaFachada.Patron(params)
db = SQLAlchemy()
cifras = random.randint(8, 14) << 2 >> 2
confa = urandom(cifras)
app = Flask(__name__)
app.secret_key = confa

nonce_list = ['default-src', 'script-src']
talisman = Talisman(app, content_security_policy=csp,
                    content_security_policy_nonce_in=nonce_list)
talisman.force_https = False
talisman.x_xss_protection = True
conf = secrets.token_hex()
compress = Compress()
compress.init_app(app)
app.config.from_object(Config)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['logged_in'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['WTF_CSRF_SECRET_KEY'] = conf
app.config["JSON_SORT_KEYS"] = False
# app.config["SESSION_PERMANENT"] = True
# app.config['PERMANENT_SESSION_LIFETIME'] = 1200
app.config['SESSION_COOKIE_NAME'] = 'GADYR'
print(f"""Iniciando como:  {app.config["SERVER_ONLINE"]}  """)
server_in_linea = app.config["SERVER_ONLINE"]
app.config.update(
    SESSION_FILE_DIR=mkdtemp(),
    SESSION_PERMANENT=True,
    SESSION_TYPE='filesystem',
    SESSION_SERIALIZATION_FORMAT='json',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_DOMAIN=server_in_linea,
    REMEMBER_COOKIE_SECURE=True,
)
app.permanent_session_lifetime = timedelta(minutes=120)
app.config["SECURITY_CSRF_COOKIE_NAME"] = "XSRF-TOKEN"
app.config["WTF_CSRF_TIME_LIMIT"] = None
app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
app.config["SECURITY_CSRF_PROTECT_MECHANISMS"] = ["session", "basic"]
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = confa
app.config['SECRET_KEY'] = confa

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'pages.login'
login_manager.session_protection = "strong"
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = "Session ha expirado Favor reingrese!"
login_manager.needs_refresh_message_category = "info"
csrf = CSRFProtect(app)


@login_manager.user_loader
def load_user(user_id):
    '''cargar usuario'''
    from model import Tradicional
    return Tradicional.User.query.get(int(user_id))


from .router import papel_trabajo_scope
from .router import sector_publico_scope
from .router import pages
from .router import dashboards
from .router import papel_portal


app.register_blueprint(papel_trabajo_scope, url_prefix="/")
app.register_blueprint(sector_publico_scope, url_prefix="/")
app.register_blueprint(pages, url_prefix="/")
app.register_blueprint(dashboards, url_prefix="/")
app.register_blueprint(papel_portal, url_prefix="/")
bcrypt = Bcrypt(app)
Session(app)

CORS(app,
     origins=[f"http://{server_in_linea}:4443/"],
     expose_headers=["Content-Type", "X-CSRFToken"],
     supports_credentials=True)


@app.after_request
def after_request(response):
    '''despues del requerimiento'''
    # response.headers["Cache-Control"] = """public, no-cache,
    #                                        no-store max-age=0,
    #                                        must-revalidate"""
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


@login_manager.unauthorized_handler
def unauthorized_handler():
    '''sin autorizacion'''
    return redirect(url_for('pages.login'))
