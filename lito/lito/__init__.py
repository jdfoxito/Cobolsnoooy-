r"""SERVICIO, desde Enero 2023
Funcionalidades:
-arranca el servicio de hypercorn un minisevidor wgsi, depende del otro init



    +-------------------+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+
    | Fecha             | Modifier          | Descripcion                                                                                                                                  |
    +-------------------+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+
    | 05ENE2023         | jagonzaj          |   se utiliza uvicorn
    | 05ENE2024         | jagonzaj          |   se cambia a hypercorn
    +-------------------+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+

ESTANDAR PEP8
poetry run py sri_papeles_trabajo/__init__.py

"""

from hypercorn.config import Config
import asyncio
from hypercorn.asyncio import serve
from jd import app
from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)
config = Config()
config.access_log_format = '%(h)s %(l)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(T)s" '
server_in_linea = app.config["SERVER_ONLINE"]
config.bind = [f"{server_in_linea}:4443"]
config.errorlog = r"C:\nginx\logs\hipercorn_err.log"
config.accesslog = r"C:\nginx\logs\hipercorn_access.log"
config.use_reloader = True
config.alpn_protocols = "h2"
asyncio.run(serve(asgi_app, config))
