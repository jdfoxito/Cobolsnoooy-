"""Tradicional, desde Diciembre 2022
Funcionalidades:
  - Entidad para manejar la informacion del usuario.

+-------------+------------+--------------------------------------------------+
| Fecha       | Modifier   | Descripcion                                      |
+-------------+------------+--------------------------------------------------+
| 22FEB2022   | jagonzaj   |   la clase se crea con la appp flas para         |
|             |            |     manejar los usuarios logueados               | 
| 15ENE2024   | jagonzaj   |   se agreagan los metos is active,               |
|             |            |     get_id, is_autenticade                       |
+-------------+------------+--------------------------------------------------+

ESTANDAR PEP8
"""
from flask_login import UserMixin
from jd import db


class User(db.Model, UserMixin):
    '''modelado'''
    __tablename__ = 'dev_usuario_cad_iva'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    cedula = db.Column(db.String(13), unique=True)
    nombre = db.Column(db.String(512), unique=True)
    cargo = db.Column(db.String(1024), unique=True)
    perfil = db.Column(db.String(64), unique=True)
    supervisor = db.Column(db.String(512), unique=True)
    modulo = db.Column(db.String(256), unique=True)
    opcion = db.Column(db.String(512), unique=True)
    codreg = db.Column(db.String(16), unique=True)
    jurisdiccion = db.Column(db.String(256), unique=True)
    provincia = db.Column(db.String(512), unique=True)
    canton = db.Column(db.String(512), unique=True)
    ubicacion = db.Column(db.String(1024), unique=True)
    grupo = db.Column(db.String(1024), unique=True)
    departamento = db.Column(db.String(1024), unique=True)

    jd = {}
    his = {}
    num_acceso = -1
    is_active: bool = True

    def get_id(self):
        '''get id'''
        return self.id

    # @property
    # def is_active(self):
    #    '''si esta activo el usuario'''
    #    return True

    @property
    def is_authenticated(self):
        '''es autenticado'''
        return self.is_active

    @property
    def is_anonymous(self):
        '''--> es anonimo'''
        return False
