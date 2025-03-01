"""servicios, desde Noviembre 2022
Funcionalidades:
  - Sirve para comerciar la informacion via json entre el navegador y el
    servidor.

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

e inician las validaciones del contri

 - fn(login_required)                   solicta que el usuario este logueado
 - fn(sostener_air)                     recarga las acciones de cada usuario
 - fn(get_declaraciones_periodo)        trae las declaraciones
 - fn(cargar_retenciones_ini())         lee el archivo de excel

+-------------+-------------+------------------------------------------------+
| Fecha       | Modifier    | Descripcion                                    |
+-------------+-------------+------------------------------------------------+
| 30NOV2022   | jagonzaj    |   Trabajo sin ssl via sessiones,               |
| 15DIC2023   | jagonzaj    |   se cambia a tabla el manejo de variables     |
|             |             |   de memoria                                   |
+-------------+-------------+------------------------------------------------+

PATTERN MEDIATOR

Mediator es un patrón de diseño de comportamiento que reduce el acoplamiento
entre los componentes de un, programa haciendo que se comuniquen indirectamente
a través de un objeto mediador especial.

...................:.  .............................   ......................:
.::.-..............:.  ..........::::...............   :.........:.::........:
.::::::-=::........:.  .........:::::::--::.........   :........::.::::=-:...:
::::::::::::::::::::. ..::::::::::::::::::::::::::::.  :::::::::::::::::::::::
...................:.  .............................   :.....................:
.::-:-----....::...:.  ..........-----:---..........   :...:-....:----==-:...:
...............-...:.  .............................   :....=................:
...............:.....  ..............:..............   .....-........=:......:
                     :                     :                      -        ..
                     :                     :                      -        ..
                     :                     :                      -        ..
                     :                     :                      -        ..
                     :                     :                      -        ..
                     :                    :*:                     -        ..
                     :       .............................        -        ..
                     :     ...:::::::::::::::::::::::::::: ..     -        ..
                     ......:-.::::+===+===++-++++++++-::::.:-......        ..
                             .::::::::::::::::::::::::::::                 ..
                            ..::::::::::::::::::::::::::::                 ..
                             .::--:::::::::::::::::--:=--:...................
                             .:::-::::::::::::::::::-:::::
                             ..:::-::::-:::::::-:::::-::::
                                    :   .=.    .:-.   ..
.....................      :    :      ..    ..        .......................
..................:.      :    :      ..    ..        :......................:
.--=--==:=:.......:..*....:    :      ..    .......=-.:........==:=---=---...:
..................:.           :      ..           .. :......................:
..................:.           :      ..              :......................:
.--:=-=-:.....::..:.           :      ..              :.........--:---=-:....:
...... ...........:.                                  :......................:
.:::::::::::::::::::.                                  .::::::::::::::::::::::

ESTANDAR PEP8
TODO Webservice entry point: https://[IPV4]/papeles/validarpapelito
"""

from flask import render_template, redirect, session, request, Blueprint
from flask_login import login_required, current_user, login_user
from jd import fox
from router import ro

papel_portal = Blueprint('papeles', __name__, template_folder='templates', static_folder='static')
from model import Tradicional


def get_obsolencia(user):
    '''elimina sobreescritura'''
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


@papel_portal.route('/papeles/validarpapelito')
@login_required
def validapapel():
    '''encadenamiento: #validar papel '''
    intervalos = {}
    usuario = 'usuario'

    posible_usuario = ro.get_current_user(request)
    if posible_usuario:
        ro.get_obsolencia(posible_usuario)
    else:
        return ro.get_link_login()

    if not current_user.is_authenticated:
        login_user(posible_usuario, remember=True)

    try:
        usuario_actual = ''
        if session.get('usuario_cad_iva') is not None:
            usuario_actual = session.get('usuario_cad_iva')
        if usuario_actual == "":
            usuario_actual = current_user.username
        if session.get('num_acceso') is not None:
            if int(session.get('num_acceso')) != -1:
                fox.db.uf.pi.num_acceso = int(session.get('num_acceso'))
                fox.db.uf.navegante.num_acceso = fox.db.uf.pi.num_acceso
        else:
            session["num_acceso"] = fox.db.uf.pi.num_acceso

        from datetime import datetime, timedelta
        hace5 = str((datetime.now() - timedelta(days=30*12*6)).strftime('%Y-%m'))
        mesanterior = str((datetime.now() - timedelta(days=60)).strftime('%Y-%m'))
        mesactual = str((datetime.now()).strftime('%Y-%m'))
        if fox.db.uf.pi.usuario == "usuario" or fox.db.uf.pi.usuario == '' or usuario_actual != current_user.username:
            return render_template('pages/account/login.html')
        fox.db.uf.pi.usuario = current_user.username
        user = Tradicional.User.query.filter_by(username=fox.db.uf.pi.usuario).first()
        if not user:
            return render_template('pages/account/login.html')

        get_obsolencia(user)
        usuario = fox.db.uf.pi.usuario

        fox.db.uf.pi.ipv4 = request.access_route[-1]
        num_acceso_real = fox.db.get_scalar(fox.nupy.get_sql_acceso_numero())
        if fox.db.uf.pi.num_acceso != num_acceso_real:
            fox.db.uf.pi.num_acceso = num_acceso_real
    except Exception as ex:
        print(ex)
        redirect(render_template('pages/account/login.html'))

    intervalos = {"usuario": usuario,
                  "hace5": hace5,
                  "mesanterior": mesanterior,
                  "mesactual": mesactual,
                  "nombre": fox.db.uf.navegante.nombre,
                  "perfil": fox.db.uf.navegante.perfil,
                  "cargo": fox.db.uf.navegante.cargo,
                  "num_acceso": fox.db.uf.pi.num_acceso}

    session.modified = True
    print(f" papelito  current_user.username  {current_user.username } fox.db.uf.pi.usuario   {fox.db.uf.pi.usuario} acceso {fox.db.uf.pi.num_acceso} ses NUMACCESO {session["num_acceso"]} ")

    # headers = {'Content-Type': 'multipart/form-data'}
    return render_template('papeles/validar-papeles.html', intervalos=intervalos, num_acceso=fox.db.uf.pi.num_acceso)


@papel_portal.route('/papeles/tramites')
@login_required
def listatramites():
    '''Lista de tramites'''
    usuario = 'usuario'
    intervalos = {}
    # res_salir = None

    posible_usuario = ro.get_current_user(request)
    if posible_usuario:
        ro.get_obsolencia(posible_usuario)
    else:
        return ro.get_link_login()

    if not current_user.is_authenticated:
        login_user(posible_usuario, remember=True)

    try:
        if session.get('num_acceso') is not None:
            if int(session.get('num_acceso')) != -1:
                fox.db.uf.pi.num_acceso = int(session.get('num_acceso'))
                fox.db.uf.navegante.num_acceso = fox.db.uf.pi.num_acceso
        else:
            session["num_acceso"] = fox.db.uf.pi.num_acceso

        if fox.db.uf.pi.usuario == "usuario" or fox.db.uf.pi.usuario == '':
            return render_template('pages/account/login.html')
        fox.db.uf.pi.usuario = current_user.username
        user = Tradicional.User.query.filter_by(username=fox.db.uf.pi.usuario).first()
        if not user:
            return render_template('pages/account/login.html')
        get_obsolencia(user)
        usuario = fox.db.uf.pi.usuario
        fox.db.uf.pi.ipv4 = request.access_route[-1]
        num_acceso_real = fox.db.get_scalar(fox.nupy.get_sql_acceso_numero())
        if fox.db.uf.pi.num_acceso != num_acceso_real:
            fox.db.uf.pi.num_acceso = num_acceso_real
            session["num_acceso"] = fox.db.uf.pi.num_acceso
            fox.db.uf.navegante.num_acceso = fox.db.uf.pi.num_acceso
    except Exception as ex:
        print(ex)
        redirect(render_template('pages/account/login.html'))

    p1 = 'Aprobados'
    p2 = 'Finalizados'
    p3 = 'Enviados'
    p4 = 'No Aprobados'

    if fox.db.uf.navegante.perfil in ['Supervisor', 'Administrador']:
        p1 = 'Pendientes de Aprobar'
        p2 = 'Aprobados'
        p3 = 'Rechazados'
        p4 = 'Duplicados'

    intervalos = {"usuario": usuario,
                  "nombre": fox.db.uf.navegante.nombre,
                  "perfil": fox.db.uf.navegante.perfil,
                  "cargo": fox.db.uf.navegante.cargo,
                  "p1": p1,
                  "p2": p2,
                  "p3": p3,
                  "p4": p4,
                  "num_acceso": fox.db.uf.pi.num_acceso}
    return render_template('papeles/tramites.html', intervalos=intervalos, p1=p1, p2=p2, p3=p3, p4=p4)

@papel_portal.route('/papeles/informe_revision')
@login_required
def informe_revision():
    '''#validar papel'''
    from datetime import datetime, timedelta
    usuario = current_user.username
    # desde
    hace5 = str((datetime.now() - timedelta(days=30*12*6)).strftime('%Y-%m')) 
    mesanterior = str((datetime.now() - timedelta(days=60)).strftime('%Y-%m'))
    # hasta
    mesactual = str((datetime.now()).strftime('%Y-%m'))
    intervalos = {"usuario": usuario, "hace5": hace5, "mesanterior": mesanterior, "mesactual": mesactual}
    return render_template('papeles/informe-revision.html', intervalos=intervalos)
