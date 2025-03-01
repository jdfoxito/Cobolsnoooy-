"""servicios, desde Noviembre 2022
Funcionalidades:
  - Sirve para comerciar la informacion via json entre el navegador
  y el servidor.

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

e inician las validaciones del contri

 - fn(login_required)                   solicta que el usuario este logueado
 - fn(sostener_air)                     recarga las acciones de cada usuario
 - fn(get_declaraciones_periodo)        trae las declaraciones
 - fn(cargar_retenciones_ini())         lee el archivo de excel

    +-------------+-----------+-----------------------------------------------+
    | Fecha       | Modifier  | Descripcion                                   |
    +-------------+-----+-------------------+---------------------------------+
    | 30NOV2022   | jagonzaj  |   Trabajo sin ssl via sessiones,              |
    | 15DIC2023   | jagonzaj  |   se cambia a tabla el manejo                 |
    |             |           |       de variables de memoria                 |
    +-------------+-----------+-------------+---------------------------------+

ESTANDAR PEP8

"""

from timeit import default_timer as timer
from flask import Blueprint, render_template, request, make_response, session, redirect, url_for, flash
from flask_login import current_user, AnonymousUserMixin, login_user
from flask_cors import cross_origin

from functools import wraps
import pandas as pd
import json
import os
from werkzeug.utils import secure_filename
from datetime import timedelta

from jd import fox
from ayudante import Interacciones
from model import Tradicional
from datetime import datetime
from datos import Reportes, RetencionesQ
from router import ro

import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


papel_trabajo_scope = Blueprint('papel_trabajo_scope',
                                __name__,
                                template_folder='templates',
                                static_folder='static')


def login_required(func):
    '''ingreso'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if fox.db.uf.pi.usuario == "usuario" or fox.db.uf.pi.usuario == '':
            return {"valida": -100}
        return func(*args, **kwargs)
    return wrapper


def sostener_air(u, a, j, h, n, operacion="recargar", incluir_dics=True):
    '''revision de sesiones'''
    ir_a_login = False
    num_acceso = -1
    mensaje = ''

    posible_usuario = ro.get_current_user(request)
    if posible_usuario:
        ro.get_obsolencia(posible_usuario)
        login_user(posible_usuario, remember=True)
    else:
        return -1, ''

    if isinstance(current_user, AnonymousUserMixin) or current_user.username is None or current_user.username == 'usuario' or current_user.username != u:
        return -1, ''
    else:
        usuario_actual = current_user.username
        aente = request.headers.get('User-Agent')
        num_acceso, j, h, n, mensaje = fox.db.set_particula_live(usuario_actual, a, j, h, n, aente, operacion)
        try:
            if num_acceso < 1:
                ir_a_login = True
            fox.db.uf.pi.num_acceso = num_acceso
            if incluir_dics:
                if "df_periodos_talves" in j and isinstance(j["df_periodos_talves"], pd.DataFrame):
                    j["df_periodos_talves"] = ''
                j_ = Interacciones.param_iva(j)
                fox.db.uf.pi = j_
                h_ = Interacciones.param_historia(h)
                fox.db.uf.his = h_
            n_ = Interacciones.Celebridades.Navegante(n)
            fox.db.uf.navegante = n_
        except Exception as ex:
            print(f"ro cadena iva 57 ex {ex}  j \n  {j} ")
            ir_a_login = True
    if ir_a_login:
        num_acceso = -1

    return num_acceso, mensaje


@papel_trabajo_scope.route("papeles/get_declaraciones_periodo", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_declaraciones_periodo():
    '''declaraciones periodo'''
    params = request.get_json()
    para_pre = 0
    u, a, c = fox.db.uf.is_dupla(params["usuario"],  params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a,  "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100
    fox.db.uf.re_mapeado(params)
    vec = fox.legir.get_declaraciones_periodo()
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    sostener_air(fox.db.uf.pi.usuario, num_axxes, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    return vec


@papel_trabajo_scope.route("papeles/get_previas", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_previas():
    '''tramites previos'''
    params = request.get_json()
    para_pre = 0
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100
    fox.db.uf.re_mapeado(params)
    vec = fox.opcion.get_previas_sql()
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    return vec


@papel_trabajo_scope.route("papeles/get_internas", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_internas():
    '''similares y previos'''
    params = request.get_json()
    para_pre = 0
    u, a, c = fox.db.uf.is_dupla(params["usuario"],  params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100
    fox.db.uf.re_mapeado(params)
    vec = fox.opcion.get_canadian()
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    return vec


@papel_trabajo_scope.route("papeles/get_elecciones_futuras", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_elecciones_futuras():
    '''elecciones de las declaracion a futura'''
    params = request.get_json()
    para_pre = 1
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100

    fox.db.uf.re_mapeado(params)
    vec = fox.actual.get_bus_seleccionadas_futuras()
    sostener_air(fox.db.uf.pi.usuario, num_axxes, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    vec["valida"] = para_pre
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    return vec


@papel_trabajo_scope.route("papeles/get_pre_chain_norm", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_pre_chain_norm():
    '''encadenamiento normal'''
    params = request.get_json()
    para_pre = 1
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100

    fox.db.uf.re_mapeado(params)
    vec = fox.iva.get_bus_chains()
    sostener_air(fox.db.uf.pi.usuario, num_axxes, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    vec["valida"] = para_pre
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    return vec


@papel_trabajo_scope.route("papeles/get_fonts", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_fonts():
    '''fuentes de informacion'''
    params = request.get_json()
    para_pre = 0
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100
    fox.db.uf.re_mapeado(params)
    vec = fox.ca.get_australian()
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    return vec


@papel_trabajo_scope.route("papeles/get_providencias")
@login_required
@cross_origin(supports_credentials=True)
def get_providencias():
    '''providencias'''
    para_pre = 1
    args = request.args
    params = json.loads(args.get('ufx'))
    u, a, c = fox.db.uf.is_dupla(params["usuario"],  params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a,  "", "", "",  "recargar")
    if num_axxes < 1:
        para_pre = -100

    fox.db.uf.re_mapeado(params)
    vec = fox.pr.get_providencias_revisadas()
    vec["valida"] = para_pre
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    return vec


@papel_trabajo_scope.route("papeles/get_elecciones", methods=['POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_elecciones():
    '''elecciones de declaraciones '''
    params = request.get_json()
    para_pre = 0
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        para_pre = -100
    fox.db.uf.re_mapeado(params)
    vec = fox.decla.get_bus_seleccionadas()
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    sostener_air(fox.db.uf.pi.usuario, fox.db.uf.pi.num_acceso, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    return vec


@papel_trabajo_scope.route("papeles/get_compritas", methods=['GET', 'POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_compritas():
    '''compritas'''
    params = request.get_json()
    para_pre = 0
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")

    if num_axxes < 1:
        para_pre = -100

    fox.db.uf.re_mapeado(params)
    vec = fox.pa.get_resumen_compras(fox.db.uf.pi.usuario)
    vec["para_pre"] = para_pre
    vec["mensaje_r"] = mensaje
    sostener_air(fox.db.uf.pi.usuario, fox.db.uf.pi.num_acceso, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    return vec


@papel_trabajo_scope.route("papeles/get_paginado_ir/<pagina>/<tiempo>/<x>/<y>/<z>/<usx>/<mu>", methods=['GET', 'POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_paginado_ir(pagina, tiempo, x, y, z, usx, mu):
    '''paginacion ir'''
    params = {}
    params["param1"] = fox.db.uf.costelo(tiempo)
    params["param2"] = x
    params["param3"] = y
    params["param4"] = 'F'
    params["param5"] = z
    params["cuerda"] = pagina
    params["usuario"] = usx
    params["mu"] = mu
    para_pre = 1
    u, a, c = fox.db.uf.is_dupla(params["usuario"],  params["mu"])
    if not c:
        para_pre = -100
    num_axxes, mensaje = sostener_air(u, a,  "", "", "",  "recargar")
    if num_axxes < 1:
        para_pre = -100
    fox.db.uf.re_mapeado(params)
    fox.db.uf.pi.procedencia = 'interna'
    _jd = fox.db.uf.pi
    _sql = RetencionesQ.Terceros(_jd)
    _sql.jd.contri_real = tiempo
    pre = fox.pa.get_pagina_ir(_sql, int(pagina), -1)
    pre["valida"] = para_pre
    pre["para_pre"] = para_pre
    pre["mensaje_r"] = mensaje
    return pre


@papel_trabajo_scope.route("papeles/cargar_retenciones_ini", methods=['GET', 'POST'])
# @cross_origin(supports_credentials=True)
@login_required
def cargar_retenciones_ini():
    '''cargar retenciones listado'''
    resultado_login_err = {
            "novedades": {},
            "stop": -100
        }

    args = request.args
    estadisticas = {}
    estadisticas_parcial = {}
    start = timer()
    params = json.loads(args.get('ufx'))
    u, a, c = fox.db.uf.is_dupla(params["usuario"],  params["mu"])
    if not c:
        return resultado_login_err
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1:
        return resultado_login_err
    mensaje = mensaje.strip() + ''
    fox.db.uf.re_mapeado(params)
    estadisticas["ip"] = fox.db.uf.pi.ipv4
    estadisticas["usuario_actual"] = fox.db.uf.pi.usuario
    fox.uf.his.time_inicia = fox.db.get_fecha_ymd_hms()
    fox.db.uf.his.num_decla_mensual_subjetivas = 0
    fox.uf.his.numeros_semestrales_subjetivas = 0
    _jd = fox.db.uf.pi

    if not fox.db.uf.informante.detener:
        respuesta, fox.uf.his.num_tramites_encontrados = fox.db.numero_procedimientos_contri()
        if fox.uf.his.num_tramites_encontrados == 0:
            fox.db.uf.informante.agregar_razones(respuesta)
            fox.db.uf.informante.detener = True

    if not fox.db.uf.informante.detener:
        respuesta, fox.uf.his.num_declaraciones_subjetivas = fox.db.numero_declas_periodo_contri()
        if fox.uf.his.num_declaraciones_subjetivas == 0:
            fox.db.uf.informante.agregar_razones(respuesta)
            fox.db.uf.informante.detener = True
        else:
            fox.db.uf.his.num_decla_mensual_subjetivas = fox.db.num_declas_mensuales_periodo()

    if not fox.db.uf.informante.detener:
        respuesta, fox.uf.his.num_terceros_subjetivos = fox.db.numero_terceros_periodo_contri()
        if fox.uf.his.num_terceros_subjetivos == 0:
            fox.db.uf.informante.agregar_razones(respuesta)
            fox.db.uf.informante.detener = True

    if not fox.db.uf.informante.detener:
        _sql = RetencionesQ.Terceros(_jd)
        fox.uf.his.numeros_semestrales_subjetivas = fox.db.get_scalar(_sql.numero_declas_semestrales())
        if fox.uf.his.numeros_semestrales_subjetivas > 0 and fox.uf.his.num_decla_mensual_subjetivas > 0:
            var_m = f"""El contribuyente {fox.uf.pi.contri} tiene {fox.uf.his.numeros_semestrales_subjetivas} semestrales, {fox.uf.his.num_decla_mensual_subjetivas}  mensuales , en el periodo"""
            fox.db.uf.informante.agregar_razones({'mensaje': var_m, "category": "warning"})
            fox.db.uf.informante.detener = False

        if fox.uf.his.numeros_semestrales_subjetivas == 0 and fox.uf.his.num_decla_mensual_subjetivas == 0:
            fox.db.uf.informante.agregar_razones({'mensaje': f"El contribuyente {fox.uf.pi.contri} no tiene declaraciones mensuales o semestrales , en el periodo", "category": "warning"})
            fox.db.uf.informante.detener = True

    renombrado = ''
    original = ''
    for key in request.files:
        archivo_in = request.files[key]
        original = secure_filename(archivo_in.filename)
        import random
        import datetime
        current_time = datetime.datetime.now()
        horita = current_time.strftime('%H_%M_%S')
        ruleta = str(int(random.uniform(15, 99999))).zfill(5)
        extension_actual = "xls"
        if original.endswith(".xlsx"):
            extension_actual = "xlsx"
        renombrado = fox.db.uf.pi.contri + ' ' + horita + ' ' + fox.db.uf.pi.periodo_inicial.replace('-', '') + ' ' + fox.db.uf.pi.periodo_final.replace('-', '') + ""
        renombrado += fox.db.uf.pi.usuario + " " + ruleta + f' LIS.{extension_actual}'
        estadisticas["archivo_nombre"] = renombrado

    if not fox.db.uf.informante.detener and len(renombrado) > 16:
        estadisticas_parcial = fox.xl.tratar_listado(archivo_in, renombrado, params)

    end = timer()
    estadisticas["num_tramites_nuevos"] = fox.uf.his.num_tramites_encontrados
    estadisticas["num_declaraciones"] = fox.uf.his.num_declaraciones_subjetivas
    estadisticas["num_semestrales"] = fox.uf.his.numeros_semestrales_subjetivas
    estadisticas["num_terceros"] = fox.uf.his.num_terceros_subjetivos
    estadisticas_parcial["periodo_inicial"] = fox.uf.pi.periodo_inicial
    estadisticas_parcial["periodo_final"] = fox.uf.pi.periodo_final
    estadisticas_parcial["contri"] = fox.uf.pi.contri

    if len(estadisticas_parcial) > 0:
        estadisticas.update(estadisticas_parcial)
    else:
        estadisticas["fecha_ejecucion"] = fox.db.get_fecha_ymd_hms()
        estadisticas["numero_filas"] = 0
        estadisticas["guardado"] = 0
        estadisticas["num_columnas"] = 0
        estadisticas["num_vacios_vr"] = 0
        estadisticas["num_vr_no_numericos"] = 0
        estadisticas["num_con_errores"] = 1
        estadisticas["monto_analizar"] = 0
        estadisticas["archivo_nombre"] = original

    estadisticas["tiempo_carga"] = str(timedelta(seconds=end-start))
    fox.uf.his.time_procesa_excel = estadisticas["tiempo_carga"]
    if int(num_axxes) == int(fox.db.uf.pi.num_acceso):
        num_acceso = int(fox.db.uf.pi.num_acceso)
    else:
        num_acceso = num_axxes
        session["num_acceso"] = num_acceso
    if session.get('num_acceso') is not None:
        num_acceso = int(session['num_acceso'])
        estadisticas["num_acceso"] = num_acceso
    print(f" num_acceso {num_acceso} estadisticas  {fox.db.uf.GREEN}  {estadisticas}   {fox.db.uf.RESET}")
    fox.db.guardar_dataframe_pg(pd.DataFrame(estadisticas, index=[0]), fox.db.config.TB_PG_DEV_ESTADISTICA_BASE, fox.db.config.TB_PG_ESQUEMA_PUBLIC)
    fox.uf.his.num_acceso = num_acceso
    session["his"] = fox.db.uf.his.__dict__
    session["num_acceso"] = fox.uf.his.num_acceso
    fox.db.uf.pi.df = ''
    fox.db.uf.pi.tramite = ''
    session["jd"] = fox.db.uf.pi.__dict__
    session.modified = True
    sostener_air(fox.db.uf.pi.usuario, num_axxes, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    resultado = {
        "novedades": fox.db.uf.informante.razones,
        "stop": fox.db.uf.informante.detener
     }
    return json.dumps(resultado, default=str, ensure_ascii=False)


@papel_trabajo_scope.route("papeles/get_informe/<tiempo>/<espacio>/<u>/<bu>",
                           methods=['GET', 'POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_informe(tiempo, espacio, u, bu):
    '''reporte '''
    resultado = {"stop": -100}
    params = {}
    if espacio == "19042008":
        espacio = ''
    params["param5"] = espacio
    params["usuario"] = u
    session["usuario_cad_iva"] = u
    u, a, c = fox.db.uf.is_dupla(params["usuario"], bu)
    if not c:
        return resultado
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    if num_axxes < 1 or num_axxes != int(bu):
        return resultado
    mensaje = mensaje.strip()+''
    if num_axxes == int(bu):
        fox.db.uf.pi.num_acceso = num_axxes

    descifrado = fox.db.uf.desfragmentar(tiempo)
    renderizado = {}
    if len(descifrado) == 4:
        if len(fox.db.uf.pi.tramite) > 5 and len(fox.db.uf.pi.tramite) < 25:
            params["param5"] = fox.db.uf.pi.tramite

        params["param2"] = descifrado[0]
        params["param3"] = descifrado[1]
        params["param1"] = descifrado[2]
        params["memoria"] = descifrado[3]
        fox.db.uf.re_mapeado(params)
        renderizado = fox.ares.reporte()
    return renderizado


@papel_trabajo_scope.route("papeles/upd_anywhere", methods=['GET', 'POST'])
@login_required
@cross_origin(supports_credentials=True)
def upd_anywhere():
    '''actualizar valores'''
    params = request.get_json()
    retorno = {"valida": -100}
    u, a, c = fox.db.uf.is_dupla(params["usuario"], params["mu"])
    if not c:
        return retorno
    num_axxes, mensaje = sostener_air(u, a, "", "", "", "recargar")
    fox.db.uf.re_mapeado(params)
    if num_axxes < 1:
        return retorno
    mensaje = mensaje + ''
    nupy = fox.neutrones.fusionar()
    sostener_air(fox.db.uf.pi.usuario, num_axxes, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    return nupy


@papel_trabajo_scope.route("papeles/save_anywhere", methods=['GET', 'POST'])
@login_required
@cross_origin(supports_credentials=True)
def save_anywhere():
    '''guardar un dato'''
    retorno = {"valida": -100}
    params = request.get_json()
    u, a, c = fox.db.uf.is_dupla(params["usuario"],  params["mu"])
    if not c:
        return retorno
    num_axxes, mensaje = sostener_air(u, a,  "", "", "",  "recargar")
    fox.db.uf.re_mapeado(params)
    if num_axxes < 1:
        return retorno
    nupy = fox.neutrones.fisionar()
    mensaje = mensaje + ''
    sostener_air(fox.db.uf.pi.usuario, num_axxes, fox.db.uf.pi.__dict__, fox.db.uf.his.__dict__, "", "actualizar")
    return nupy


@papel_trabajo_scope.route("papeles/get_df/<tiempo>/<uname>/<dim>", methods=['GET', 'POST'])
@login_required
@cross_origin(supports_credentials=True)
def get_df(tiempo, uname, dim):
    '''recuperar informacion'''
    retorno = {"valida": -100}
    params = {}
    posible_usuario = ro.get_current_user(request)

    if current_user.is_authenticated:
        login_user(posible_usuario, remember=True)

    if posible_usuario:
        ro.get_obsolencia(posible_usuario)

    params["ufuf"] = tiempo
    params["usuario"] = fox.db.uf.pi.usuario
    params["num_acceso"] = fox.db.uf.pi.num_acceso
    u, a, c = fox.db.uf.is_dupla(params["usuario"], fox.db.uf.pi.num_acceso)
    if not c:
        return retorno
    num_axxes, mensaje = sostener_air(u,
                                      a,
                                      "",
                                      "",
                                      "",
                                      "recargar",
                                      incluir_dics=False)
    fox.db.uf.re_mapeado(params)
    _sql = Reportes.Globales(fox.db.uf.pi)
    _sql.nav = fox.db.uf.navegante
    mensaje = mensaje + ''
    if num_axxes < 1:
        return retorno
    nupy = fox.neutrones.volcado(_sql)
    return nupy
