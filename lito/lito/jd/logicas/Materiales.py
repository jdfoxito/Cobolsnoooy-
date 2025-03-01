"""Materiales, desde Abril 2023
Funcionalidades:
  - Clase Transversal con alunas funciones comunes.


METODOS:

 - fn(get_rellenar_cols_jd)         Rellena los dataframes de las
                                    tablas tempmorales con las
                                    columnas estandar para sus
                                    relaciones futuras cuando
                                    dejan de ser solas
 - fn(guardar_warp_jd)              Guarda un dataframe en la base
                                    de datos local, distinguiendo
                                    entre los dataframes que no
                                    rellenan su primera fila
                                    por estar transpuestos
 - fn(get_negados_dups)             Formula para los negados
 - fn(get_no_listado)               Formula para los no cruzan
 - fn(get_aceptados_cadena)         Formula para la columa aceptados
                                    cadena en el resumen de las
                                    retenciones
 - fn(get_vncf)                     Formula para los que no constan
                                    en fisico
 - fn(get_dif_actualizar)           Formula para los que las
                                    diferencias a actualizar
 - fn(get_no_base)                  Formula para los comprobantes
                                    que no constan en base
 - fn(guardar_mayoreo)              Formula se aplica cuando
                                    se cambia un valor en algun
                                    mayor-periodo
 - fn(get_diccionario_uni)          de dataframe a diccionario json
                                    como records, para evitar el if
 - fn(get_longitud_si_df)           dar la longitud de un dataframe
                                    si tiene datos, se evita el uso de if
 - fn(get_eliminar_index)           eliminar columnas de un dataframe,
                                    segun una lista
 - fn(renombrar_columna)            renombrado de una columna dataframe
 - fn(get_amarre_inicializador)     Se utiliza para el informe,
                                    estandariza un daframe de tipo pendiente
 - fn(get_merge_multiples)          Unir multiple dataframes

+-------------------+--------------+--------------------------------+
| Fecha      | Modifier     | Descripcion                           |
+-------------------+-------------------+---------------------------+
| 19ABR2023  | jagonzaj     | Paulatinamente se agregan             |
|            |              | funcioget_panalnes transversales      |
| 19FEB2024  | jagonzaj     | Se agregan la diferencias para        |
|            |              |  periodos que pressentan valores      |
|            |              |  duplicados entre columnas            |
|            |              |  transpuestas                         |
+------------+--------------+-----------+---------------------------+

ESTANDAR PEP8
REVISADO CON SONARLINT 4.3.0
"""

import numpy
import pandas
from datos import Consultas


class Universales():
    '''para mineria de datos '''
    def __init__(self, db):
        '''construnctor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)

    def get_rellenar_cols_jd(self, _sql, estado="INA"):
        '''relleno de columnas '''
        df_cambiar = _sql.jd.df.copy()
        df_cambiar["contri"] = _sql.jd.contri
        df_cambiar["fecha_analisis"] = _sql.jd.fecha_hoy
        df_cambiar["estado"] = estado
        df_cambiar["fila"] = numpy.arange(len(df_cambiar))
        df_cambiar["periodo_inicial"] = _sql.jd.periodo_inicial
        df_cambiar["periodo_final"] = _sql.jd.periodo_finalisima
        df_cambiar["numero_tramite"] = _sql.jd.tramite
        df_cambiar["usuario"] = _sql.jd.usuario
        return df_cambiar

    def guardar_warp_jd(self, _sql, cabecera=False, estado="INA"):
        '''wrap para guardar'''
        df = _sql.jd.df.copy()
        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        self.db.get_reseto_tabla_estandar_jd(_sql)
        if not df.empty:
            _sql.jd.df = df
            df_grabar_bx = self.get_rellenar_cols_jd(_sql, estado)
            if not cabecera:
                df_grabar_bx = df_grabar_bx.head(df.shape[0] - 1)
            _sql.jd.df = df_grabar_bx
            self.db.guardar_dataframe_jd(_sql)

    def get_negados_dups(self, a, b, c, d):
        '''negados duplciados'''
        return a + b + c + d

    def get_no_listado(self, a, b, c, d, e):
        '''no forman parte del listado'''
        r = 0
        if min(a, c) - b >= 0:
            r = b - d - e
        return r

    def get_aceptados_cadena(self, a, c, e, f, g):
        '''aceptados en la cadena'''
        r = 0
        if (a - c - e - f - g) > 0:
            r = a - c - e - f - g
        return r

    def get_vncf(self, a, b, c):
        '''no constan fisicos'''
        d = 0
        if min(a, b) - c >= 0:
            d = min(a, b) - c
        return d

    def get_dif_actualizar(self, a, b):
        '''diferencias a actualizar'''
        c = 0
        if a-b >= 0:
            c = a-b
        return c

    def get_no_base(self, a, b, c):
        '''no constn en Base'''
        d = 0
        if min(a, b) - c >= 0:
            d = min(a, b) - c
        return d

    def guardar_mayoreo(self, _sql):
        '''guardar valores de los mayores '''
        df_pre_informe = \
            self.db.get_vector(_sql.get_sql_resumen_periodos_est())
        df_pre_informe = df_pre_informe.fillna(0)
        vnr = "valor_no_reporta"
        df_pre_informe['negados_dups'] = \
            df_pre_informe.apply(lambda r:
                                 self.get_negados_dups(r["fantasmas"],
                                                       r["fallecidos"],
                                                       r["duplicados"],
                                                       r[vnr]), axis=1)
        # df_pre_informe['mayores'] = df_pre_informe["retenciones_fuente_iva"]
        # no en listado ncf and ncb                                                                  A                       B               C              D                   E
        df_pre_informe['no_listado'] = df_pre_informe.apply(lambda r: self.get_no_listado(r['retenciones_fuente_iva'], r['ingresados'], r['mayores'], r['aceptados'],  r["negados_dups"]  ), axis = 1)
        # comprobantes no sustentados
        df_pre_informe['v_ncf'] = df_pre_informe['no_cruzaron_sin_obs']
        df_pre_informe['diferencia_actualizar'] = df_pre_informe.apply(lambda row : self.get_dif_actualizar(row['retenciones_fuente_iva'], row['mayores']), axis = 1)
        df_pre_informe['no_consta_base'] = df_pre_informe.apply(lambda row : self.get_no_base(row['retenciones_fuente_iva'], row['mayores'], row['ingresados'] ), axis = 1)
        df_pre_informe = df_pre_informe.fillna(0)
        # RESULTADO FINAL                                                                                        A                           C                                   E               F               G               
        df_pre_informe['aceptados_cadena'] = df_pre_informe.apply(lambda r : self.get_aceptados_cadena(r['retenciones_fuente_iva'], r['diferencia_actualizar'] ,  r['no_consta_base'], r["nocruzan"], r["negados_dups"]    ), axis = 1)
        df_pre_informe = df_pre_informe.fillna(0)
        df_pre_informe = df_pre_informe.round(2)

        self.db.uf.pi.esquema = \
            self.db.config.TB_PG_ESQUEMA_TEMPORAL
        self.db.uf.pi.tabla_relacional = \
            self.db.config.TB_PG_DEV_RESUMEN_CADENA
        self.db.uf.pi.tabla_esquema = \
            f"{self.db.uf.pi.esquema}.{self.db.uf.pi.tabla_relacional}"
        self.db.uf.pi.df = df_pre_informe
        self.guardar_warp_jd(_sql, True)
        self.db.uf.pi.df = ''
        return 1

    def get_mayoreo(self, _sql):
        '''conseguir los que ya se ingeso en mayores'''
        return self.db.get_vector(_sql.get_sql_resumen_periodos_est())

    def unir_serie(self, df):
        '''unir las dos series'''
        df["anio_fiscal"] = df["anio_fiscal"].astype(str)
        df["mes_fiscal"] = df["mes_fiscal"].astype(str)
        return df["anio_fiscal"] + "-" + df["mes_fiscal"]

    def set_periocidad(self, df):
        '''periodo encontrado'''
        if "periocidad" not in df.columns:
            df = df.reset_index()
            if "index" in df.columns:
                df.drop("index", axis=1, inplace=True)
            df["segmento"] = 'M-'+df["anio_fiscal"].astype(str)
            df["mes_fiscal"] = df["mes_fiscal"].str.zfill(2)
            df["periocidad"] = self.unir_serie(df)
            anios = pandas.unique(df["anio_fiscal"])
            for x_year in anios:
                df_phase = \
                    (df[(df.codigo_impuesto == "SEMESTRAL") &
                        (x_year == df.anio_fiscal)])
                for ix, fila in df_phase.iterrows():
                    if int(fila["mes_fiscal"]) < 7 and int(fila["anio_fiscal"]) == int(x_year):
                        df.at[ix, "periocidad"] = str(fila["anio_fiscal"]) + "-6"
                        df_cam = df[(df["anio_fiscal"] == fila["anio_fiscal"]) & df["mes_fiscal"].astype(int).between(1, 6)]
                        df.loc[df_cam.index, 'segmento'] = "S1_"+df["anio_fiscal"].astype(str)
                    else:
                        df.at[ix, "periocidad"] = str(fila["anio_fiscal"]) + "-12"
                        df_cam = df[(df["anio_fiscal"] == fila["anio_fiscal"]) & df["mes_fiscal"].astype(int).between(7, 12)]
                        df.loc[df_cam.index, 'segmento'] = "S2_"+df["anio_fiscal"].astype(str)
        return df

    def borrar_columnas(self, df, columnas):
        '''borrado de columnas '''
        for x in columnas:
            if x in df.columns:
                df = df.drop(x, axis=1)
        return df
