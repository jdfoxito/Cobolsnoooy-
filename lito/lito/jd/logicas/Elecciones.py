"""Elecciones, desde Enero/Febrero 2023
Funcionalidades:
  - Sirve para determinar las declaraciones validas

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

METODOS

- fn(get_listas_df_v_mar_2024)  Seleccion de periodos segun ultimo memorando
                                    en marzo 2024
- fn(get_listas_df)             Seleccion de periodos segun definicion
                                    a inicios de 2023

+-------------+------------+------------+-------------------------------------+
| Fecha       | Modifier   | Descripcion                                      |
+---------------------------------------+-------------------------------------+
| 10FEB2023   | jagonzaj   |Seleccion de periodos mensuales segun formulas con|
|             |            |     MFI, CM, DF de la DNJ                        |
| 20NOV2023   | jagonzaj   |Seleccion de periodos mensuales/semestrales       |
|             |            |   hibridos segun formulas con Ivone PErez,       |
|             |            |    Fernanda Freire de la zonal  9                |
| 05MAR2024   | jagonzaj   |Se agreaga cambio normativo en marzo 2024 para    |
|             |            |   elegir declaracino valida                      |
+-------------+------------+------------+-------------------------------------+

ESTANDAR PEP8

"""

import pandas as pd
import numpy as numerico
import random
from datos import Consultas, RetencionesQ
from logicas import Materiales


class Periodo(Materiales.Universales):
    '''Segmentacion de declaraciones
    Caracteristicas Futuras version 1.0.3
    ---------------------------------------------------------------------------
    seleccion segun un parametro por la version del tipo de declaracion valida.
    '''

    __version__ = "1.0.2"
    tipo_frecuencia = 'MENSUAL'

    def __init__(self, db):
        '''constructor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)
        self.DATE_TIME_64 = self.db.config.DATE_TIME_64
        self.FORMATO_YMD_HMS = self.db.config.FORMATO_YMD_HMS
        self.MAYOR_IMPUESTO = 'MAYOR IMPUESTO'
        self.MAYOR_CREDITO = 'MAYOR CREDITO'

    def get_listas_df_v_mar_2024(self, _sql, _his):
        '''    # Memorando Nro SRI-NAC-DNJ-2024-0035M
            #    Se cambia la forma de elegir las declaraciones'''
        listadf_cumplen = []
        listadf_por_revisar = []
        df_segunda_vuelta = pd.DataFrame()
        df_cumplen_set_x = pd.DataFrame()
        df_no_cumplen_set = pd.DataFrame()
        df_cumplen_set_x_per = pd.DataFrame()
        df_segmentos = pd.DataFrame()
        dfperiodofabrica = pd.DataFrame()
        df_set_principal_periodos_mix = pd.DataFrame()
        df_uni_periodo = pd.DataFrame()
        df_multi_periodo = pd.DataFrame()
        listadf_no_cumplian = []
        lista_son_no_por_revisar = []
        origen = _sql.get_sql_declaracion_cumplen_nocumplen()
        codigo_impuesto = ''
        df_origen = self.db.get_df_from_pg(origen)
        # se divide en dos 1-6 nperiodo (1),  7-12 Periodo 2
        df_origen["ciclo"] = numerico.where(df_origen["mes_fiscal"].astype(int) < 7, 1, 2)
        df_clasificador = df_origen.groupby(['anio_fiscal', 'ciclo'])['codigo_impuesto'].nunique().reset_index()
        df_clasificador = df_clasificador.rename(columns={'codigo_impuesto': 'conteo'})
        df_unicos = df_clasificador[df_clasificador["conteo"] == 1]
        df_mixtos = df_clasificador[df_clasificador["conteo"] > 1]
        lista_unicos = []
        for ix, fila in df_unicos.iterrows():
            anio = fila["anio_fiscal"]
            ciclo = fila["ciclo"]
            lista_unicos.append(df_origen.query(f" anio_fiscal == '{anio}'  & ciclo ==  {int(ciclo)} "))
            ix = ix*1

        if len(lista_unicos) > 0:
            df_uni_periodo = pd.concat(lista_unicos)

        lista_multi = []
        for ix, fila in df_mixtos.iterrows():
            anio = fila["anio_fiscal"]
            ciclo = fila["ciclo"]
            lista_multi.append(df_origen.query(f" anio_fiscal == '{anio}'  & ciclo ==  {int(ciclo)} "))
        if len(lista_multi) > 0:
            df_multi_periodo = pd.concat(lista_multi)

        df_set_principal_periodos = pd.DataFrame()
        _his.frecuenciamiento = "MENSUAL"
        if _his.num_decla_mensual_subjetivas >= 0 and _his.numeros_semestrales_subjetivas > 0:
            _his.frecuenciamiento = "MIXTO"

        if _his.num_decla_mensual_subjetivas == 0 and _his.numeros_semestrales_subjetivas > 0:
            _his.frecuenciamiento = "SEMESTRAL_UNICO"

        self.tipo_frecuencia = _his.frecuenciamiento

        if not df_uni_periodo.empty:
            df_set_principal = df_uni_periodo[["anio_fiscal", "mes_fiscal", "numero_adhesivo", "fecha_recepcion", "ciclo"]]
            df_set_principal = df_set_principal.drop_duplicates()
            df_set_principal = df_set_principal.sort_values(by=["anio_fiscal", 'mes_fiscal', 'ciclo'], ascending=True)
            df_set_principal_periodos = df_set_principal[["anio_fiscal", "mes_fiscal", "ciclo"]]
            df_set_principal_periodos = df_set_principal_periodos.drop_duplicates()
            if len(df_set_principal.index) > 0:
                pre = df_set_principal.groupby(['anio_fiscal', 'mes_fiscal', 'ciclo'])["numero_adhesivo"].count()
                df_filas = pd.DataFrame(pre).reset_index()
                if len(df_filas.index) > 0:
                    if len(df_filas.index) == 1:
                        lista_df_pre = {"anio_fiscal": [df_filas["anio_fiscal"].values[0]], "mes_fiscal": [df_filas["mes_fiscal"].values[0]], "ciclo": [df_filas["ciclo"].values[0]]}
                        listadf_cumplen.append(pd.DataFrame(lista_df_pre))

                    if len(df_filas.index) > 1:
                        for index, fila in df_filas.iterrows():
                            df_x = df_set_principal[(df_set_principal['anio_fiscal'].astype('string') == fila["anio_fiscal"]) & (df_set_principal['mes_fiscal'].astype('string') == fila["mes_fiscal"])]
                            df_y = pd.DataFrame(df_x['fecha_recepcion'].agg(['min', 'max'])).T.reset_index()
                            df_y["esta"] = (pd.to_datetime(df_y["max"]) - pd.to_datetime(df_y["min"])).dt.days < 365
                            df_z = pd.DataFrame(df_y["esta"]).reset_index()
                            df_z.replace({False: "OUT", True: "IN"}, inplace=True)
                            try:
                                if len(df_z.index) > 0:
                                    valor = df_z["esta"].iloc[0]
                                    if valor == "IN":
                                        listadf_cumplen.append(pd.DataFrame({"anio_fiscal": [fila["anio_fiscal"]], "mes_fiscal": [fila["mes_fiscal"]], "ciclo": [fila["ciclo"]]}))
                                    else:
                                        listadf_por_revisar.append(pd.DataFrame({"anio_fiscal": [fila["anio_fiscal"]], "mes_fiscal": [fila["mes_fiscal"]], "ciclo": [fila["ciclo"]]}))
                                else:
                                    valor = ''
                            except Exception as ex:
                                print(f" {self.db.uf.RED} ERROR : {ex} {self.db.uf.RESET}")
                                valor = ''
                            index = index * -1

                df_cumplen_set = []
                df_no_cumplen_set = []

                if len(listadf_cumplen) > 0:
                    df_cumplen = pd.concat(listadf_cumplen, ignore_index=True)
                    df_cumplenx = pd.merge(df_cumplen, df_set_principal, on=["anio_fiscal", "mes_fiscal", "ciclo"], how="inner", validate="1:m")
                    df_cumplen_maximos = pd.DataFrame(df_cumplenx.groupby(['anio_fiscal', 'mes_fiscal', 'ciclo'])["fecha_recepcion"].max()).reset_index()
                    df_cumplen_set = pd.merge(df_cumplen_maximos, df_origen, on=["anio_fiscal", "mes_fiscal", "ciclo", "fecha_recepcion"], how="inner", validate="1:m")

                if len(listadf_por_revisar) > 0:
                    df_no_cumplen = pd.concat(listadf_por_revisar, ignore_index=True)
                    df_no_cumplenx = pd.merge(df_no_cumplen, df_set_principal, on=["anio_fiscal", "mes_fiscal", "ciclo"], how="inner", validate="1:m")
                    df_no_cumplen_set = pd.merge(df_no_cumplenx, df_origen, on=["anio_fiscal", "mes_fiscal", "ciclo", "fecha_recepcion"], how="inner", validate="1:m")
                    df_calculos_px = df_origen[self.db.config.CAMPOS_DECLARACION_ORIGEN]
                    df_calculos_px = df_calculos_px.reset_index(drop=True)
                    df_calculos_px.sort_values(by='numero_adhesivo', ascending=True, inplace=True)
                    df_no_cumplen_set.sort_values(by='mes_fiscal', ascending=True, inplace=True)
                    dfperiodosunicos = df_no_cumplen_set[["anio_fiscal", "mes_fiscal", "ciclo"]]
                    dfperiodosunicos = dfperiodosunicos.drop_duplicates()

                    for ix, periodo in dfperiodosunicos.iterrows():
                        df_no_cumplen_set_xp = df_calculos_px[(df_calculos_px['anio_fiscal'].astype('string') == periodo["anio_fiscal"]) & (df_calculos_px['mes_fiscal'].astype('string') == periodo["mes_fiscal"])]
                        df_no_cumplen_set_xp.loc[:, 'fecha_recepcion'] = df_no_cumplen_set_xp['fecha_recepcion'].astype(self.DATE_TIME_64)
                        df_limites = pd.DataFrame(df_no_cumplen_set_xp['fecha_recepcion'].agg(['min', 'max'])).T.reset_index()
                        df_limites["12meses"] = pd.to_datetime(df_limites['min']) + pd.Timedelta(days=365)
                        minimafecha = df_limites["min"].iloc[0]
                        limitefecha = df_limites["12meses"].iloc[0]
                        maxima_fecha = df_limites["max"].iloc[0]
                        df_rango_no_cumplen_1 = df_no_cumplen_set_xp.loc[df_no_cumplen_set_xp['fecha_recepcion'].between(minimafecha, limitefecha, inclusive="both")]
                        df_limites_1 = pd.DataFrame(df_rango_no_cumplen_1['fecha_recepcion'].agg(['min', 'max'])).T.reset_index()
                        fecha_declaracion_valida = df_limites_1["max"].iloc[0]
                        df_rango_no_cumplen_2 = df_no_cumplen_set_xp.loc[df_no_cumplen_set_xp['fecha_recepcion'].between(fecha_declaracion_valida, maxima_fecha, inclusive="both")]
                        df_rango_no_cumplen_2 = df_rango_no_cumplen_2.sort_values(by='numero_adhesivo', ascending=True, ignore_index=True)
                        declaracion_valida_fecha = ''
                        adhesivo_valido = ''
                        c1 = ''
                        i = 0
                        actual = 0
                        df_rango_no_cumplen_2 = pd.DataFrame(df_rango_no_cumplen_2)
                        hay_decla_valida = False
                        longitud_periodo2 = len(df_rango_no_cumplen_2)

                        # Nueva Definicion
                        # 2140	IMPUESTO_CAUSADO_2140				IMPUESTO CAUSADO							601
                        # 2150	CREDITO_TRIBUTARIO_MAC_2150			CREDITO TRIBUTARIO MES ACTUAL				602
                        # Si en el resultado de las dos lógicas es afirmativo se deberá otorgar la marca “DV” a la declaración posterior “DP”.
                        # En caso de que existan más declaraciones se deberá realizar el mismo proceso con todas.
                        # # Cuando una declaración sustitutiva no cumpla con la validación
                        # positiva de las dos lógicas se deberá mostrar al analista la última declaración válida “DV”
                        # seguido por todas las declaraciones posteriores a fin de que el analista seleccione la válida después de un análisis manual.
                        v601_impuesto_causado_valida = float(df_rango_no_cumplen_2.loc[actual, "impuesto_causado"])
                        v602_cred_tributa_mes_valida = float(df_rango_no_cumplen_2.loc[actual, "ct_mes_actual"])
                        posicion_disco = 0
                        for i in range(longitud_periodo2 - 1):
                            siguiente = i+1
                            c1 = ''
                            v601_impuesto_causado_siguiente = float(df_rango_no_cumplen_2.loc[siguiente, "impuesto_causado"])
                            v602_cred_tributa_mes_siguiente = float(df_rango_no_cumplen_2.loc[siguiente, "ct_mes_actual"])
                            # 601 (DP) mayor  601 (DV)
                            # 602 (DP) menor 602 (DV)
                            if ((v601_impuesto_causado_siguiente > v601_impuesto_causado_valida) and (v602_cred_tributa_mes_siguiente < v602_cred_tributa_mes_valida)):
                                declaracion_valida_fecha = df_rango_no_cumplen_2.loc[i, "fecha_recepcion"]
                                adhesivo_valido = df_rango_no_cumplen_2.loc[i, "numero_adhesivo"]
                                c1 = 'CUMPLE POR FORMULA'
                                v601_impuesto_causado_valida = v601_impuesto_causado_siguiente
                                v602_cred_tributa_mes_valida = v602_cred_tributa_mes_siguiente
                                i += 1
                            else:
                                posicion_disco = i-1
                                hay_decla_valida = False
                                break
                        if not hay_decla_valida:
                            if posicion_disco < 0:
                                posicion_disco = 0

                            df_almas_perdidas_ = df_rango_no_cumplen_2[posicion_disco:].copy()
                            df_almas_perdidas_["c1"] = ''
                            df_almas_perdidas = df_almas_perdidas_[["anio_fiscal", "mes_fiscal", "fecha_recepcion", "codigo_impuesto", "numero_adhesivo", "ciclo", "c1"]]
                            lista_son_no_por_revisar.append(df_almas_perdidas)
                        else:
                            pre_dic = {"anio_fiscal": [periodo["anio_fiscal"]]}
                            pre_dic["mes_fiscal"] = [periodo["mes_fiscal"]]
                            pre_dic["fecha_recepcion"] = declaracion_valida_fecha
                            pre_dic["codigo_impuesto"] = codigo_impuesto
                            pre_dic["numero_adhesivo"] = adhesivo_valido
                            pre_dic["c1"] = c1
                            pre_dic["ciclo"] = periodo["ciclo"]

                            listadf_no_cumplian.append(pre_dic)
                    if len(listadf_no_cumplian) > 0:
                        df_segunda_vuelta = pd.concat(listadf_no_cumplian)

                df_parcial_a = pd.DataFrame()
                df_parcial_b = pd.DataFrame()

                if isinstance(df_cumplen_set, pd.DataFrame):
                    if len(df_cumplen_set.index) > 0:
                        df_parcial_a = df_cumplen_set[["anio_fiscal", "mes_fiscal", "numero_adhesivo", "fecha_recepcion"]]
                        df_parcial_a_maximos = df_parcial_a.groupby(["anio_fiscal", "mes_fiscal", "fecha_recepcion"])['numero_adhesivo'].max().reset_index()
                        df_parcial_a = df_parcial_a_maximos
                        df_parcial_a["c1"] = ''

                if len(df_segunda_vuelta.index) > 0:
                    df_parcial_b = df_segunda_vuelta[["anio_fiscal", "mes_fiscal", "numero_adhesivo", "fecha_recepcion", "c1"]]

                if len(df_parcial_a.index) > 0 or len(df_parcial_b.index) > 0:
                    df_cumplen = pd.concat([df_parcial_a, df_parcial_b])
                    df_cumplen_set_x = pd.merge(df_cumplen, df_origen, on=["anio_fiscal", "mes_fiscal", "numero_adhesivo"], how='inner', validate="1:m")
                    df_cumplen_set_x.sort_values(by='mes_fiscal', ascending=True, inplace=True, ignore_index=True)
                    df_cumplen_set_x['fecha_recepcion_x'] = pd.to_datetime(df_cumplen_set_x['fecha_recepcion_x'])
                    df_cumplen_set_x['fecha_recepcion_x'] = df_cumplen_set_x['fecha_recepcion_x'].map(lambda ts: ts.strftime(self.FORMATO_YMD_HMS))
                    df_cumplen_set_x_per = df_cumplen_set_x[["anio_fiscal", "mes_fiscal"]]
                    df_cumplen_set_x_per = df_cumplen_set_x_per.drop_duplicates()

                if len(lista_son_no_por_revisar) > 0:
                    df_no_cumplen_set = pd.concat(lista_son_no_por_revisar)
                    df_no_cumplen_set['fecha_recepcion'] = df_no_cumplen_set['fecha_recepcion'].map(lambda ts: ts.strftime(self.FORMATO_YMD_HMS))
                    df_no_cumplen_set.sort_values(by=['anio_fiscal', 'mes_fiscal'], ascending=True, inplace=True, ignore_index=True)
                    dfperiodofabrica = df_no_cumplen_set[["anio_fiscal", "mes_fiscal"]]
                    dfperiodofabrica = dfperiodofabrica.drop_duplicates()

        if self.tipo_frecuencia == "MIXTO" and not df_multi_periodo.empty:
            df_set_principal_periodos_mix = df_multi_periodo[["anio_fiscal", "mes_fiscal"]]
            df_set_principal_periodos_mix = df_set_principal_periodos_mix.drop_duplicates()
            if isinstance(df_no_cumplen_set, pd.DataFrame) and not df_no_cumplen_set.empty and not df_multi_periodo.empty:
                df_no_cumplen_set = pd.concat([df_no_cumplen_set, df_multi_periodo])
            else:
                df_no_cumplen_set = df_multi_periodo

            df_no_cumplen_set["c1"] = ''
            df_no_cumplen_set['fecha_recepcion'] = df_no_cumplen_set['fecha_recepcion'].astype(self.DATE_TIME_64)

        if self.tipo_frecuencia in ['MIXTO', 'SEMESTRAL_UNICO']:
            self.tipo_frecuencia = "SEMESTRAL"
            _his.frecuenciamiento = self.tipo_frecuencia

        df_periodos__conteos = pd.DataFrame()
        if isinstance(df_cumplen_set_x, pd.DataFrame):
            if not df_cumplen_set_x.empty:
                df_cumplen_set_x = self.set_periocidad(df_cumplen_set_x)

        if isinstance(df_no_cumplen_set, pd.DataFrame):
            if not df_no_cumplen_set.empty:
                df_no_cumplen_set = self.set_periocidad(df_no_cumplen_set)
                df_periodos__conteos = df_no_cumplen_set.groupby('segmento')['periocidad'].nunique().reset_index()
                df_periodos__conteos = df_periodos__conteos.rename(columns={'periocidad': 'conteo'})
                df_no_cumplen_set = pd.merge(df_periodos__conteos, df_no_cumplen_set, indicator=True, on=["segmento"], how="inner", validate="1:m").reset_index()
                df_no_cumplen_set["segmentacion"] = df_no_cumplen_set["segmento"].astype(str) + '_' + df_no_cumplen_set["ciclo"].astype(str)
                df_no_cumplen_set["segmento"] = df_no_cumplen_set["segmentacion"]
                lista_unicos = pd.unique(df_no_cumplen_set["segmento"]).tolist()
                df_segmentos = pd.DataFrame({"segmentados": lista_unicos})

        if isinstance(df_cumplen_set_x, pd.DataFrame):
            df_cumplen_set_x = self.rellenar(df_cumplen_set_x, 0)

        if isinstance(df_no_cumplen_set, pd.DataFrame):
            df_no_cumplen_set = self.rellenar(df_no_cumplen_set, 0)
            df_no_cumplen_set = self.rellenar_cols(df_no_cumplen_set, ["declaracion_cero", "estadentro_del_year", "numero_identificacion", "prescrito2", "sustitutiva_original", "ultima_declaracion"], '')
            df_no_cumplen_set = df_no_cumplen_set.reset_index()
            df_no_cumplen_set = self.borrar_columnas(df_no_cumplen_set, ["level_0", "index", "_merge"])
        return df_cumplen_set_x, df_no_cumplen_set, dfperiodofabrica, len(df_set_principal_periodos.index) + len(df_set_principal_periodos_mix.index), df_segmentos, _sql, _his

    def get_listas_df(self,  _sql, _his):
        '''Segmentacion'''
        listadf_cumplen = []
        listadf_por_revisar = []
        df_segunda_vuelta = pd.DataFrame()
        df_cumplen_set_x = pd.DataFrame()
        df_no_cumplen_set = pd.DataFrame()
        df_cumplen_set_x_per = pd.DataFrame()
        df_segmentos = pd.DataFrame()
        dfperiodofabrica = pd.DataFrame()
        df_set_principal_periodos_mix = pd.DataFrame()
        df_uni_periodo = pd.DataFrame()
        df_multi_periodo = pd.DataFrame()
        listadf_no_cumplian = []
        lista_son_no_por_revisar = []
        origen = _sql.get_sql_declaracion_cumplen_nocumplen()
        codigo_impuesto = ''
        df_origen = self.db.get_df_from_pg(origen)
        # se divide en dos 1-6 nperiodo (1),  7-12 Periodo 2
        df_origen["ciclo"] = numerico.where(df_origen["mes_fiscal"].astype(int) < 7, 1, 2)
        df_clasificador = df_origen.groupby(['anio_fiscal', 'ciclo'])['codigo_impuesto'].nunique().reset_index()
        df_clasificador = df_clasificador.rename(columns={'codigo_impuesto': 'conteo'})
        df_unicos = df_clasificador[df_clasificador["conteo"] == 1]
        df_mixtos = df_clasificador[df_clasificador["conteo"] > 1]
        lista_unicos = []
        for ix, fila in df_unicos.iterrows():
            anio = fila["anio_fiscal"]
            ciclo = fila["ciclo"]
            lista_unicos.append(df_origen.query(f" anio_fiscal == '{anio}' & ciclo ==  {int(ciclo)} "))

        if len(lista_unicos) > 0:
            df_uni_periodo = pd.concat(lista_unicos)

        lista_multi = []
        for ix, fila in df_mixtos.iterrows():
            anio = fila["anio_fiscal"]
            ciclo = fila["ciclo"]
            lista_multi.append(df_origen.query(f" anio_fiscal == '{anio}'  & ciclo ==  {int(ciclo)} "))
        if len(lista_multi) > 0:
            df_multi_periodo = pd.concat(lista_multi)

        df_set_principal_periodos = pd.DataFrame()
        _his.frecuenciamiento = "MENSUAL"
        if _his.num_decla_mensual_subjetivas >= 0 and _his.numeros_semestrales_subjetivas > 0:
            _his.frecuenciamiento = "MIXTO"

        if _his.num_decla_mensual_subjetivas == 0 and _his.numeros_semestrales_subjetivas > 0:
            _his.frecuenciamiento = "SEMESTRAL_UNICO"

        self.tipo_frecuencia = _his.frecuenciamiento
        if not df_uni_periodo.empty:
            df_set_principal = df_uni_periodo[["anio_fiscal", "mes_fiscal", "numero_adhesivo", "fecha_recepcion", "ciclo"]]
            df_set_principal = df_set_principal.drop_duplicates()
            df_set_principal = df_set_principal.sort_values(by=["anio_fiscal", 'mes_fiscal', 'ciclo'], ascending=True)
            df_set_principal_periodos = df_set_principal[["anio_fiscal", "mes_fiscal", "ciclo"]]
            df_set_principal_periodos = df_set_principal_periodos.drop_duplicates()
            if len(df_set_principal.index) > 0:
                pre = df_set_principal.groupby(['anio_fiscal', 'mes_fiscal', 'ciclo'])["numero_adhesivo"].count()
                df_filas = pd.DataFrame(pre).reset_index()
                if len(df_filas.index) > 0:
                    if len(df_filas.index) == 1:
                        listadf_cumplen.append(pd.DataFrame({"anio_fiscal": [df_filas["anio_fiscal"].values[0]], "mes_fiscal": [df_filas["mes_fiscal"].values[0]], "ciclo": [df_filas["ciclo"].values[0]]}))

                    if len(df_filas.index) > 1:
                        for index, fila in df_filas.iterrows():
                            df_x = df_set_principal[(df_set_principal['anio_fiscal'].astype('string') == fila["anio_fiscal"]) & (df_set_principal['mes_fiscal'].astype('string') == fila["mes_fiscal"])]
                            df_y = pd.DataFrame(df_x['fecha_recepcion'].agg(['min', 'max'])).T.reset_index()
                            df_y["esta"] = (pd.to_datetime(df_y["max"]) - pd.to_datetime(df_y["min"])).dt.days < 365
                            df_z = pd.DataFrame(df_y["esta"]).reset_index()
                            df_z.replace({False: "OUT", True: "IN"}, inplace=True)
                            index = index * -1
                            try:
                                if len(df_z.index) > 0:
                                    valor = df_z["esta"].iloc[0]
                                    if valor == "IN":
                                        listadf_cumplen.append(pd.DataFrame({"anio_fiscal": [fila["anio_fiscal"]], "mes_fiscal": [fila["mes_fiscal"]], "ciclo": [fila["ciclo"]]}))
                                    else:
                                        listadf_por_revisar.append(pd.DataFrame({"anio_fiscal": [fila["anio_fiscal"]], "mes_fiscal": [fila["mes_fiscal"]], "ciclo": [fila["ciclo"]]}))
                                else:
                                    valor = ''
                            except Exception as ex:
                                print(f" {self.db.uf.RED} ERROR : {ex} {self.db.uf.RESET}")
                                valor = ''

                df_cumplen_set = []
                df_no_cumplen_set = []

                if len(listadf_cumplen) > 0:
                    df_cumplen = pd.concat(listadf_cumplen, ignore_index=True)
                    df_cumplenx = pd.merge(df_cumplen, df_set_principal, on=["anio_fiscal", "mes_fiscal", "ciclo"], how="inner", validate="1:m")
                    df_cumplen_maximos = pd.DataFrame(df_cumplenx.groupby(['anio_fiscal', 'mes_fiscal', 'ciclo'])["fecha_recepcion"].max()).reset_index()
                    df_cumplen_set = pd.merge(df_cumplen_maximos, df_origen, on=["anio_fiscal", "mes_fiscal", "ciclo", "fecha_recepcion"], how="inner", validate="1:m")

                if len(listadf_por_revisar) > 0:
                    df_no_cumplen = pd.concat(listadf_por_revisar, ignore_index=True)
                    df_no_cumplenx = pd.merge(df_no_cumplen, df_set_principal, on=["anio_fiscal", "mes_fiscal", "ciclo"], how="inner", validate="1:m")
                    df_no_cumplen_set = pd.merge(df_no_cumplenx, df_origen, on=["anio_fiscal", "mes_fiscal", "ciclo", "fecha_recepcion"], how="inner", validate="1:m")
                    df_calculos_px = df_origen[self.db.config.CAMPOS_DECLARACION_ORIGEN_RED]
                    df_calculos_px = df_calculos_px.reset_index(drop=True)
                    df_calculos_px.sort_values(by='numero_adhesivo', ascending=True, inplace=True)
                    df_no_cumplen_set.sort_values(by='mes_fiscal', ascending=True, inplace=True)
                    dfperiodosunicos = df_no_cumplen_set[["anio_fiscal", "mes_fiscal", "ciclo"]]
                    dfperiodosunicos = dfperiodosunicos.drop_duplicates()

                    for ix, periodo in dfperiodosunicos.iterrows():
                        df_no_cumplen_set_xp = df_calculos_px[(df_calculos_px['anio_fiscal'].astype('string') == periodo["anio_fiscal"]) & (df_calculos_px['mes_fiscal'].astype('string') == periodo["mes_fiscal"])]
                        df_no_cumplen_set_xp.loc[:, 'fecha_recepcion'] = df_no_cumplen_set_xp['fecha_recepcion'].astype(self.DATE_TIME_64)
                        df_limites = pd.DataFrame(df_no_cumplen_set_xp['fecha_recepcion'].agg(['min', 'max'])).T.reset_index()
                        df_limites["12meses"] = pd.to_datetime(df_limites['min']) + pd.Timedelta(days=365)
                        minimafecha = df_limites["min"].iloc[0]
                        limitefecha = df_limites["12meses"].iloc[0]
                        maxima_fecha = df_limites["max"].iloc[0]
                        df_rango_no_cumplen_1 = df_no_cumplen_set_xp.loc[df_no_cumplen_set_xp['fecha_recepcion'].between(minimafecha, limitefecha, inclusive="both")]
                        df_limites_1 = pd.DataFrame(df_rango_no_cumplen_1['fecha_recepcion'].agg(['min', 'max'])).T.reset_index()
                        fecha_declaracion_valida = df_limites_1["max"].iloc[0]
                        df_rango_no_cumplen_2 = df_no_cumplen_set_xp.loc[df_no_cumplen_set_xp['fecha_recepcion'].between(fecha_declaracion_valida, maxima_fecha, inclusive="both")]
                        df_rango_no_cumplen_2 = df_rango_no_cumplen_2.sort_values(by='numero_adhesivo', ascending=True, ignore_index=True)
                        declaracion_valida_fecha = ''
                        adhesivo_valido = ''
                        c1 = ''
                        i = 0
                        actual = 0
                        df_rango_no_cumplen_2 = pd.DataFrame(df_rango_no_cumplen_2)
                        ambas_falso = False
                        longitud_periodo2 = len(df_rango_no_cumplen_2)
                        for i in range(longitud_periodo2 - 1):
                            ambas_falso = False
                            declaracion_valida_fecha = df_rango_no_cumplen_2.loc[i, "fecha_recepcion"]
                            adhesivo_valido = df_rango_no_cumplen_2.loc[i, "numero_adhesivo"]
                            codigo_impuesto = df_rango_no_cumplen_2.loc[i, "codigo_impuesto"]
                            c1 = ''
                            v2270_valida_actual = float(df_rango_no_cumplen_2.loc[actual, "tot_impuesto_pagar_x_percepcion"])
                            v2610_valida_actual = float(df_rango_no_cumplen_2.loc[actual, "total_impuesto_a_pagar_2610"])
                            v2220_valida_actual = float(df_rango_no_cumplen_2.loc[actual, "saldo_crt_clo_ipr_msi_2220"])
                            v2230_valida_actual = float(df_rango_no_cumplen_2.loc[actual, "sct_x_retenciones"])
                            v2270_siguiente = float(df_rango_no_cumplen_2.loc[i+1, "tot_impuesto_pagar_x_percepcion"])
                            v2610_siguiente = float(df_rango_no_cumplen_2.loc[i+1, "total_impuesto_a_pagar_2610"])
                            v2220_siguiente = float(df_rango_no_cumplen_2.loc[i+1, "saldo_crt_clo_ipr_msi_2220"])
                            v2230_siguiente = float(df_rango_no_cumplen_2.loc[i+1, "sct_x_retenciones"])

                            if ((v2270_siguiente + v2610_siguiente) > (v2270_valida_actual + v2610_valida_actual)) or ((v2220_siguiente + v2230_siguiente) < (v2220_valida_actual + v2230_valida_actual)):
                                declaracion_valida_fecha = df_rango_no_cumplen_2.loc[i, "fecha_recepcion"]
                                adhesivo_valido = df_rango_no_cumplen_2.loc[i, "numero_adhesivo"]
                                ambas_falso = True
                                if ((v2270_siguiente + v2610_siguiente) > (v2270_valida_actual + v2610_valida_actual)):
                                    c1 = self.MAYOR_IMPUESTO

                                if ((v2220_siguiente + v2230_siguiente) < (v2220_valida_actual + v2230_valida_actual)):
                                    c1 = self.MAYOR_CREDITO

                                actual = i+1
                                if actual == (longitud_periodo2 - 1):
                                    declaracion_valida_fecha = df_rango_no_cumplen_2.loc[i+1, "fecha_recepcion"]
                                    adhesivo_valido = df_rango_no_cumplen_2.loc[i+1, "numero_adhesivo"]
                                i += 1
                            else:
                                ambas_falso = True
                        if not ambas_falso:
                            pre_dic = {"anio_fiscal": [periodo["anio_fiscal"]]}
                            pre_dic["mes_fiscal"] = [periodo["mes_fiscal"]]
                            pre_dic["fecha_recepcion"] = declaracion_valida_fecha
                            pre_dic["codigo_impuesto"] = codigo_impuesto
                            pre_dic["numero_adhesivo"] = adhesivo_valido
                            pre_dic["c1"] = c1
                            pre_dic["ciclo"] = periodo["ciclo"]
                            listadf_no_cumplian.append(pd.DataFrame(pre_dic))
                        else:
                            lista_son_no_por_revisar.append(df_rango_no_cumplen_2)

                    if len(listadf_no_cumplian) > 0:
                        df_segunda_vuelta = pd.concat(listadf_no_cumplian)

                df_parcial_a = pd.DataFrame()
                df_parcial_b = pd.DataFrame()

                if isinstance(df_cumplen_set, pd.DataFrame):
                    if len(df_cumplen_set.index) > 0:
                        df_parcial_a = df_cumplen_set[["anio_fiscal", "mes_fiscal", "numero_adhesivo", "fecha_recepcion"]]
                        df_parcial_a_maximos = df_parcial_a.groupby(["anio_fiscal", "mes_fiscal", "fecha_recepcion"])['numero_adhesivo'].max().reset_index()
                        df_parcial_a = df_parcial_a_maximos
                        df_parcial_a["c1"] = ''

                if len(df_segunda_vuelta.index):
                    df_parcial_b = df_segunda_vuelta[["anio_fiscal", "mes_fiscal", "numero_adhesivo", "fecha_recepcion", "c1"]]

                if len(df_parcial_a.index) > 0 or len(df_parcial_b.index) > 0:
                    df_cumplen = pd.concat([df_parcial_a, df_parcial_b])
                    df_cumplen_set_x = pd.merge(df_cumplen, df_origen, on=["anio_fiscal", "mes_fiscal", "numero_adhesivo"], how='inner', validate="1:m")
                    df_cumplen_set_x.sort_values(by='mes_fiscal', ascending=True, inplace=True, ignore_index=True)
                    df_cumplen_set_x['fecha_recepcion_x'] = pd.to_datetime(df_cumplen_set_x['fecha_recepcion_x'])
                    df_cumplen_set_x['fecha_recepcion_x'] = df_cumplen_set_x['fecha_recepcion_x'].map(lambda ts: ts.strftime(self.FORMATO_YMD_HMS))
                    df_cumplen_set_x_per = df_cumplen_set_x[["anio_fiscal", "mes_fiscal"]]
                    df_cumplen_set_x_per = df_cumplen_set_x_per.drop_duplicates()

                if len(lista_son_no_por_revisar) > 0:
                    df_no_cumplen_set = pd.concat(lista_son_no_por_revisar)
                    df_no_cumplen_set['fecha_recepcion'] = df_no_cumplen_set['fecha_recepcion'].map(lambda ts: ts.strftime(self.FORMATO_YMD_HMS))
                    df_no_cumplen_set.sort_values(by=['anio_fiscal', 'mes_fiscal'], ascending=True, inplace=True, ignore_index=True)
                    dfperiodofabrica = df_no_cumplen_set[["anio_fiscal", "mes_fiscal"]]
                    dfperiodofabrica = dfperiodofabrica.drop_duplicates()

        if self.tipo_frecuencia == "MIXTO" and not df_multi_periodo.empty:
            df_set_principal_periodos_mix = df_multi_periodo[["anio_fiscal", "mes_fiscal"]]
            df_set_principal_periodos_mix = df_set_principal_periodos_mix.drop_duplicates()

            if isinstance(df_no_cumplen_set, pd.DataFrame) and not df_no_cumplen_set.empty and not df_multi_periodo.empty:
                df_no_cumplen_set = pd.concat([df_no_cumplen_set, df_multi_periodo])
            else:
                df_no_cumplen_set = df_multi_periodo

            df_no_cumplen_set["c1"] = ''
            df_no_cumplen_set['fecha_recepcion'] = df_no_cumplen_set['fecha_recepcion'].astype(self.DATE_TIME_64)

        if self.tipo_frecuencia in ['MIXTO', 'SEMESTRAL_UNICO']:
            self.tipo_frecuencia = "SEMESTRAL"
            _his.frecuenciamiento = self.tipo_frecuencia

        df_periodos__conteos = pd.DataFrame()
        if isinstance(df_cumplen_set_x, pd.DataFrame):
            if not df_cumplen_set_x.empty:
                df_cumplen_set_x = self.set_periocidad(df_cumplen_set_x)

        if isinstance(df_no_cumplen_set, pd.DataFrame):
            if not df_no_cumplen_set.empty:
                df_no_cumplen_set = self.set_periocidad(df_no_cumplen_set)
                df_periodos__conteos = df_no_cumplen_set.groupby('segmento')['periocidad'].nunique().reset_index()
                df_periodos__conteos = df_periodos__conteos.rename(columns={'periocidad': 'conteo'})
                df_no_cumplen_set = pd.merge(df_no_cumplen_set, df_periodos__conteos, how="inner", indicator=True, on=["segmento"], validate="m:m").reset_index()
                df_no_cumplen_set["segmentacion"] = df_no_cumplen_set["segmento"].astype(str) + '_' + df_no_cumplen_set["ciclo"].astype(str)
                df_no_cumplen_set["segmento"] = df_no_cumplen_set["segmentacion"]
                lista_unicos = pd.unique(df_no_cumplen_set["segmento"]).tolist()
                df_segmentos = pd.DataFrame({"segmentados": lista_unicos})

        if isinstance(df_cumplen_set_x, pd.DataFrame):
            df_cumplen_set_x = self.rellenar(df_cumplen_set_x, 0)

        if isinstance(df_no_cumplen_set, pd.DataFrame):
            df_no_cumplen_set = self.rellenar(df_no_cumplen_set, 0)
            df_no_cumplen_set = self.rellenar_cols(df_no_cumplen_set, ["declaracion_cero", "estadentro_del_year", "numero_identificacion", "prescrito2", "sustitutiva_original", "ultima_declaracion"], '')
            df_no_cumplen_set = df_no_cumplen_set.reset_index()
            df_no_cumplen_set = self.borrar_columnas(df_no_cumplen_set, ["level_0", "index", "_merge"])
        return df_cumplen_set_x, df_no_cumplen_set, dfperiodofabrica, len(df_set_principal_periodos.index) + len(df_set_principal_periodos_mix.index), df_segmentos, _sql, _his

    def rellenar(self, df, value):
        '''rellenar '''
        df = df.copy()
        if not df.empty:
            for col in df:
                if df[col].dtype in ("int", "float"):
                    df[col] = df[col].fillna(value)
        return df

    def rellenar_cols(self, df, columnas, valor):
        '''rellenar columnas'''
        df = df.copy()
        if not df.empty:
            for col in columnas:
                if col in df.columns:
                    df[col] = df[col].fillna(valor)
        return df

    def get_declaraciones_periodo(self):
        '''declaraciones periodos'''
        _jd = self.db.uf.pi
        _his = self.db.uf.his
        _sql = RetencionesQ.Declaraciones(_jd)
        _sql.jd.fecha_hoy = self.db.get_fecha_ymd()
        len_cumplen = 0
        len_no_cumplen = 0
        df_cumplen, df_por_revisar, dfperiodofabrica, longitudfabrica, df_segmentos, _sql, _his = self.get_listas_df(_sql, _his)
        if not isinstance(df_cumplen, pd.DataFrame):
            df_cumplen = pd.DataFrame()
        elif not df_cumplen.empty:
            df_cumplen.sort_values(['anio_fiscal', 'mes_fiscal', 'ciclo'], ascending=[True, True, True], inplace=True)
            df_cumplen = self.borrar_columnas(df_cumplen, ["fecha_recepcion_y"])
            df_cumplen.rename(columns={'fecha_recepcion_x': 'fecha_recepcion'}, inplace=True)
            df_cumplen.rename(columns={'c1': 'condicion'}, inplace=True)
            df_cumplen.fecha_recepcion = df_cumplen.fecha_recepcion.astype(str)
            _sql.jd.df = df_cumplen
            _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
            _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_PRE_ANALISIS_PREVIO
            self.guardar_warp_jd(_sql, cabecera=True)
            _sql.jd.df = ''
            len_cumplen = len(df_cumplen.index)

        if not isinstance(df_por_revisar, pd.DataFrame):
            df_por_revisar = pd.DataFrame()

        if not df_por_revisar.empty:
            df_por_revisar.sort_values(['anio_fiscal', 'mes_fiscal', 'ciclo'], ascending=[True, True, True], inplace=True)
            df_por_revisar["fecha_recepcion"] = df_por_revisar["fecha_recepcion"].astype(str)
            df_mensuales_no = df_por_revisar.groupby(['anio_fiscal', 'ciclo'])['mes_fiscal'].nunique().reset_index()
            df_mensuales_no = df_mensuales_no.rename(columns={'mes_fiscal': 'num_limite'})
            df_por_revisar = pd.merge(df_por_revisar, df_mensuales_no, on=["anio_fiscal", "ciclo"], how="inner", validate="m:m")

        df_por_revisar.rename(columns={'numero_adhesivo_x': 'numero_adhesivo'}, inplace=True)
        df_no_cumplen_set, len_no_cumplen = self.db.get_lorentz(df_por_revisar)
        _his.num_declaraciones_cumplen = len_cumplen
        _his.num_declaraciones_no_cumplen = len_no_cumplen
        if not isinstance(dfperiodofabrica, pd.DataFrame):
            dfperiodofabrica = pd.DataFrame()

        dfperiodofabrica_no, longitud_no = self.db.get_lorentz(dfperiodofabrica)
        placebo = str(int(random.uniform(15 << 2, 100000))).zfill(10)
        fecha = _sql.jd.fecha_hoy
        nombre = f"{_sql.jd.contri}_{fecha}_DEC_CONTRI"
        fragmentado = self.db.uf.fragmentar()

        if str(_sql.jd.tramite).strip() == '':
            _sql.jd.tramite = '19042008'

        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd
        pre_dic = f""" <a href="get_informe/{fragmentado}12{placebo}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" """
        pre_dic += f""" download="{nombre}.xlsx" target="_blank" id='dev_a_declas_contri' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Declaraciones</a> """
        enlace_declas = pre_dic

        if str(_sql.jd.tramite).strip() == '19042008':
            _sql.jd.tramite = ''

        resultado = {
            "df_cumplen": df_cumplen.to_dict('records'),
            "df_no_cumplen": df_no_cumplen_set,
            "periodos_no": dfperiodofabrica_no,
            "longitud_no": longitudfabrica,
            "no_cumplen": len_no_cumplen,
            "stat": "V" + str(len_cumplen) + '  P' + str(len_no_cumplen) + "",
            "longitud_no_1": longitud_no,
            "enlace_declas": enlace_declas,
            "segmentados": df_segmentos.to_dict("records")
            }
        return resultado
