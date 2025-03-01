'''
+-------------------+--------------------------------------------+
| Contexto DB       |  Entidad                                   |
|                   |  Manejo de la conexion ORM                 |
+-------------------+--------------------------------------------+
| Agosto 2023       |V1                                          |
+--------------------+--+----------------------------------------+
| jagonzaj  19_AB_24 |  se migra a clase de repositorio          |
|                    |                                           |
+--------------------+--+----------------------------------------+
Webservice entry point: https://[IPV4]/account/login '''

import jwt
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, session, request, make_response
from flask_login import login_required, current_user, login_user

dashboards = Blueprint('dashboards',
                       __name__,
                       template_folder='templates',
                       static_folder='static')
from datos import Tableros
from logicas import regraf

from model import Tradicional
from jd import fox, db

from router import ro


# @dashboards.route('/', methods=['POST'])
# @login_required
# def index2():
#    print("post")


@dashboards.route('/', methods=['GET'])
@login_required
def index():
    '''pagina inicial'''

    # if request.method == 'GET':
    #    print("GET")

    # if request.method == 'POST':
    #     print("POS....")

    intervalos = {}
    # print("38 TABLERO ")
    posible_usuario = ro.get_current_user(request)
    # print(f"/ entrada TABLERO index PU {posible_usuario} ")
    tipo_ingreso = 'INGRESO'
    if posible_usuario:
        tipo_ingreso = 'RE-INGRESO'
        ro.get_obsolencia(posible_usuario)

    if not current_user.is_authenticated:
        # print(f"current_user --> {current_user.__dict__}")
        login_user(posible_usuario, remember=True)

    try:
        resp = make_response(render_template('pages/account/login.html'))

        # print(f"fox.db.uf.navegante.nombre {fox.db.uf.navegante.nombre}")
        # print(f"fox.db.uf.usuario {fox.db.uf.usuario}")
        # print(f"current_user.username {current_user.username}")

        # if fox.db.uf.navegante.nombre == '' or fox.db.uf.usuario == "usuario":
        #    return ro.get_link_login()

        # fox.db.uf.pi.usuario = current_user.username

        user = Tradicional.User.query.filter_by(username=fox.db.uf.pi.usuario).first()
        if not user:
            return ro.get_link_login()

        if session.get('num_acceso') is not None:
            if int(session.get('num_acceso')) != -1:
                fox.db.uf.pi.num_acceso = int(session.get('num_acceso'))
                user.num_acceso = fox.db.uf.pi.num_acceso
        else:
            fox.db.uf.pi.num_acceso = fox.db.uf.navegante.num_acceso
            session["num_acceso"] = fox.db.uf.navegante.num_acceso
            user.num_acceso = fox.db.uf.navegante.num_acceso
            fox.db.uf.pi.num_acceso = fox.db.uf.navegante.num_acceso
        fox.db.uf.pi.usuario = user.username
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

        fox.db.uf.pi.ipv4 = request.access_route[-1]
        num_acceso_real = fox.db.get_scalar(fox.nupy.get_sql_acceso_numero())

        if fox.db.uf.pi.num_acceso != num_acceso_real:
            fox.db.uf.pi.num_acceso = num_acceso_real

        print(f"-------------------------------------------------------------------------------------------------------{tipo_ingreso}|")
        mostrar(f"ACCESO {fox.db.uf.GREEN} {fox.db.uf.pi.num_acceso} {fox.db.uf.RESET}  ")
        mostrar(f"ACC NAVE: {fox.db.uf.CYAN} {fox.db.uf.navegante.num_acceso} {fox.db.uf.RESET}    ACCUSER:  {user.num_acceso} ")
        mostrar(f"USUARIO:  {fox.db.uf.GREEN}  {fox.db.uf.pi.usuario} {fox.db.uf.RESET} ")
        mostrar(f"IP: {fox.db.uf.GREEN} {fox.db.uf.pi.ipv4} {fox.db.uf.RESET} ")
        mostrar(f"Cédula: {fox.db.uf.GREEN} {fox.db.uf.navegante.cedula} {fox.db.uf.RESET} ")
        mostrar(f"Nombre: {fox.db.uf.GREEN} {fox.db.uf.navegante.nombre} {fox.db.uf.RESET} ")
        mostrar(f"Perfil: {fox.db.uf.GREEN} {fox.db.uf.navegante.perfil} {fox.db.uf.RESET} ")
        mostrar(f"Jurisdicción: {fox.db.uf.GREEN}  {fox.db.uf.navegante.jurisdiccion} {fox.db.uf.RESET} ")
        mostrar(f"Provincia: {fox.db.uf.GREEN} {fox.db.uf.navegante.provincia} {fox.db.uf.RESET} ")
        mostrar(f"Cantón: {fox.db.uf.GREEN} {fox.db.uf.navegante.canton} {fox.db.uf.RESET}")
        print("| -------------------------------------------------------------------------------------------------------------|")

        noticia = ''
        if session.get('notice') is not None:
            noticia = str(session["notice"])

        nupy = Tableros.MasConsultas(fox.db)
        df_actividad_reciente = fox.db.get_vector(nupy.get_sql_actividad_reciente())
        df_top_ten_devs = fox.db.get_vector(nupy.get_sql_top_ten_devs())
        df_cuardros = fox.db.get_vector(nupy.get_sql_cuadros())
        monto_en_analisis = fox.db.monto_en_analisis()
        num_contris_analisis = fox.db.num_contri_analisis()
        session["num_acceso"] = fox.db.uf.pi.num_acceso
        intervalos = {"usuario": fox.db.uf.pi.usuario,
                      "monto_en_analisis": monto_en_analisis,
                      "num_contris_analisis": num_contris_analisis,
                      "nombre": fox.db.uf.navegante.nombre,
                      "perfil": fox.db.uf.navegante.perfil,
                      "cargo": str(fox.db.uf.navegante.cargo),
                      "noticia": noticia,
                      "num_acceso": fox.db.uf.pi.num_acceso
                      }
        session["notice"] = ''

        data = {
            'usuario': fox.db.uf.pi.usuario,
            'acceso': fox.db.uf.pi.num_acceso
        }
        encoded_jwt = jwt.encode(data,
                                 key=fox.db.config.SECRET_KEY,
                                 algorithm=fox.db.config.ALGORITM)

        resp = make_response(render_template('dashboards/index.html', intervalos=intervalos, df_actividad_reciente=df_actividad_reciente, df_top_ten_devs=df_top_ten_devs, df_cuardros=df_cuardros, num_acc=fox.db.uf.pi.num_acceso))
        # resp.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, encoded_jwt, secure=True, expires=ro.tiempo_expira(), httponly=True)
        # print(f"expire_date  {expire_date}")

        print(f"expires=ro.tiempo_expira() --> {ro.tiempo_expira()} type-->:  {type(ro.tiempo_expira())} ")
        print(f"expires=datetime.utcnow() + timedelta(hours=4)  {datetime.utcnow() + timedelta(hours=4)}  type {type(datetime.utcnow() + timedelta(hours=4))} ")

        # resp.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, encoded_jwt, secure=True, expires=datetime.utcnow() + timedelta(hours=4), httponly=True)
        resp.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, encoded_jwt, secure=True, expires=ro.tiempo_expira(), httponly=True)

    except Exception as ex:
        print(f" RO TABLERO  -->  {ex}")
        return render_template('pages/account/login.html')
    return resp


def mostrar(texto):
    '''printer'''
    longitud = len(texto) + 10
    umbral = 130
    diferencia = umbral - longitud
    print("|" + texto + diferencia * " " + "|")


@dashboards.route('/estadistica/<opcion>', methods=['GET', 'POST'])
@login_required
def estad(opcion):
    '''Estadisticas'''
    tipografico = 0
    posible_usuario = ro.get_current_user(request)

    print(f"180 GRAFICAS posible_usuario --> {posible_usuario}")

    if posible_usuario:
        ro.get_obsolencia(posible_usuario)
        if current_user.is_authenticated:
            login_user(posible_usuario, remember=True)

        gra = regraf.Graficas()
        match int(opcion):
            case 1: tipografico = gra.graf_tramitacion()
            case 2: tipografico = gra.devuelto_vs_atentido()
            case 3: tipografico = gra.empresas()
            case 4: tipografico = gra.hora_atencion()
            case 5: tipografico = gra.hora_atencion()
            case 6: tipografico = gra.grafica_usuarios()
        return tipografico
    else:
        return ro.get_link_login()
