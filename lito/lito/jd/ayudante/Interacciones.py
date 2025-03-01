"""Interacciones, desde Enero 2023
Funcionalidades:
  - Entidades con sus propiedades para alimentar todo el flujo de un caso.

COMPORTAMIENTO:
 - fn(varias)              Son depuraciones en la informacion de entrada
                            a nivel servidor
 - fn(fragmentar)          Crea un string con un ocultamiento de informacion
 - fn(desfragmentar)       Traduce un strin previamente fragmentado
 - fn(abot)                Cifra una porcion de texto
 - fn(costelo)             Descifra una porcion de texto

+------------+-----------+----------------------------------------------------+
| Fecha      | Modifier  | Descripcion                                        |
+------------+-----------+----------------------------------------------------+
| 15DIC2022  | jagonzaj  |   Se agrega comportamiento general                 |
| 19ABR2023  | jagonzaj  |   Se agrega funciones parar cifrar los links,      |
|            |           |         y usarlo en el javascript                  |
+------------+-----------+----------------------------------------------------+

ESTANDAR PEP8

"""


import os
import nh3
import pandas
import numpy
import math
from datetime import datetime, timedelta
from ayudante import Celebridades, Juez
from decimal import *
from datetime import date
from dateutil.relativedelta import relativedelta
os.system("")


class param_historia(object):
    '''historia'''

    def __init__(self, diccionario):
        '''constructor principal'''
        self.num_tramites_encontrados = 0
        self.num_tramites_objetivos = 0

        self.num_declaraciones_subjetivas = 0
        self.num_decla_mensual_subjetivas = 0
        self.numeros_semestrales_subjetivas = 0
        self.num_terceros_subjetivos = 0

        self.num_declas_objetivas_mensual = 0
        self.num_declas_periodos_analizados = 0

        self.num_declaraciones_cumplen = 0
        self.num_declaraciones_no_cumplen = 0

        self.num_excel_filas = 0
        self.num_excel_val_ret_blanks = 0
        self.num_excel_val_ret_invalid = 0
        self.monto_excel_identificado = 0

        self.num_excel_fec_emi_invalid = 0
        self.num_excel_num_fails = 0
        self.num_providencias = 0
        self.num_excel_col_val_ret_invalid = 0

        # tiempos
        self.time_procesa_excel = ''
        self.time_excel_a_db = ''
        self.time_procesa_cadena = ''

        self.time_inicia = ''
        self.time_elige_declas_nc = ''
        self.time_providencia = ''
        self.time_graba_cadena = ''
        self.time_graba_memoria = ''

        # snt
        self.snt_fecha_ingreso = ''
        self.snt_monto_solicitado = 0
        self.snt_monto_a_devolver = 0

        # montos
        self.monto_a_devolver_calculado = 0

        # conteos
        self.num_fantasmas = 0
        self.num_fallecidos = 0
        self.num_ffpv = 0
        self.num_descartados = 0
        self.num_acceso = 0

        self.frecuenciamiento = 'SO FAR'

        if len(diccionario) > 0:
            for key in diccionario:
                setattr(self, key, diccionario[key])


class param_espejo():
    '''clase espejo'''
    contri = ''
    periodo_inicial = ''
    periodo_final = ''
    tramite = ''
    usuario = ''


class param_iva(object):
    '''clase parametros principales'''
    contri = ''
    contri_real = ''
    periodo_inicial = ''
    periodo_final = ''
    periodo_inicial_org = ''
    periodo_final_org = ''
    ipv4 = ''
    periodo_finalisima = ''
    usuario = ''
    escena = ''
    tramite = ''
    adhesivos = ''
    adhesivo = ''
    valores_arrastre_p6 = []
    valores_analizados_p7 = []
    valores_analizados_6_7_am = []
    compensa = ''
    adquisiciones_txt = 0.0
    retenciones_txt = 0.0
    grabar = 0
    fecha_hoy = ''
    fecha_hoy_ts = ''
    suma_arrastre = 0.0
    suma_analisis = 0.0
    anio = 0
    mes = 0
    cuerda = 0
    razon_social = ''
    df = ''
    df_periodos_talves = ''
    prefijo = ''
    adquisiciones_normal = 0.0
    contri_abot = ''
    el_diez = 0.0
    el_once = 0.0
    expediente = 0
    num_acceso = 0
    observaciones = ''
    tabla_esquema = ''
    tabla_relacional = ''
    esquema = ''
    campo_primario = ''
    huesped = ''
    mayoriza_ajuste = 0.0
    no_sustentado = 0.0
    and_errante = ''
    procedencia = ''
    tercero = ''
    autorizacion_tercero = ''
    fecha_tercero = ''
    secuencia_tercero = ''
    ufuf = ''
    memoria = 0

    # procesamientos
    time_informe_revision = ''
    num_retenciones_proce = 0
    num_retenciones_dupli = 0
    num_retenciones_excel = 0

    def __init__(self, diccionario):
        if len(diccionario) > 0:
            for key in diccionario:
                setattr(self, key, diccionario[key])


class Colores:
    '''pintado '''
    peach = "00CCFFCC"
    negro = '00000000'
    blanco = '00FFFFFF'
    rojo = '00FFFF00'
    sri = '00000080'
    lavender = '00CCCCFF'
    azul = '1072BA'


class Recepcion(param_iva, Colores):
    '''parametros de entrada'''
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

    def mapeado_nivel_dos(self, contri):
        '''mapeado nivel 2'''
        self.pi.usuario = self.deja(contri["usuario"]) if "usuario" in contri else self.pi.usuario
        self.pi.escena = self.deja(contri["param4"]) if "param4" in contri else self.pi.escena
        self.pi.tramite = self.sea_numero(contri, "param5") if "param5" in contri else self.pi.tramite
        self.pi.adhesivos = self.sea_bonder(contri, "bonder") if "bonder" in contri else self.pi.adhesivos
        self.pi.adhesivo = self.sea_numero(contri, "adhesivo") if "adhesivo" in contri else self.pi.adhesivo
        self.pi.adquisiciones_txt = self.sea_real(contri, 'adquisiciones') if "adquisiciones" in contri else self.pi.adquisiciones_txt
        self.pi.adquisiciones_normal = self.sea_real(contri, 'adq_ingre') if "adq_ingre" in contri else self.pi.adquisiciones_normal
        self.pi.retenciones_txt = self.sea_real(contri, 'retenciones') if "retenciones" in contri else self.pi.retenciones_txt
        self.pi.grabar = self.sea_numero(contri, 'grab') if "grab" in contri else self.pi.grabar
        self.pi.expediente = self.sea_numero(contri, 'expediente') if "expediente" in contri else self.pi.expediente
        self.pi.valores_arrastre_p6 = self.sea_lista(contri, 'ufo') if "ufo" in contri else self.pi.valores_arrastre_p6
        self.pi.valores_analizados_p7 = self.sea_lista(contri, 'ufa') if "ufa" in contri else self.pi.valores_analizados_p7
        self.pi.valores_analizados_6_7_am = self.sea_lista(contri, 'ufx') if "ufx" in contri else self.pi.valores_analizados_6_7_am
        self.pi.mayoriza_ajuste = self.sea_real(contri, 'mayor_ajuste')if "mayor_ajuste" in contri else self.pi.mayoriza_ajuste
        self.pi.no_sustentado = self.sea_real(contri, 'no_sustentado')if "no_sustentado" in contri else self.pi.no_sustentado
        self.pi.memoria = self.sea_numero(contri, 'memoria')if "memoria" in contri else self.pi.memoria

    def mapeado_nivel_tres(self, contri):
        '''mapeado nivel tres'''
        edt = datetime.now()
        self.pi.fecha_hoy = str(edt.strftime("%Y-%m-%d"))
        self.pi.fecha_hoy_ts = str(edt.strftime("%Y-%m-%d %H:%M:%S"))
        self.pi.suma_arrastre = self.sea_real(contri, 'lastre') if "lastre" in contri else self.pi.suma_arrastre
        self.pi.suma_analisis = self.sea_real(contri, 'ia')if "ia" in contri else self.pi.suma_analisis
        self.pi.compensa = self.sea_texto(contri, 'agrega')if "agrega" in contri else self.pi.compensa
        self.pi.anio = self.sea_numero(contri, 'anio') if "anio" in contri else self.pi.anio
        self.pi.mes = self.sea_numero(contri, 'mes') if "mes" in contri else self.pi.mes
        self.pi.cuerda = self.sea_numero_definido(contri, 'cuerda', 10) if "cuerda" in contri else self.pi.cuerda
        self.pi.el_diez = self.sea_real(contri, 'el_diez') if "el_diez" in contri else self.pi.el_diez
        self.pi.el_once = self.sea_real(contri, 'el_once') if "el_once" in contri else self.pi.el_once
        self.pi.ipv4 = self.sea_texto(contri, 'ipv4')if "ipv4" in contri else self.pi.ipv4
        self.pi.num_acceso = self.sea_numero(contri, 'num_acceso') if "num_acceso" in contri else self.pi.num_acceso
        self.his.num_acceso = self.sea_numero(contri, 'num_acceso') if "num_acceso" in contri else self.his.num_acceso
        self.pi.observaciones = self.sea_texto(contri, 'obs')if "obs" in contri else self.pi.observaciones
        self.pi.tabla_esquema = self.sea_texto(contri, 'tabla_esquema')if "tabla_esquema" in contri else self.pi.tabla_esquema
        self.pi.tabla_relacional = self.sea_texto(contri, 'tabla_relacional')if "tabla_relacional" in contri else self.pi.tabla_relacional
        self.pi.esquema = self.sea_texto(contri, 'esquema')if "esquema" in contri else self.pi.esquema
        self.pi.campo_primario = self.sea_texto(contri, 'campo_primario')if "campo_primario" in contri else self.pi.campo_primario
        self.pi.huesped = self.sea_texto(contri, 'huesped')if "huesped" in contri else self.pi.huesped

    def re_mapeado(self, contri):
        '''mapeado'''
        if isinstance(contri, dict):
            self.pi.contri = self.sea_contribuyente(contri, 'param1') if "param1" in contri else self.pi.contri
            self.pi.ufuf = self.sea_numero_z(contri, 'ufuf') if "ufuf" in contri else self.pi.ufuf
            self.pi.periodo_inicial = self.sea_periodo(contri, 'param2', 1) if "param2" in contri else self.pi.periodo_inicial
            self.pi.periodo_final = self.sea_periodo(contri, 'param3', 2) if "param3" in contri else self.pi.periodo_final
            if len(str(self.pi.periodo_inicial)) == 10 and not self.informante.detener:
                self.pi.periodo_inicial_org = self.pi.periodo_inicial

            if len(str(self.pi.periodo_final)) == 10 and not self.informante.detener:
                self.pi.periodo_finalisima = self.get_ultimo_dia(int(self.pi.periodo_final[0:4]), int(self.pi.periodo_final[5:7]))
                self.pi.periodo_final_org = self.pi.periodo_finalisima
                self.pi.df_periodos_talves = pandas.DataFrame(pandas.date_range(start=self.pi.periodo_inicial_org, end=self.pi.periodo_final_org, freq="MS"), columns=['fecha_ini'])
                self.pi.df_periodos_talves["fecha_fin"] = pandas.DataFrame(pandas.date_range(start=self.pi.periodo_inicial_org, end=self.pi.periodo_final_org, freq="ME"), columns=['fecha_fin'])
                self.pi.periodo_final = self.pi.periodo_final_org
            self.mapeado_nivel_dos(contri)
            self.mapeado_nivel_tres(contri)

    def __init__(self, contri):
        '''constructor principal'''
        self.pi = param_iva({})
        self.his = param_historia({})
        self.espejo = param_espejo()
        self.navegante = Celebridades.Navegante({})
        self.informante = Juez.Novedades(False)
        self.re_mapeado(contri)
        self.tablas_temporales = ['dev_ruc_consultados',
                                  'dev_tramites_cons',
                                  'dev_cad_iva_procesa',
                                  'dev_cargas_archivos',
                                  'dev_cargas_archivos_nv',
                                  'dev_compensa_futuro',
                                  'dev_cuadro_liquidacion',
                                  'dev_declaraciones_validas',
                                  'dev_informe_retencion',
                                  'dev_observaciones',
                                  'dev_pre_cadena_iva',
                                  'dev_providencias_vals',
                                  'dev_resultado_analisis_retencion',
                                  'dev_resumen_analizados',
                                  'dev_resumen_cadena',
                                  'dev_resumen_periodo',
                                  'dev_resumen_resultados',
                                  'dev_resumen_verifica',
                                  'dev_analisis_previo'
                                  ]

    def redondear2(self, decimal_number, places=2):
        '''redondear'''
        resultado = 0
        if str(decimal_number)[-1] == '5':
            if places == 0:
                exp = Decimal('1')
            else:
                exp_str = '0' * places
                exp_str = exp_str[:-1] + '1'
                exp = Decimal('.{}'.format(exp_str))
            resultado = float(Decimal(decimal_number).quantize(exp, rounding=ROUND_UP))
        else:
            resultado = float(round(decimal_number, 2))
        return resultado

    def redondear(self, number, decimal=0):
        '''otro metodo de redondeo por un tem con la precision'''
        tens = 10.0
        half_way = 0.5
        if not isinstance(decimal, int):
            raise TypeError("Argument 'decimal' must be of type int")

        if decimal == 0:
            return math.floor(number + half_way)

        multiples = math.pow(tens, decimal)
        return math.floor(number * multiples + half_way) / multiples

    def fx(self, celda):
        '''buscar valores en celda'''
        valor = 0.00
        if isinstance(celda, str):
            celda = celda.replace(",", ".")
            celda = celda.replace("$", "")
            if self.sea_texto_real(celda):
                valor = self.redondear(float(celda), 2)
            else:
                valor = 0.00
        elif self.sea_texto_real(str(celda)):
            valor = self.redondear(float(str(celda)), 2)

        return valor

    def es_fx(self, celda):
        '''es celda'''
        es = False
        if isinstance(celda, str):
            celda = celda.replace(",", ".")
            celda = celda.replace("$", "")
            if self.sea_texto_real(celda):
                es = True
        elif self.sea_texto_real(str(celda)):
            es = True
        return es

    def sea_numero_definido(self, diccio, clave, limite):
        '''numero definido'''
        valor = 0
        if clave in diccio and str(diccio[clave]).isdigit():
            valor = int(self.deja(str(diccio[clave])))
            if valor > limite or valor < 0:
                valor = 0
        return valor

    def is_entero(self, numero):
        '''es entero'''
        cambio = 0
        try:
            cambio = int(numero)
        except Exception as ex:
            print(ex)
            cambio = -81
        return cambio

    def is_dupla(self, u, a):
        '''es dupla'''
        u = str(u).strip()
        a = str(a).strip()
        if (len(str(u)) > 4 and len(str(u)) < 40) and (len(str(a)) > 1 and len(str(a)) < 20):
            u = self.deja(u)
            a = self.deja(a)
            if (len(str(u)) > 4 and len(str(u)) < 40) and (len(str(a)) > 1 and len(str(a)) < 20 and str(a).isdigit()):
                return u, int(a), True
            else:
                return u, -1, False
        else:
            return u, -1, False

    def sea_numero_z(self, diccio, clave):
        '''sea numero entero'''
        valor = ''
        if clave in diccio:
            valor = self.is_entero(str(diccio[clave]))
        return valor

    def sea_numero(self, diccio, clave):
        '''sea numero'''
        valor = ''
        if clave in diccio and str(diccio[clave]).isdigit():
            valor = self.deja(str(diccio[clave]))
        return valor

    def sea_real(self, diccio, clave):
        '''sea numero real'''
        valor = ''
        if clave in diccio and str(diccio[clave]).replace('.', '', 1).replace("-", '', 1).isdigit() and str(diccio[clave]).count('.') < 2:
            valor = str(diccio[clave])
        return valor

    def sea_bonder(self, diccio, clave):
        '''sea valores ocnsecutivos'''
        valor = ''
        if clave in diccio and len(str(diccio[clave])) > 5:
            listado = str(diccio[clave])[1:].split(',')
            listado = list(map(str, listado))
            valor = "','".join(listado)
            valor = "'" + valor + "'"
        return valor

    def sea_lista(self, diccio, clave):
        '''sea una vlaor tipo lista'''
        valor = ''
        if clave in diccio and len(str(diccio[clave])) > 2:
            valor = str(diccio[clave]).replace("[", "").replace("]", "").replace(" ", "")
        return valor

    def sea_texto_real(self, texto):
        '''busqueda de nu nuemro decimal en un string formateado'''
        valor = False
        if texto.replace('.', '', 1).replace("-", '', 1).isdigit() and texto.count('.') < 2:
            valor = True
        return valor

    def sea_contribuyente(self, diccio, clave):
        '''verificacion contribuyente'''
        valor = ''
        self.informante.razones.clear()
        revisando = self.deja(str(diccio[clave]))
        if revisando == "nupy":
            return ''
        self.informante.detener = False
        if clave in diccio and revisando.isdigit():
            if revisando.endswith("001"):
                valor = revisando
            else:
                sms = f"El RUC del contri {revisando} debe terminar en 001"
                dic = {'mensaje': sms,
                       "category": "contri", "devuelve": True}
                self.informante.agregar_razones(dic)

            if len(revisando) == 13:
                valor = revisando
            else:
                sms = f"El Contri {revisando} debe terminar 13 caracteres"
                dic = {'mensaje': sms, "category": "contri", "devuelve": True}
                self.informante.agregar_razones(dic)
        else:
            sms = f"El RUC del contri {revisando} debe ser secuencia numerica"
            dic = {'mensaje': sms, "category": "contri", "devuelve": True}
            self.informante.agregar_razones(dic)

        if len(self.informante.razones) > 0:
            self.informante.detener = True
            valor = '0'

        return valor

    def sea_periodo(self, diccio, clave, extremo):
        '''verificacion periodo'''
        valor = ''
        current_date = date.today()
        inferior = current_date - relativedelta(years=10)
        sup = current_date + relativedelta(years=10)
        inferior = str(inferior)
        sup = str(sup)
        if clave in diccio and len(str(diccio[clave])) > 6 and \
                len(str(diccio[clave])) < 11:
            pre = str(diccio[clave])
            match pre.count('-'):
                case 1:
                    if extremo == 1:
                        pre = pre + '-01'
                    if extremo == 2:
                        pre = pre + '-27'
                case _:    pre = pre if len(pre) == 10 else ''

            formato = '%Y-%m-%d'
            try:

                rangofuera = datetime.strptime(pre, formato)
                match extremo:
                    case 1:
                        if rangofuera < datetime.strptime(inferior,
                                                          formato):
                            sms = f"Revisar Fecha del periodo solicitado {pre}"
                            dic = {'mensaje': sms,
                                   "category": "fechas",
                                   "devuelve": True}
                            self.informante.agregar_razones(dic)
                            self.informante.detener = True
                    case 2:
                        if rangofuera > datetime.strptime(sup, formato) or \
                                rangofuera < datetime.strptime(inferior,
                                                               formato):
                            sms = f"Revisar Fecha del periodo solicitado {pre}"
                            dic = {'mensaje': sms,
                                   "category": "fechas",
                                   "devuelve": True}

                            self.informante.agregar_razones(dic)
                            self.informante.detener = True
                valor = pre
            except Exception as ex:
                sms = f"En la Fecha {ex} en {pre} "
                dic = {'mensaje': dic,
                       "category": "fechas",
                       "devuelve": True}
                self.informante.agregar_razones(dic)
                self.informante.detener = True
                valor = ''

        return valor

    def sea_texto(self, diccio, clave):
        '''sea texto'''
        valor = ''
        if clave in diccio and len(str(diccio[clave])) > 2:
            pre = str(diccio[clave])
            if len(pre.replace('=', '').replace(">", '', 1).replace("<", '', 1)) > 2:
                valor = pre
        return valor

    def deja_pre(self,  parametro):
        '''formateado'''
        jfx = str(parametro).strip()
        jfx = jfx.replace("=", "")
        jfx = jfx.replace("&", "")
        jfx = jfx.replace("and", "")
        jfx = jfx.replace("or", "")
        jfx = jfx.replace(">", "")
        jfx = jfx.replace("<", "")
        jfx = jfx.replace("--", "")
        jfx = jfx.replace("--", "")
        return jfx

    def deja(self, parametro):
        '''cambio'''
        jfx = nh3.clean(parametro)
        jfx = str(jfx).strip()
        jfx = jfx.replace(";", "")
        jfx = jfx.replace("--", "")
        return jfx

    def abot(self, num):
        '''encriptacion particular, no se usa jwt por vulnerabilidadades'''
        vector = [0, 1]
        longitud = len(num)
        longitud = 10 if longitud == 13 else longitud
        lista = []
        for i in range(longitud):
            x = vector[0] + vector[1]
            vector[0] = vector[1]
            vector[1] = x
            coeficiente = int(str(x)[-1]) + int(num[i])
            lista.append(str(coeficiente - 10 if coeficiente >= 10 else coeficiente))
        return ''.join(lista)

    def costelo(self, num):
        '''desecnriptado'''
        vector = [0, 1]
        longitud = len(num)
        lista = []
        for i in range(longitud):
            x = vector[0] + vector[1]
            vector[0] = vector[1]
            vector[1] = x
            coeficiente = int(num[i]) - int(str(x)[-1])
            lista.append(str(coeficiente + 10 if coeficiente < 0 else coeficiente))
        return (''.join(lista))+'001'

    def get_ultimo_dia(self, year, month):
        """Regresa el ultimo dia del mes
        Args:
            Anio (int): anio, i.e. 2022
            mes (int): Mes, i.e. 1 x Enero
        Retorna:
            fecha (datetime): ultima fecha del mes
        """
        if month == 12:
            last_date = datetime(year, month, 31)
        else:
            last_date = datetime(year, month + 1, 1) + timedelta(days=-1)
        return last_date.strftime("%Y-%m-%d")

    def get_mes_nombrado(self):
        '''mes nombrado'''
        mes = 'Enero'
        if str(self.pi.mes) == '':
            self.pi.mes = -1
        match(int(self.pi.mes)):
            case 1: mes = "Enero"
            case 2: mes = "Febrero"
            case 3: mes = "Marzo"
            case 4: mes = "Abril"
            case 5: mes = "Mayo"
            case 6: mes = "Junio"
            case 7: mes = "Julio"
            case 8: mes = "Agosto"
            case 9: mes = "Septiembre"
            case 10: mes = "Octubre"
            case 11: mes = "Noviembre"
            case 12: mes = "Diciembre"
            case _: mes = ""
        return mes.upper()

    def fragmentar_h(self, a, b, c):
        '''union de partes'''
        self.pi.contri = a
        self.pi.periodo_inicial = b
        self.pi.periodo_final = c
        xc = self.abot(self.pi.contri)
        xb = []
        for periodo in [self.pi.periodo_inicial, self.pi.periodo_final]:
            periodo = str(periodo)
            if len(periodo) == 10 and periodo.count("-") == 2:
                xa = 2000
                partes = periodo.split('-')
                if len(str(partes[0])) == 4:
                    xa = int(partes[0]) - xa
                    xb.append(str(numpy.int64(xc) - numpy.int64(int(str(xa)+partes[1] + partes[2]))) + 'e')

        respuesta = ''
        if len(xb) > 1:
            respuesta = xc + xb[0] + xb[1].replace('e', '')
        return respuesta

    def fragmentar(self):
        '''union de partes corta'''
        xc = self.abot(self.pi.contri)
        xb = []
        for periodo in [self.pi.periodo_inicial, self.pi.periodo_final]:
            periodo = str(periodo)
            if len(periodo) > 10:
                periodo = periodo[:10]

            if len(periodo) == 10 and periodo.count("-") == 2:
                xa = 2000
                partes = periodo.split('-')
                if len(str(partes[0])) == 4:
                    xa = int(partes[0]) - xa
                    xb.append(str(numpy.int64(xc) - numpy.int64(int(str(xa)+partes[1] + partes[2]))) + 'e')

        respuesta = ''
        if len(xb) > 1:
            respuesta = xc + xb[0] + xb[1].replace('e', '')
        return respuesta

    def fragmentar_varios(self, contri, periodo_inicial, periodo_final):
        '''cifran enalce'''
        xc = self.abot(contri)
        xb = []
        for periodo in [periodo_inicial, periodo_final]:
            periodo = str(periodo)
            if len(periodo) > 10:
                periodo = periodo[:10]

            if len(periodo) == 10 and periodo.count("-") == 2:
                xa = 2000
                partes = periodo.split('-')
                if len(str(partes[0])) == 4:
                    xa = int(partes[0]) - xa
                    xb.append(str(numpy.int64(xc) - numpy.int64(int(str(xa) + partes[1] + partes[2]))) + 'e')

        respuesta = ''
        if len(xb) > 1:
            respuesta = xc + xb[0] + xb[1].replace('e', '')
        return respuesta

    def desfragmentar(self, arquetipo):
        '''descompresion de parametros'''
        self.espejo.contri = self.pi.contri
        self.pi.periodo_inicial = str(self.pi.periodo_inicial)
        self.pi.periodo_final = str(self.pi.periodo_final)
        self.espejo.periodo_inicial = self.pi.periodo_inicial
        self.espejo.periodo_final = self.pi.periodo_final
        self.espejo.usuario = self.pi.usuario
        xb = []
        espe = arquetipo
        if len(arquetipo) > 30 and len(arquetipo) < 70 and str(arquetipo).count('e') == 1:
            self.pi.memoria = int(arquetipo[-10:])
            arquetipo = arquetipo[:-10]
            self.pi.cuerda = int(arquetipo[-2:])
            if len(self.pi.contri) == 13 and len(self.pi.periodo_inicial) == 10 and len(self.pi.periodo_final) == 10 \
                    and self.espejo.contri == '' and self.espejo.periodo_inicial == '' and self.espejo.periodo_final == '':
                print("no es necesaria recarga de valores ")
            else:
                arquetipo = arquetipo[:-2]
                partes = arquetipo.split('e')
                preabot = partes[0][:10]
                pf = partes[0][10:]
                sf = partes[1]
                xb = []
                memoria = int(espe[-10:])
                for periodo in [pf, sf]:
                    pre = str(numpy.int64(preabot) - numpy.int64(periodo))
                    back_to_back = 2000 + int(pre[:2])
                    mes = pre[2:4]
                    dia = pre[4:]
                    xb.append(str(back_to_back) + '-' + mes + '-' + dia)

                contri_pre = self.costelo(preabot)
                self.pi.contri = contri_pre
                self.pi.periodo_inicial = xb[0]
                self.pi.periodo_final = xb[1]
                xb.append(contri_pre)
                xb.append(memoria)
        return xb
