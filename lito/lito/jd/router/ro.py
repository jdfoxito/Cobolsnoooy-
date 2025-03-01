'''

RO

'''

import jwt
from datetime import datetime, timedelta
import pytz
from flask import request
from flask import render_template, make_response

from jd import fox
from model import Tradicional


class Usuario():
    '''modelado'''
    __tablename__ = 'dev_usuario_cad_iva'
    id: int
    email: str
    password: str
    username: str
    cedula: str
    nombre: str
    cargo: str
    perfil: str
    supervisor: str
    modulo: str
    opcion: str
    codreg: str
    jurisdiccion: str
    provincia: str
    canton: str
    ubicacion: str
    grupo: str
    departamento: str


def get_obsolencia(user):
    '''elimina sobreescritura'''
    fox.db.uf.pi.usuario = user.username
    fox.db.uf.pi.num_acceso = user.num_acceso
    fox.db.uf.navegante.id = user.id
    fox.db.uf.navegante.email = user.email
    fox.db.uf.navegante.password = user.password
    fox.db.uf.navegante.username = user.username
    fox.db.uf.navegante.cedula = user.cedula
    fox.db.uf.navegante.nombre = user.nombre
    fox.db.uf.navegante.cargo = user.cargo
    fox.db.uf.navegante.perfil = user.perfil
    fox.db.uf.navegante.modulo = user.modulo
    fox.db.uf.navegante.opcion = user.opcion
    fox.db.uf.navegante.supervisor = user.supervisor
    fox.db.uf.navegante.codreg = user.codreg
    fox.db.uf.navegante.jurisdiccion = user.jurisdiccion
    fox.db.uf.navegante.provincia = user.provincia
    fox.db.uf.navegante.canton = user.canton
    fox.db.uf.navegante.ubicacion = user.ubicacion
    fox.db.uf.navegante.grupo = user.grupo
    fox.db.uf.navegante.departamento = user.departamento


def verify_token(token: str):
    '''verficar token'''
    try:
        payload = jwt.decode(token, fox.db.config.SECRET_KEY, algorithms=[fox.db.config.ALGORITM])
        return payload
    except Exception as ex:
        print(f"VerTok {ex}")
        return None


def get_year():
    '''YEAR'''
    current_dateTime = datetime.now()
    return current_dateTime.date().year


def get_link_login():
    '''login link'''
    year = get_year()
    resp = make_response(render_template('pages/account/login.html', year=year))
    return resp


def salir():
    '''salir'''
    year = get_year()
    resp = make_response(render_template('pages/account/login.html', year=year))
    try:
        # resp.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, '', max_age=0, expires=0)
        request.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, '', max_age=0, expires=0)
    except Exception as ex:
        print(ex)
        return resp


def get_current_user(request: request):
    ''' get actualizaciones usuario '''
    user = {}
    data = {}
    jwt_token = None
    try:
        jwt_token = request.cookies.get(fox.db.config.COOKIE_SESSION_ID_KEY)
        if jwt_token is None:
            return None
        data = verify_token(jwt_token)
    except Exception:
        return None
    if jwt_token and data:
        usuario = data['usuario']
        user = Tradicional.User.query.filter_by(username=usuario).first()
        user.num_acceso = data['acceso']
        if not user:
            return None
    else:
        return None
    return user


def get_fecha_futura(fecha):
    '''fecha futura'''
    momento = datetime.today()
    dt_string = momento.strftime("%d/%m/%Y")
    time_data = dt_string + fecha
    format_data = "%d/%m/%Y %H:%M:%S.%f"
    fecha_futura = datetime.strptime(time_data, format_data)
    return fecha_futura


def tiempo_expira():
    '''tiempo de expiracion'''
    momento = datetime.today()
    minuto = 1
    hora = 4
    fecha_futura = get_fecha_futura(" 20:00:9.123")
    if momento > fecha_futura:
        fecha_futura = get_fecha_futura(" 23:59:9.123")

    diferencia = fecha_futura - momento

    valor_decimal = round(diferencia / timedelta(hours=1), 2)
    if valor_decimal > 1:
        partes = str(valor_decimal).split(".")
        if len(partes) == 2:
            hora = int(partes[0])
            minuto = int(partes[1])
            minuto = int(minuto*60/100)

    # expire_date = datetime.now()
    expire_date = datetime.now(pytz.timezone('America/Guayaquil'))

    print(f"ro.py 154 expire_date {expire_date} hora {hora} minuto  {minuto}")
    expire_date = expire_date + timedelta(hours=hora, minutes=minuto)
    # expire_date = expire_date.strftime('%Y-%m-%d %H:%M:%S.%f')
    # print(f"expire_date  {expire_date}")

    return expire_date
