"""Catastro, desde Enero 2023
Funcionalidades:
  - Sirve para traer la informacion del contribuyente entre otras validaciones.

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

COMPORTAMIENTO:

- fn(get_australian) Genera la informacion del contri y sus
    tramites nuevos asignados

+--------------------------+--------------------------------------------------+
| Fecha       | Modifier   |       | Descripcion                              |
+-------------+------------+--------------------------------------------------+
| 23FEB2023   | jagonzaj   |       |   La consulta revisa si el contri        |
|             |            |       |    tienes declaraciones, tramites nuevos,|
|             |            |       |    en los periodos fiscales              |
| 01MAR2024   | jagonzaj   |       |   se agrega un chequeo entre la cabecera |
|             |            |       |   y detalle de la informacion del SNT    |
+-------------------+-------------------+-------------------------------------+

ESTANDAR PEP8

"""

import pandas
from dateutil import parser

from datos import Consultas, RetencionesQ
from logicas import Materiales


class Tramites(Materiales.Universales):
    """Caracteristicas Futuras version 1.0.3
    --------------------------------------------------------------------------
    remover la consulta, y cambiarla a dataframes segun la respectiva
    prueba unitaria.
    """
    __version__ = "1.0.2"

    def __init__(self, db):
        '''construcntor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)

    def get_validar_fecha(self, fecha):
        '''validacion de fecha'''
        try:
            res = bool(parser.parse(fecha))
        except ValueError:
            res = False
        return res

    def get_australian(self):
        """ FUNCIONALIDAD:      revisar si el contri es fantasma, informacion
                                en general del contri, tramites.
            PARAMETROS :
            self(_sql)     :   Trama general para los habituales contri,
                                y periodos
            GENERA:

            contri           :   DataFrame que contiene informacion del contri
                                  que se grafica en la pantalla incial
            tramites         :   trae la informacion de tramites
                                  nuevos y asignados
            representante    :   reperesentante legal de la compania

            lhistoria        :   desde cuando el contri es olbigado
                                  a llevar contabilidad
            novedades        :   informacion acerca de probables fallos
            detener          :  en caso de que toque detener la ejecucion
                                por multiiples fallos
            EXCEPCIONES:
               implementacion pendiente, remover el sql complejo por una
            simple para el uso de pandas
        """
        _his = self.db.uf.his
        _jd = self.db.uf.pi
        _sql = RetencionesQ.Contri(_jd)
        _sql.jd.fecha_hoy = self.db.get_fecha_ymd()
        lrepresentante = ''
        df_tramites = pandas.DataFrame()
        df_contri = pandas.DataFrame()
        lhistoria = pandas.DataFrame()
        novedades = []
        continuar = True
        detener = 0

        es_fantasma = self.db.get_scalar(_sql.es_fantasma())
        sms = f""" El contribuyente {_sql.jd.contri} es fantasma """
        if es_fantasma > 0:
            novedades.append({"mensaje": sms, "category": "fantasma"})
            continuar = False

        sms = f"""La fecha inicio {_sql.jd.periodo_inicial} esta incorrecta """
        if not self.get_validar_fecha(_sql.jd.periodo_inicial):
            novedades.append({"mensaje": sms, "category": "ingreso"})
            continuar = False

        if not self.get_validar_fecha(_sql.jd.periodo_final):
            novedades.append({"mensaje": f""" La fecha final
                                             {_sql.jd.periodo_final}
                                             esta incorrecta """,
                              "category": "ingreso"})
            continuar = False
        lla = ['nombre_tipo_tramite',
               'nombre_sub_tipo_tramite',
               'nombre_clase_tramite']
        _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
        if continuar:
            df_contri = self.db.get_vector(_sql.get_sql_contribuyente())
            if len(df_contri) > 0:
                _sql.jd.tabla_relacional = \
                    self.db.config.TB_PG_DEV_RUC_CONSULTADOS
                _sql.jd.tabla_esquema = \
                    f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                _sql.jd.df = df_contri
                self.guardar_warp_jd(_sql, True)
                _sql.jd.df = ''
                rle = "representante_legal"
                _sql.representante = \
                    self.db.get_representante(df_contri[rle].iloc[0])
                lrepresentante = \
                    self.db.get_scalar(_sql.get_info_representante())
                lhistoria = self.db.get_vector(_sql.get_contri_his())
                df_tramites = \
                    self.db.get_vector(_sql.get_sql_tramites_nuevos_periodo())
                _his.num_tramites_objetivos = len(df_tramites.index)
                if _his.num_tramites_objetivos == 0:
                    detener = 1
                    df_inconsistencia_tipo = \
                        self.db.get_vector(_sql.es_tramite_tipo_inconsistent())
                    if not df_inconsistencia_tipo.empty:
                        cat = """INCONSISTENCIA EN LA INFORMACION DE TRAMITE:
                                  EL ENCABEZADO ESTA COMO: """
                        cat += str(df_inconsistencia_tipo["tipo1"].iloc[0]) + \
                            "(" + str(df_inconsistencia_tipo["t1"].iloc[0]) + \
                            ")"
                        cat += ", Y EN EL DETALLE : -> " + \
                            str(df_inconsistencia_tipo["tipo2"].iloc[0]) + \
                            "(" + str(df_inconsistencia_tipo["t2"].iloc[0]) + \
                            ")" + ", reporte a la administración. "
                    else:
                        cat = f""" No existen trámites nuevos dentro de los
                                    periodos  {_sql.jd.periodo_inicial}
                                    {_sql.jd.periodo_final} seleccionados! """

                    novedades.append({"mensaje": cat, "category": "tramites"})
                else:
                    df_tramites_save = df_tramites.copy()
                    dic = {'estado': 'estado_tramite'}
                    df_tramites_save.rename(columns=dic, inplace=True)
                    df_tramites_save = df_tramites_save.drop(lla, axis=1)
                    _sql.jd.tabla_relacional = \
                        self.db.config.TB_PG_DEV_TRAMITES_CONS
                    _sql.jd.tabla_esquema = \
                        f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                    _sql.jd.df = df_tramites_save
                    self.guardar_warp_jd(_sql, True)
                    _sql.jd.df = ''
            else:
                sms = f""" NO existe informacion del
                            contribuyente {_sql.jd.contri}  """
                novedades.append({"mensaje": sms, "category": "ingreso"})
                detener = 1
        else:
            detener = 1
            sms = """ Revise las novedades reportadas """
            novedades.append({"mensaje": sms, "category": "ingreso"})

        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd

        print(f"df_contri {df_contri}")

        resultado = {
            "contri": df_contri.to_dict('records'),
            "tramites": df_tramites.to_dict('records'),
            "repre": lrepresentante,
            "lhistoria": lhistoria.to_dict('records'),
            "novedades": pandas.DataFrame(novedades).to_dict('records'),
            "detener": detener
        }
        return resultado
