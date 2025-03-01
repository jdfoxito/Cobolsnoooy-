"""fechas, formato fecha
Funcionalidades:

  -  Separacion por tema de import y encoder

    +-------------------+-------------------+-------------------------------+
    | Fecha             | Modifier          | Descripcion                   |
    +-------------------+-------------------+-------------------------------+
    | 15OCT2023         | jagonzaj          |   se separa por los import    |
    +-------------------+-------------------+-------------------------------+

ESTANDAR PEP8

"""

from datetime import datetime
import math


def celda_valor(celda):
    '''valor en celda html'''
    valor = 0.00
    if isinstance(celda, str):
        celda = celda.replace(",", ".")
        celda = celda.replace("$", "")
        if sea_texto_real(celda):
            valor = redondear(float(celda), 2)
        else:
            valor = 0.00
    elif sea_texto_real(str(celda)):
        valor = redondear(float(str(celda)), 2)

    return valor


def wfx(base):
    '''wrap para depuracion valor'''
    return celda_valor(base)


def val_en(diccionario, posicion):
    '''Valor en el diccionario de entrada, '''
    valor = 0
    if posicion in diccionario:
        valor = wfx(diccionario.get(posicion))

    return valor


def sea_texto_real(texto):
    '''sea texto real'''
    valor = False
    if texto.replace('.', '', 1).replace("-", '', 1).isdigit()\
            and texto.count('.') < 2:
        valor = True
    return valor


def redondear(number, decimal=0):
    '''redondear '''
    tens = 10.0
    half_way = 0.5
    if not isinstance(decimal, int):
        raise TypeError("Argument 'decimal' debe ser int ")

    if decimal == 0:
        return math.floor(number + half_way)

    multiples = math.pow(tens, decimal)
    return math.floor(number * multiples + half_way) / multiples


def a_dos(num):
    '''wrap por longitudes a 2 '''
    return redondear(float(num), 2)


def a_tres(num):
    '''wrap por longitudes a 3 '''
    return redondear(num, 3)


def meses(mes):
    '''configuracion meses '''
    mmes = 'no aplica mes'
    match int(mes):
        case 1: mmes = 'Enero'
        case 2: mmes = 'Febrero'
        case 3: mmes = 'Marzo'
        case 4: mmes = 'Abril'
        case 5: mmes = 'Mayo'
        case 6: mmes = 'Junio'
        case 7: mmes = 'Julio'
        case 8: mmes = 'Agosto'
        case 9: mmes = 'Septiembre'
        case 10: mmes = 'Octubre'
        case 11: mmes = 'Noviembre'
        case 12: mmes = 'Diciembre'

    return mmes


def nub(celda):
    '''valor en celda html'''
    valor = 0.00
    if isinstance(celda, str):
        celda = celda.replace(",", ".")
        celda = celda.replace("$", "")
        if sea_texto_real(celda):
            valor = a_dos(celda)
        else:
            valor = 0.00
    elif sea_texto_real(str(celda)):
        valor = a_dos(celda)

    return valor


class Momentos:
    '''obtener la fecha'''
    @staticmethod
    def get_fecha_ymd_hms() -> str:
        '''conseguir fecha hoy'''
        date_time = datetime.fromtimestamp(datetime.now().timestamp())
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_fecha_10() -> str:
        '''fecha en formato 10 c'''
        fecha = datetime.fromtimestamp(datetime.now().timestamp())
        return fecha.strftime("%Y-%m-%d")

    @staticmethod
    def get_fecha_ymd() -> str:
        '''fecha en formato completo '''
        fecha = datetime.fromtimestamp(datetime.now().timestamp())
        return fecha.strftime("%Y-%m-%d %H:%M:%S")
