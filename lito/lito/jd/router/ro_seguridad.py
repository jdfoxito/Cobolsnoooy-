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


from datetime import datetime
from pyrfc3339 import generate
import pandas
import time
from os import urandom
import random

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import session, make_response
from flask_login import login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from model import Tradicional
from jd import db, fox
from router import ro
from datos import Tableros

pages = Blueprint('pages',
                  __name__,
                  template_folder='templates',
                  static_folder='static')


@pages.route('/authentication/auth-pass-change-basic')
@login_required
def auth_pass_change_basic():
    '''autenticacion basica'''
    if fox.db.uf.pi.usuario == "usuario":
        return render_template('pages/account/login.html')
    return render_template('pages/authentication/auth-pass-change-basic.html')


@pages.route('/authentication/auth-pass-change-basic', methods=['POST'])
@login_required
def auth_pass_change_basic_post():
    '''cambio de clave'''
    if request.method == 'POST':
        try:
            usuario_actual = current_user.username
            txt_pass_a = request.form.get('txt_pass')
            txt_pass_b = request.form.get('txt_pass_confirma')
            if usuario_actual != fox.db.uf.pi.usuario:
                fox.db.uf.pi.usuario = usuario_actual
            if txt_pass_a == txt_pass_b:
                usuario = \
                    Tradicional.User.query.filter_by(username=fox.db.uf.pi.usuario).first()
                usuario.password = \
                    generate_password_hash(txt_pass_b.strip(), method="scrypt")
                db.session.add(usuario)
                db.session.commit()
        except Exception as ex:
            redirect(render_template('pages/account/login.html'))
            print(ex)
    return redirect(url_for('dashboards.index'))


@pages.route('/account/login')
def login():
    '''entrada al aplicativo'''
    posible_usuario = ro.get_current_user(request)
    if posible_usuario:
        if current_user and not current_user.is_authenticated and "is_active" in current_user.__dict__:
            print(f"current_user --> {current_user.__dict__}")
            login_user(posible_usuario, remember=True)

        # print(f" 80 LOGIN PASAS posible_usuario --> {posible_usuario.__dict__}")
        ro.get_obsolencia(posible_usuario)

        #print(f"86 REDIRECT ---> {url_for('dashboards.index')} ")
        #return redirect(url_for('dashboards.index'))
        # return redirect(url_for('pages.login'))
        # return ro.get_link_login()
    # else:
        #response1 = make_response(render_template("pages/account/login.html", cookies=request.cookies, year=2024))
        #response1.delete_cookie("remember_token")
        #response1.delete_cookie(fox.db.config.COOKIE_SESSION_ID_KEY)

        # response1 = make_response(render_template("dashboards/index.html", cookies=request.cookies))
        # response1.delete_cookie("remember_token")
        # response1.delete_cookie(fox.db.config.COOKIE_SESSION_ID_KEY)

        # print("85 redireccionando login post ")
    return ro.get_link_login()



@pages.route('/account/login', methods=['POST'])
def login_post():
    '''revision de usuario se ha conectado correctamente'''
    # resp = make_response(render_template('pages/account/login.html'))
    if request.method == 'POST':
        try:
            session["usuario_cad_iva"] = ''
            session["username"] = ''
            session["his"] = ''
            session["jd"] = ''
            session["num_acceso"] = -1
            session["now"] = time.time() * 100.0
            session.modified = True
            usuario_entra = request.form.get('username')
            password = request.form.get('password')
            fox.db.uf.pi.ipv4 = request.access_route[-1]
            user = \
                Tradicional.User.query.filter_by(username=usuario_entra).first()
            if not user or not check_password_hash(user.password, password):
                flash("Credenciales Invalidas")
                return redirect(url_for('pages.login'))

            fox.db.uf.pi.usuario = user.username
            session["usuario_cad_iva"] = fox.db.uf.pi.usuario
            fox.db.uf.navegante.id = user.id

            # cifras = random.randint(8, 14) << 2 >> 2
            # conf = urandom(cifras)
            # session["SECRET_KEY"] = conf

            session["_user_id"] = user.id
            fox.db.uf.navegante.email = user.email
            fox.db.uf.navegante.password = user.password
            fox.db.uf.navegante.username = user.username
            fox.db.uf.navegante.cedula = user.cedula
            fox.db.uf.navegante.nombre = user.nombre
            fox.db.uf.navegante.cargo = user.cargo
            fox.db.uf.navegante.perfil = user.perfil
            fox.db.uf.navegante.modulo = user.modulo
            fox.db.uf.navegante.opcion = user.opcion
            fox.db.uf.navegante.codreg = user.codreg
            fox.db.uf.navegante.jurisdiccion = user.jurisdiccion
            fox.db.uf.navegante.provincia = user.provincia
            fox.db.uf.navegante.canton = user.canton
            fox.db.uf.navegante.ubicacion = user.ubicacion
            fox.db.uf.navegante.grupo = user.grupo
            fox.db.uf.navegante.supervisor = user.supervisor
            fox.db.uf.navegante.departamento = user.departamento
            login_user(user, remember=True)
            fox.db.uf.pi.fecha_hoy_ts = fox.db.get_fecha_ymd_hms()
            acceso = {"usuario": [fox.db.uf.pi.usuario],
                      "ipv4": [fox.db.uf.pi.ipv4],
                      "fecha_ingreso": [fox.db.uf.pi.fecha_hoy_ts],
                      "estado": [1]}
            df_acceso = pandas.DataFrame.from_dict(acceso)
            fox.db.uf.pi.num_acceso = \
                fox.db.guardar_dataframe_pg(df_acceso,
                                            "dev_accesos_portal",
                                            "public")
            fox.db.uf.pi.num_acceso = \
                int(fox.db.get_scalar(fox.nupy.get_sql_acceso_numero()))
            fox.db.uf.navegante.num_acceso = fox.db.uf.pi.num_acceso
            aente = str(request.headers.get('User-Agent'))
            current_user.__setattr__("num_acceso", fox.db.uf.pi.num_acceso)
            session["num_acceso"] = fox.db.uf.pi.num_acceso
            acceso_num = "usuario_" + str(fox.db.uf.pi.num_acceso)
            navy = fox.db.uf.navegante.__dict__
            j = fox.db.uf.pi.__dict__
            h = fox.db.uf.his.__dict__
            print(f""" 125 LOGIN POST fox.db.uf.pi.usuario  {fox.db.uf.pi.usuario}
                        fox.db.uf.pi.num_acceso   {fox.db.uf.pi.num_acceso}""")
            num_acceso, j, h, n, mensaje = \
                fox.db.set_particula_live(fox.db.uf.pi.usuario,
                                          fox.db.uf.pi.num_acceso,
                                          j,
                                          h,
                                          navy,
                                          aente,
                                          "ingreso")
            session["notice"] = mensaje
            del navy["password"]
            session[acceso_num] = navy

            print(f"""acceso en login {fox.db.uf.pi.num_acceso}
                        num_acceso  {num_acceso}  """)
            # 1 n = n + 1
        except Exception as ex:
            print(f"130 login {ex}")
            return ro.get_link_login()
        session.modified = True
    return redirect(url_for('dashboards.index'))

@pages.route('/account/signup')
def signup():
    '''alta de usuario previa '''
    return render_template('pages/account/signup.html')


@pages.route('/account/signup', methods=['POST'])
def signup_post():
    '''alta de usuario'''
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    if len(username.strip()) == 0:
        flash("Debe ingresar un usuario!")
        return redirect(url_for('pages.signup'))

    if len(email.strip()) == 0:
        flash("Debe ingresar un mail!")
        return redirect(url_for('pages.signup'))

    user_email = Tradicional.User.query.filter_by(email=email).first()
    user_username = Tradicional.User.query.filter_by(username=username).first()

    if user_email:
        flash("User email already Exists")
        return redirect(url_for('pages.signup'))
    if user_username:
        flash("Username already Exists")
        return redirect(url_for('pages.signup'))
    new_user = Tradicional.User(email=email,
                                username=username,
                                password=generate_password_hash(password,
                                                                method="sha256"))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('pages.login'))


def salir():
    ''' salir '''
    session.clear()
    # logout_user()
    session["usuario_cad_iva"] = ''
    current_dateTime = datetime.now()
    year = current_dateTime.date().year
    resp = make_response(render_template('pages/account/login.html', year=year))
    try:
        resp.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, '', max_age=0, expires=0)
        resp.delete_cookie("remember_token")
        resp.delete_cookie(fox.db.config.COOKIE_SESSION_ID_KEY)
        # request.set_cookie(fox.db.config.COOKIE_SESSION_ID_KEY, '', max_age=0, expires=0)
    except Exception as ex:
        print(ex)
        return resp
    return resp

@pages.route('/account/logout')
@login_required
def logout():
    '''salida'''
    return salir()
