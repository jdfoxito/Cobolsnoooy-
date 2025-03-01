"""Navegante, desde Septiembre 2023
Funcionalidades:
  - Entidad espejo para comparativas.

ESTANDAR PEP8
REVISADO CON SONARLINT 4.3.0 (Exluida la regla de longitud minima de
lineas en una funcion,
y la longitud de linea se trabaja con 240 caracteres)"""


class Navegante(object):
    '''clase de usuario que va accediendo'''
    id = 0
    email = ''
    password = ''
    username = ''
    cedula = ''
    nombre = ''
    cargo = ''
    perfil = ''
    modulo = ''
    opcion = ''
    codreg = ''

    jurisdiccion = ''
    provincia = ''
    canton = ''

    ubicacion = ''
    grupo = ''
    departamento = ''

    nombre_analista = ''
    usuario_analista = ''

    nombre_supervisor = ''
    usuario_supervisor = ''
    supervisor = ''
    ipv4 = ''
    num_acceso = -1

    def __init__(self, diccionario):
        '''constructor principal'''
        if len(diccionario) > 0:
            for key in diccionario:
                setattr(self, key, diccionario[key])
