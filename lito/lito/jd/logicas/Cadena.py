"""Cadena, desde Abril 2023
Funcionalidades:
  - Segun las declaraciones y litado se arma la cadena.

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

e inician las validaciones del contri

METODOS:

 - fn(get_bus_chains)                   Realiza el encadenamiento

+------------+------------+---------------------------------------------------+
| Fecha      | Modifier   | Descripcion                                       |
+------------+------+-------------------+-------------------------------------+
| 01ABR2023  | jagonzaj   | Se arma la cadena                                 |
|            |            |    y su reporte en pantalla                       |
| 01MAR2023  | jagonzaj   | Se agregan la diferencias para                    |
|            |            |   períodos que pressentan valores duplicados entre|
|            |            |   columnas transpuestas                           |
+------------+------------+-------------+-------------------------------------+

ESTANDAR PEP8  """

import numpy as np
import pandas as pd
import json
import random
import datetime
from timeit import default_timer as timer
from datetime import timedelta
from flask import session

from logicas import Materiales
from datos import Consultas, RetencionesQ
from datos.cortas import a_tres, val_en


class SetEncoder(json.JSONEncoder):
    '''codficacion de algunos objetos json'''
    def default(self, obj):
        '''constructor principal'''
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Iva(Materiales.Universales):
    '''cadenas de iva'''
    def __init__(self, db):
        '''constructor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)

    def F(self, celda):
        '''funcion de revision de las celdas'''
        valor = 0.00
        if isinstance(celda, str):
            celda = celda.replace(",", ".")
            celda = celda.replace("$", "")
            if self.db.uf.sea_texto_real(celda):
                valor = a_tres(float(celda))
            else:
                valor = 0.00
        elif self.db.uf.sea_texto_real(str(celda)):
            valor = a_tres(float(str(celda)))

        return valor

    def get_rellenar_cols(self, df_cambiar,  parametro1, fecha_hoy):
        '''rellenar columnas'''
        df_cambiar["contri"] = parametro1
        df_cambiar["fecha_analisis"] = fecha_hoy
        df_cambiar["estado"] = 'INA'
        df_cambiar["fila"] = np.arange(len(df_cambiar))
        df_cambiar["periodo_inicial"] = self.db.uf.pi.periodo_inicial
        df_cambiar["periodo_final"] = self.db.uf.pi.periodo_finalisima
        df_cambiar["numero_tramite"] = self.db.uf.pi.tramite
        df_cambiar["usuario"] = self.db.uf.pi.usuario

        return df_cambiar

    def get_total_impuesto_a_pagar(self, X, valor_a, valor_b):
        '''total impuesto a pagar'''
        total_impuesto_a_pagar = 0
        if (valor_a + valor_b + val_en(X, "8") + val_en(X, "5")) > val_en(X, "4"):
            total_impuesto_a_pagar = 0
        else:
            total_impuesto_a_pagar = a_tres(val_en(X, "4") - valor_a - valor_b - val_en(X, "8") - val_en(X, "5"))
        return total_impuesto_a_pagar - val_en(X, "13")

    def get_retenciones_a_devolver(self, X, valor_a, valor_b):
        '''valor de retencion a devolver'''
        retenciones_a_devolver = 0
        if valor_a + valor_b + val_en(X, "5") > val_en(X, "4"):
            retenciones_a_devolver = val_en(X, "8")
        elif valor_a + valor_b + val_en(X, "5") + val_en(X, "8") > val_en(X, "4"):
            retenciones_a_devolver = a_tres(valor_a + valor_b + self.F(X.get("5")) + self.F(X.get("8")) - self.F(X.get("4")))
        else:
            retenciones_a_devolver = 0
        return retenciones_a_devolver

    def get_sct_adquisicion_mesanterior(self, X, val_c):
        '''adquisicion mes anterior'''
        sct_adquisicion_mesanterior = val_c
        if self.F(X.get("13")) < 0 and self.F(X.get("15")) < 0:
            sct_adquisicion_mesanterior = a_tres(sct_adquisicion_mesanterior + (self.F(X.get("13")) + self.F(X.get("15"))))
        elif self.F(X.get("13")) < 0 and self.F(X.get("15")) >= 0:
            sct_adquisicion_mesanterior = sct_adquisicion_mesanterior + (self.F(X.get("13")))
        elif self.F(X.get("15")) < 0 and self.F(X.get("13")) >= 0:
            sct_adquisicion_mesanterior = sct_adquisicion_mesanterior + (self.F(X.get("15")))

        if self.F(X.get("18")) < 0 or self.F(X.get("16")) < 0:
            sct_adquisicion_mesanterior = sct_adquisicion_mesanterior + (self.F(X.get("16")) + self.F(X.get("18")))

        return sct_adquisicion_mesanterior

    def get_sct_retenciones_mesanterior(self, X, val_d):
        '''retenciones mes anterior'''
        sct_retenciones_mesanterior = val_d
        if self.F(X.get("14")) < 0 and self.F(X.get("16")) < 0:
            sct_retenciones_mesanterior = val_d + (self.F(X.get("14")) + self.F(X.get("16")))
        elif self.F(X.get("14")) < 0 and self.F(X.get("16")) >= 0:
            sct_retenciones_mesanterior = val_d + (self.F(X.get("14")))

        if self.F(X.get("19")) < 0 or self.F(X.get("17")) < 0:
            sct_retenciones_mesanterior = sct_retenciones_mesanterior + (self.F(X.get("17")) + self.F(X.get("19")))

        return sct_retenciones_mesanterior

    def destino_123_iva(self, df, parametro3, parametro4):
        '''destino mes anterior'''
        lis_sct_adquisicion_mesanterior = []
        lis_sct_retenciones_mesanterior = []
        lis_ct_adq_proximo_mes = []
        lis_ct_ret_proximo_mes = []
        lis_total_impuesto_a_pagar = []
        lis_retenciones_a_devolver = []
        jd = 1
        val_c = 0
        val_d = 0
        for (columna, celdavalor) in df.items():
            lista = celdavalor.values
            ix = 0
            X = {"0": "CAMINO"}
            for elemento in lista:
                ix += 1
                X[f"{ix}"] = str(elemento).replace("$", "").replace(",", "")
            adq = 0
            ret = 0
            adq = self.F(X.get("6"))
            ret = self.F(X.get("7"))
            val_a = 0
            val_b = 0
            val_e = 0
            val_f = 0
            if jd == 1:
                val_15 = self.F(X.get("15"))
                val_16 = self.F(X.get("16"))
                if self.F(parametro3) != -1:
                    adq = self.F(parametro3)
                    X["6"] = str(adq)
                if self.F(parametro4) != -1:
                    ret = self.F(parametro4)
                    X["7"] = str(ret)
                df.at["sct_adquisicion_mesanterior", columna] = a_tres(adq + val_15 if val_15 < 0 else adq)
                val_a = a_tres(adq + val_15 if val_15 < 0 else adq)
                df.at["sct_retenciones_mesanterior", columna] = a_tres(ret + val_16 if val_16 < 0 else ret)
                val_b = a_tres(ret + val_16 if val_16 < 0 else ret)
            else:
                X["6"] = str(val_c)
                X["7"] = str(val_d)
                val_a = a_tres(self.get_sct_adquisicion_mesanterior(X, val_c)) - (self.F(X.get("20")))
                df.at["sct_adquisicion_mesanterior", columna] = val_a
                val_b = a_tres(self.get_sct_retenciones_mesanterior(X, val_d))
                df.at["sct_retenciones_mesanterior", columna] = val_b

            val_c = a_tres(self.get_ct_adq_proximo_mes_v2(X, val_a, val_b))
            df.at["ct_adq_proximo_mes", columna] = val_c
            val_d = a_tres(self.get_ct_ret_proximo_mes_v2(X, val_a, val_b))
            df.at["ct_ret_proximo_mes", columna] = val_d
            val_e = a_tres(self.get_total_impuesto_a_pagar(X, val_a, val_b))
            df.at["total_impuesto_a_pagar", columna] = val_e
            val_f = a_tres(self.get_retenciones_a_devolver(X, val_a, val_b))
            df.at["retenciones_a_devolver", columna] = val_f
            ix += 1

            lis_sct_adquisicion_mesanterior.append(val_a)
            lis_sct_retenciones_mesanterior.append(val_b)
            lis_ct_adq_proximo_mes.append(val_c)
            lis_ct_ret_proximo_mes.append(val_d)
            lis_total_impuesto_a_pagar.append(val_e)
            lis_retenciones_a_devolver.append(val_f)
            jd += 1

        return df, lis_sct_adquisicion_mesanterior, lis_sct_retenciones_mesanterior,  lis_ct_adq_proximo_mes, lis_ct_ret_proximo_mes, lis_total_impuesto_a_pagar, lis_retenciones_a_devolver

    def get_ct_adq_proximo_mes_v2(self, X, valor_a, valor_b):
        '''saldo credito tributario mes anterior'''
        resultado = 0
        match X.get("1"):
            case '1':
                if valor_a >= 0:
                    if valor_a > self.F(X.get("4")):
                        if valor_b < 0:
                            if valor_a + valor_b - self.F(X.get("4")) > 0:
                                resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                            else:
                                resultado = 0.0
                        else:
                            resultado = self.db.uf.redondear(valor_a - self.F(X.get("4")), 3)
                    else:
                        resultado = 0.0
                else:
                    resultado = 0.0

            case '2':
                if valor_b >= 0:
                    if valor_b > self.F(X.get("4")):
                        if valor_a > 0:
                            resultado = self.db.uf.redondear(valor_a, 3)
                        else:
                            resultado = 0.00
                    elif valor_a + valor_b > self.F(X.get("4")):
                        resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                    else:
                        resultado = 0.00
                elif valor_a + valor_b - self.F(X.get("4")) > 0:
                    resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                else:
                    resultado = 0.00

            case '3':
                if valor_a >= 0:
                    if valor_a > self.F(X.get("4")):
                        if valor_b > 0:
                            resultado = self.db.uf.redondear(valor_a - self.F(X.get("4")), 3)
                        elif valor_a + valor_b - self.F(X.get("4")) > 0:
                            resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                        else:
                            resultado = 0.00
                    else:
                        resultado = 0.00
            case '':
                if valor_a + self.F(X.get("5")) > 0:
                    resultado = valor_a + self.F(X.get("5"))
                else:
                    resultado = 0.00

            case '4':
                if valor_a > self.F(X.get("4")):
                    resultado = valor_b - self.F(X.get("4"))
                else:
                    resultado = 0.00
            case _:
                resultado = 0.00
        return resultado

    def get_ct_ret_proximo_mes_v2(self, X, valor_a, valor_b):
        '''saldo credito tributario proximo mes'''
        resultado = 0
        match X.get("1"):
            case '1':
                if valor_b > 0:
                    if valor_a > self.F(X.get("4")):
                        resultado = valor_b

                    elif self.F(X.get("6")) >= 0:
                        if valor_a + valor_b > self.F(X.get("4")):
                            resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                        else:
                            resultado = 0.0
                    elif valor_a + valor_b - self.F(X.get("4")) > 0:
                        resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                    else:
                        resultado = 0.0
                else:
                    resultado = 0.0

            case '2':
                if valor_b > 0:
                    if valor_b > self.F(X.get("4")):
                        if valor_a > 0:
                            resultado = self.db.uf.redondear(valor_b - self.F(X.get("4")), 3)

                        elif valor_a + valor_b - self.F(X.get("4")) > 0:
                            resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                        else:
                            resultado = 0.00
                    else:
                        resultado = 0.00
                else:
                    resultado = 0.00

            case '3':
                if valor_a > 0:
                    if valor_a > self.F(X.get("4")):
                        if valor_b > 0:
                            resultado = self.db.uf.redondear(valor_b, 3)
                        else:
                            resultado = 0.00
                    elif valor_a + valor_b - self.F(X.get("4")) > 0:
                        resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                    else:
                        resultado = 0.00
                elif valor_a + valor_b - self.F(X.get("4")) > 0:
                    resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                else:
                    resultado = 0.00

            case '':
                if valor_b > 0:
                    resultado = valor_b
                else:
                    resultado = 0.00
            case '4':
                if valor_a > 0:
                    if valor_a > self.F(X.get("4")):
                        if valor_b > 0:
                            resultado = self.db.uf.redondear(valor_b, 3)
                        else:
                            resultado = 0.00
                    elif valor_a + valor_b > self.F(X.get("4")):
                        resultado = self.db.uf.redondear(valor_a + valor_b - self.F(X.get("4")), 3)
                    else:
                        resultado = 0.00

                elif valor_b > 0 and valor_b > self.F(X.get("4")):
                    resultado = self.db.uf.redondear(valor_b - self.F(X.get("4")), 3)
                else:
                    resultado = 0.00
            case _:
                resultado = 0.00
        return resultado

    def get_bus_chains(self):
        '''cambios en la cadena'''
        start = timer()
        _jd = self.db.uf.pi
        _jd.fecha_hoy = self.db.get_fecha_ymd()
        _his = self.db.uf.his
        _sql = RetencionesQ.Chain(_jd)
        atencion_en = '0'
        _his.time_graba_cadena = self.db.get_fecha_ymd_hms()
        p6_l = []
        if _jd.valores_arrastre_p6 and len(_jd.valores_arrastre_p6.strip()) > 0:
            lista = (_jd.valores_arrastre_p6.replace("'", '').replace("[", "").replace("]", "")) .split(',')
            p6_l = list(map(float, lista))
        p7_l = []
        if _jd.valores_analizados_p7 and len(_jd.valores_analizados_p7.strip()) > 0:
            _jd.valores_analizados_p7 = _jd.valores_analizados_p7.replace('$', '')
            lista = (_jd.valores_analizados_p7.replace("'", '').replace("[", "").replace("]", "")) .split(',')
            p7_l = list(map(float, lista))

        p67_l_am = []
        if _jd.valores_analizados_6_7_am and len(_jd.valores_analizados_6_7_am.strip()) > 0:
            _jd.valores_analizados_6_7_am = _jd.valores_analizados_6_7_am.replace('$', '')
            lista = (_jd.valores_analizados_6_7_am.replace("'", '').replace("[", "").replace("]", "")) .split(',')
            lista = lista[: -1]
            p67_l_am = list(map(str, lista))
        existe_proceso = self.db.get_scalar(_sql.get_sql_cadena_iva_existe())
        if existe_proceso == 0:
            df = self.db.get_vector(_sql.get_sql_cadena_iva())
        else:
            df = self.db.get_vector(_sql.get_sql_cadena_iva_procesado())

        df = df.copy()
        df1 = pd.DataFrame()
        df_resumen_periodos = pd.DataFrame()
        df_liquidacion = pd.DataFrame()
        df_analizados = pd.DataFrame()
        df_resultados = pd.DataFrame()
        df_verifica = pd.DataFrame()
        df_historia = pd.DataFrame()
        df_supervisores = pd.DataFrame()
        enlace = ''
        enlace_infos = ''
        vrv = 'valor_retencion_valida'

        if isinstance(df_resumen_periodos, pd.DataFrame):
            df_resumen_periodos = df_resumen_periodos.to_dict("records")
        if isinstance(df_liquidacion, pd.DataFrame):
            df_liquidacion = df_liquidacion.to_dict("records")
        if isinstance(df_analizados, pd.DataFrame):
            df_analizados = df_analizados.to_dict("records")
        if isinstance(df_resultados, pd.DataFrame):
            df_resultados = df_resultados.to_dict("records")
        if isinstance(df_verifica, pd.DataFrame):
            df_verifica = df_verifica.to_dict("records")

        if not df.empty:
            df[vrv] = df[vrv].apply(a_tres)
            valor_solo_adq = 0.0
            if float(_jd.adquisiciones_txt) >= 0.0:
                valor_solo_adq = float(_jd.adquisiciones_txt) - float(df['ajuste_x_adquisiciones'].values[0])
            if valor_solo_adq < 0:
                valor_solo_adq = 0
            else:
                valor_solo_adq = self.db.uf.redondear(valor_solo_adq, 3)
            if float(_jd.adquisiciones_txt) >= 0.0:
                _jd.adquisiciones_txt = valor_solo_adq

            print(f"_sql.jdg.adquisiciones_txt   {_jd.adquisiciones_txt}")

            df["anio_borrar"] = df["anio"].astype(int)
            df["mes_borrar"] = df["mes"].astype(str)
            df["mes_borrar"] = df["mes_borrar"].str.zfill(2)

            if len(p6_l) > 0:
                df_analizados_periodos = self.db.get_vector(_sql.get_sql_periodos_analizados())
                if not df_analizados_periodos.empty:
                    df_6 = pd.DataFrame()
                    p67_l_a = [x[:4] for x in p67_l_am if len(x) > 0]
                    p67_l_m = [x[4:6] for x in p67_l_am if len(x) > 0]
                    if len(p67_l_a) == len(p67_l_m) == len(p6_l):
                        df_6 = pd.DataFrame({"anio": p67_l_a, "mes": p67_l_m, "valor_retencion_valida": p6_l})

                    df_analizados_periodos["anio"] = df_analizados_periodos["anio"].astype(int)
                    df_analizados_periodos["mes"] = df_analizados_periodos["mes"].astype(str)
                    for ix, fila in df_6.iterrows():
                        anio = int(fila["anio"])
                        mes = str(fila["mes"]).zfill(2)
                        monto = fila["valor_retencion_valida"]
                        df.loc[(df["anio_borrar"] == anio) & (df["mes_borrar"] == mes), "valor_retencion_valida"] = monto
                        ix = ix * -1

            if "anio_borrar" in df.columns:
                df.drop("anio_borrar", axis=1, inplace=True)

            if "mes_borrar" in df.columns:
                df.drop("mes_borrar", axis=1, inplace=True)

            df.sort_values(by=['anio', 'mes'],
                           ascending=True,
                           inplace=True, ignore_index=True)
            df.index.rename('variable', inplace=True)
            df2 = df.copy()
            df2["contri"] = _jd.contri
            df2["fecha_analisis"] = _sql.jd.fecha_hoy
            df.fillna(0)
            df1 = df.T

            df1["descripcion"] = df1.index
            df1, lis_sct_adquisicion_mesanterior, lis_sct_retenciones_mesanterior, lis_ct_adq_proximo_mes, lis_ct_ret_proximo_mes, lis_total_impuesto_a_pagar, lis_retenciones_a_devolver\
                = self.destino_123_iva(df1, _jd.adquisiciones_txt, _jd.retenciones_txt)
            df1 = df1.round(2)
            df_warp = df1.T
            if "retenciones_fuente_iva" in df_warp.columns:
                df_warp.drop("retenciones_fuente_iva", axis=1, inplace=True)

            _sql.jd.df = df_warp
            _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
            _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_CAD_IVA_PROCESA
            self.guardar_warp_jd(_sql)
            _sql.jd.df = ''

            lis_sct_adquisicion_mesanterior = lis_sct_adquisicion_mesanterior[:-1]
            lis_sct_retenciones_mesanterior = lis_sct_retenciones_mesanterior[:-1]
            lis_ct_adq_proximo_mes = lis_ct_adq_proximo_mes[:-1]
            lis_ct_ret_proximo_mes = lis_ct_ret_proximo_mes[:-1]
            lis_retenciones_a_devolver = lis_retenciones_a_devolver[:-1]
            lis_total_impuesto_a_pagar = lis_total_impuesto_a_pagar[:-1]

            sret_a = 'sct_retenciones_mesanterior'
            sadq_a = 'sct_adquisicion_mesanterior'
            df2[sret_a] = lis_sct_retenciones_mesanterior
            df2[sadq_a] = lis_sct_adquisicion_mesanterior
            df2["ct_adq_proximo_mes"] = lis_ct_adq_proximo_mes
            df2["ct_ret_proximo_mes"] = lis_ct_ret_proximo_mes
            df2["total_impuesto_a_pagar"] = lis_total_impuesto_a_pagar
            df2["retenciones_a_devolver"] = lis_retenciones_a_devolver
            df2[sret_a] = df2[sret_a].apply(a_tres)
            df2[sadq_a] = df2[sadq_a].apply(a_tres)
            df2['ct_adq_proximo_mes'] = df2['ct_adq_proximo_mes'].apply(a_tres)
            df2['ct_ret_proximo_mes'] = df2['ct_ret_proximo_mes'].apply(a_tres)
            df2['total_impuesto_a_pagar'] = df2['total_impuesto_a_pagar'].apply(a_tres)
            df2['retenciones_a_devolver'] = df2['retenciones_a_devolver'].apply(a_tres)
            df2['valor_retencion_valida'] = df2['valor_retencion_valida'].apply(a_tres)
            df_resumen_periodos = []
            df_liquidacion = []
            df_analizados = []
            df_resultados = []
            df_verifica = []
            if int(_jd.grabar) == 1:
                df2["anio"] = df2["anio"].astype(int)
                df2["mes"] = df2["mes"].astype(int)
                df_resumen_periodos = df2[["anio", "mes", "total_impuesto_a_pagar", "retenciones_a_devolver"]]
                df_resumen_periodos.loc[:, 'total_impuesto_a_pagar'] *= 1
                df_resumen_periodos.eval("saldos = total_impuesto_a_pagar - retenciones_a_devolver", inplace=True)
                df_resumen_periodos = df_resumen_periodos.fillna(0)
                df_resumen_periodos["anio"] = df_resumen_periodos["anio"].astype(str)
                df_resumen_periodos["mes"] = df_resumen_periodos["mes"].astype(str)
                df_resumen_periodos.loc['Column_Total'] = df_resumen_periodos.sum(numeric_only=True, axis=0)
                df_resumen_periodos = df_resumen_periodos.reset_index()
                df_resumen_periodos = df_resumen_periodos.drop(['variable'], axis=1)
                df_resumen_periodos.loc[df_resumen_periodos.index[-1], 'anio'] = ''
                df_resumen_periodos.loc[df_resumen_periodos.index[-1], 'mes'] = ''
                df_resumen_periodos['saldos'] = df_resumen_periodos['saldos'].apply(lambda x: self.db.uf.redondear(x, 3))

                _jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                _jd.tabla_relacional = self.db.config.TB_PG_DEV_RESUMEN_PERIODO
                _jd.tabla_esquema = f"{_jd.esquema}.{_jd.tabla_relacional}"
                self.db.get_reseto_tabla_estandar_jd(_sql)
                if not df_resumen_periodos.empty:
                    df_resumen_periodos["anio"] = df_resumen_periodos["anio"].replace('', 0)
                    df_resumen_periodos["mes"] = df_resumen_periodos["mes"].replace('', 0)
                    df_resumen_periodos["anio"] = df_resumen_periodos["anio"].astype(int)
                    df_resumen_periodos["mes"] = df_resumen_periodos["mes"].astype(int)
                    _sql.jd.df = df_resumen_periodos
                    df_grabar_rp = self.get_rellenar_cols_jd(_sql)
                    df_grabar_rp = df_grabar_rp.head(df_resumen_periodos.shape[0] - 1)
                    _sql.jd.df = df_grabar_rp
                    self.db.guardar_dataframe_jd(_sql)
                    _sql.jd.df = ''

                df_resultantes = df2.copy()
                df_resultantes["diferencia_arr_ct"] = df_resultantes["diferencia_arr_ct"].astype(float)
                df_resultantes["diferencia_x_ct"] = df_resultantes["diferencia_x_ct"].astype(float)
                df_resultantes["diferencia_adquisiciones"] = df_resultantes["diferencia_adquisiciones"].astype(float)
                df_resultantes["diferencia_retenciones"] = df_resultantes["diferencia_retenciones"].astype(float)

                retenciones_validas = df_resultantes["valor_retencion_valida"].sum()
                ajuste_x_adquisiciones_suma = df_resultantes["ajuste_x_adquisiciones"].sum()
                diferencia_adquisiciones_suma = df_resultantes.query("diferencia_adquisiciones > 0 ")['diferencia_adquisiciones'].sum()
                diferencia_retenciones_suma = df_resultantes.query("diferencia_retenciones > 0 ")['diferencia_retenciones'].sum()
                diferencia_arr_ct_suma = df_resultantes.query("diferencia_arr_ct > 0 ")['diferencia_arr_ct'].sum()
                diferencia_x_ct_suma = df_resultantes.query("diferencia_x_ct > 0 ")['diferencia_x_ct'].sum()

                diferencia_adquisiciones_suma_men0 = df_resultantes.query("diferencia_adquisiciones < 0 ")['diferencia_adquisiciones'].sum()
                diferencia_retenciones_suma_men0 = df_resultantes.query("diferencia_retenciones < 0 ")['diferencia_retenciones'].sum()
                diferencia_arr_ct_suma_men0 = df_resultantes.query("diferencia_arr_ct < 0 ")['diferencia_arr_ct'].sum()
                diferencia_x_ct_suma_men0 = df_resultantes.query("diferencia_x_ct < 0 ")['diferencia_x_ct'].sum()

                if (_jd.adquisiciones_normal == ''):
                    _jd.adquisiciones_normal = '0'
                sct_adquisicion_mesanterior_f1 = float(_jd.adquisiciones_normal)
                sct_retenciones_mesanterior_f1 = 0
                if 'sct_retenciones_mesanterior' in df_resultantes.columns and len(df_resultantes.index) > 0:
                    sct_retenciones_mesanterior_f1 = df_resultantes['sct_retenciones_mesanterior'].values[0]

                col_a = float(df_resultantes["impuesto_causado"].sum()) - float(df_resultantes["tot_impuesto_pagar_x_percepcion"].sum())
                col_b = float(df_resultantes["ct_mes_actual"].sum()) + (diferencia_adquisiciones_suma_men0 + diferencia_retenciones_suma_men0 + diferencia_arr_ct_suma_men0 + diferencia_x_ct_suma_men0) - ajuste_x_adquisiciones_suma
                saldo_favor = retenciones_validas + sct_adquisicion_mesanterior_f1 + sct_retenciones_mesanterior_f1 - float(col_a-col_b)
                df_resultantes["ct_adq_proximo_mes"] = df_resultantes["ct_adq_proximo_mes"].astype(float)
                df_resultantes["ct_ret_proximo_mes"] = df_resultantes["ct_ret_proximo_mes"].astype(float)

                ct_adq_proximo_mes_fn = 0
                ct_ret_proximo_mes_fn = 0
                sct_x_adquisiciones = 0
                sct_x_retenciones = 0
                if not df_resultantes.empty:
                    ct_adq_proximo_mes_fn = df_resultantes['ct_adq_proximo_mes'].iat[-1]
                    ct_ret_proximo_mes_fn = df_resultantes['ct_ret_proximo_mes'].iat[-1]
                    sct_x_adquisiciones = df_resultantes['sct_x_adquisiciones'].iat[-1]
                    sct_x_retenciones = df_resultantes['sct_x_retenciones'].iat[-1]

                retenciones_devolver = 0
                if saldo_favor - (ct_adq_proximo_mes_fn + ct_ret_proximo_mes_fn) > 0:
                    retenciones_devolver = self.db.uf.redondear(saldo_favor - (ct_adq_proximo_mes_fn + ct_ret_proximo_mes_fn), 3)

                impuesto_pagar = 0
                if saldo_favor - (ct_adq_proximo_mes_fn + ct_ret_proximo_mes_fn) < 0:
                    impuesto_pagar = self.db.uf.redondear(saldo_favor - (ct_adq_proximo_mes_fn + ct_ret_proximo_mes_fn), 3)

                # R2 cuadro de liquidacion
                _his.monto_a_devolver_calculado = retenciones_devolver
                df_liquidacion = pd.DataFrame({"detalle": self.db.config.CAMPOS_LIQUIDACION,
                                               "valor": [col_a, col_b,
                                                         col_a - col_b,
                                                         sct_adquisicion_mesanterior_f1, sct_retenciones_mesanterior_f1,
                                                         retenciones_validas,
                                                         saldo_favor,
                                                         ct_adq_proximo_mes_fn, ct_ret_proximo_mes_fn, retenciones_devolver,
                                                         0,
                                                         retenciones_devolver,
                                                         impuesto_pagar
                                                         ]})
                df_liquidacion = df_liquidacion.round(2)
                _jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                _jd.tabla_relacional = self.db.config.TB_PG_DEV_CUADRO_LIQUIDACION
                _jd.tabla_esquema = f"{_jd.esquema}.{_jd.tabla_relacional}"
                self.db.get_reseto_tabla_estandar_jd(_sql)

                if not df_liquidacion.empty:
                    _sql.jd.df = df_liquidacion
                    df_grabar = self.get_rellenar_cols_jd(_sql)
                    df_grabar = df_grabar.drop('detalle', axis=1)
                    _sql.jd.df = df_grabar
                    self.db.guardar_dataframe_jd(_sql)
                    _sql.jd.df = ''
                total_dfr3 = 0
                df_analizados = pd.DataFrame()
                ct_incrementado_adq = float(diferencia_arr_ct_suma) + float(diferencia_adquisiciones_suma)
                ct_incrementado_ret = float(diferencia_x_ct_suma) + float(diferencia_retenciones_suma)

                if len(p7_l) > 0:
                    df_analizados = pd.DataFrame({"detalle": ['VALOR A RECONOCER POR RETENCIONES',
                                                              'NO CONSTAN EN BASE (NB) ',
                                                              'VALOR NO SUSTENTADO ',
                                                              'VALOR NEGADO ',
                                                              'DIFERENCIAS EN VALOR DECLARADO VS. LIBROS MAYORES',
                                                              'CRÉDITO TRIBUTARIO PARA EL PRÓXIMO MES DE ACUERDO A ANÁLISIS ADQUISICIIONES',
                                                              'CRÉDITO TRIBUTARIO PARA EL PRÓXIMO MES DE ACUERDO A ANÁLISIS RETENCIONES',
                                                              'CT INCREMENTADO INJUSTIFICADAMENTE POR EL CONTRIBUYENTE ADQUISICIONES',
                                                              'CT INCREMENTADO INJUSTIFICADAMENTE POR EL CONTRIBUYENTE RETENCIONES',
                                                              'TOTAL VALORES ANÁLIZADOS'],
                                                  "valor": [retenciones_devolver, p7_l[4], p7_l[5], p7_l[6], p7_l[2],
                                                            self.db.uf.redondear(float(ct_adq_proximo_mes_fn), 3),
                                                            self.db.uf.redondear(float(ct_ret_proximo_mes_fn), 3),
                                                            ct_incrementado_adq,
                                                            ct_incrementado_ret,
                                                            0]})

                    total_dfr3 = df_analizados['valor'].sum()
                    df_analizados.iat[len(df_analizados.index)-1, 1] = total_dfr3
                    df_analizados = df_analizados.round(3)
                    _jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                    _jd.tabla_relacional = self.db.config.TB_PG_DEV_RESUMEN_ANALIZADOS
                    _jd.tabla_esquema = f"{_jd.esquema}.{_jd.tabla_relacional}"
                    self.db.get_reseto_tabla_estandar_jd(_sql)
                    if not df_analizados.empty:
                        _sql.jd.df = df_analizados
                        df_grabar = self.get_rellenar_cols_jd(_sql)
                        df_grabar = df_grabar.drop('detalle', axis=1)
                        _sql.jd.df = df_grabar
                        self.db.guardar_dataframe_jd(_sql)
                        _sql.jd.df = ''

                # R3.5  diferencia en cadena
                dif_cadena = self.db.uf.redondear(float(total_dfr3) - float(sct_x_adquisiciones) - float(sct_x_retenciones), 3)
                df_verifica = pd.DataFrame({"detalle": ['(+) TOTAL VALORES ANÁLIZADOS',
                                                        '(-) CREDITO TRIBUTARIO PARA EL PROXIMO MES DECLARADO EN EL ULTIMO MES ANALIZADO (ADQUISICIONES E IMPORTACIONES)',
                                                        '(-) CREDITO TRIBUTARIO PARA EL PROXIMO MES DECLARADO EN EL ULTIMO MES ANALIZADO (RETENCIONES)',
                                                        'DIFERENCIA EN CADENA A REVISAR'],
                                            "valor1": [total_dfr3, sct_x_adquisiciones, sct_x_retenciones, dif_cadena],
                                            "valor2": ['',
                                                       'Traer el último valor declarado como CT para el próximo mes',
                                                       'Traer el último valor declarado como CT para el próximo mes', 'Revisar Diferencia' if dif_cadena != 0 else 'OK']
                                            })
                df_verifica = df_verifica.round(2)
                _jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                _jd.tabla_relacional = self.db.config.TB_PG_DEV_RESUMEN_VERIFICA
                _jd.tabla_esquema = f"{_jd.esquema}.{_jd.tabla_relacional}"
                self.db.get_reseto_tabla_estandar_jd(_sql)
                if not df_verifica.empty:
                    _sql.jd.df = df_verifica
                    df_grabar = self.get_rellenar_cols_jd(_sql)
                    df_grabar = df_grabar.drop('detalle', axis=1)
                    _sql.jd.df = df_grabar
                    self.db.guardar_dataframe_jd(_sql)
                    _sql.jd.df = ''

                dividir_adq_ret = self.db.get_scalar(_sql.get_sql_dividir_adq_ret())
                elementos_adq_ret = []
                if (dividir_adq_ret):
                    elementos_adq_ret = dividir_adq_ret.split(",")

                if len(elementos_adq_ret) == 0:
                    elementos_adq_ret.append(0)
                    elementos_adq_ret.append(0)

                total_negados_ret = 0.00
                if len(p7_l) > 0:
                    total_negados_ret = total_negados_ret + self.db.uf.redondear(float(p7_l[4]), 3) + self.db.uf.redondear(float(p7_l[5]), 3) + self.db.uf.redondear(float(p7_l[2]), 3) + self.db.uf.redondear(float(p7_l[6]), 3)

                total_analizados_adq = self.db.uf.redondear(float(sct_x_adquisiciones) - float(ct_incrementado_adq), 3)
                total_analizados_ret = self.db.uf.redondear(float(sct_x_retenciones) - float(ct_incrementado_ret) - float(retenciones_devolver) - float(total_negados_ret), 3)
                # 'DIFERENCIA ENTRE CRÉDITO TRIBUTARIO INICIAL DECLARADO MENOS CRÉDITO TRIBUTARIO INICIAL DE LA CADENA',
                r4_dif_revisar = abs(total_analizados_adq) - abs(ct_adq_proximo_mes_fn)
                r4_dif_revisar_prox_mes = abs(total_analizados_ret) - abs(ct_ret_proximo_mes_fn)
                df_resultados = pd.DataFrame({"detalle": ['VALOR DECLARADO',
                                                          'CT INCREMENTADO INJUSTIFICADAMENTE POR EL CONTRIBUYENTE',
                                                          'RETENCIONES A FAVOR DEL CONTRIBUYENTE',
                                                          'NEGADOS / NO CONSTAN BASE/ NO SUSTENTADOS / DIF. MAYORES',
                                                          'TOTAL VALORES ANALIZADOS',
                                                          'VALOR FINAL DE LA CADENA',
                                                          'DIFERENCIAS A REVISAR'],
                                              "valor1": [float(sct_x_adquisiciones), ct_incrementado_adq, '', '',
                                                         total_analizados_adq, ct_adq_proximo_mes_fn,
                                                         'OK' if float(r4_dif_revisar) == 0.0 else self.db.uf.redondear(r4_dif_revisar, 3)
                                                         ],
                                              "valor2": [float(sct_x_retenciones), ct_incrementado_ret, retenciones_devolver, total_negados_ret,
                                                         abs(total_analizados_ret),
                                                         ct_ret_proximo_mes_fn,
                                                         'OK' if float(r4_dif_revisar_prox_mes) == 0.0 else self.db.uf.redondear(r4_dif_revisar_prox_mes, 3)
                                                         ]
                                              })

                df_resultados = df_resultados.round(2)
                _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_RESUMEN_RESULTADOS
                _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                self.db.get_reseto_tabla_estandar_jd(_sql)
                if not df_resultados.empty:
                    _sql.jd.df = df_resultados
                    df_grabar = self.get_rellenar_cols_jd(_sql)
                    df_grabar = df_grabar.drop('detalle', axis=1)
                    _sql.jd.df = df_grabar.copy()
                    self.db.guardar_dataframe_jd(_sql)
                    _sql.jd.df = ''

                numero_veces = self.db.get_scalar(_sql.get_sql_num_veces_pre_cad_iva())
                if numero_veces > 0:
                    self.db.get_actualizar(_sql.get_sql_borrar_pre_cad_iva())

                df_resumen_periodos = df_resumen_periodos.to_dict("records")
                df_liquidacion = df_liquidacion.to_dict('records')
                df_analizados = df_analizados.to_dict('records')
                df_verifica = df_verifica.to_dict('records')
                df_resultados = df_resultados.to_dict('records')
                df2["estado"] = 'INA'
                df2["diferencia_arr_ct"] = df2["diferencia_arr_ct"].astype(float)
                df2["diferencia_x_ct"] = df2["diferencia_x_ct"].astype(float)
                df2["diferencia_adquisiciones"] = df2["diferencia_adquisiciones"].astype(float)
                df2["diferencia_retenciones"] = df2["diferencia_retenciones"].astype(float)
                df2 = df2.drop('ct_adq_proximo_mes', axis=1)
                df2 = df2.drop('ct_ret_proximo_mes', axis=1)
                df2["periodo_inicial"] = _sql.jd.periodo_inicial
                df2["periodo_final"] = _sql.jd.periodo_final
                _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_PRE_CADENA_IVA
                _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                _sql.jd.df = df2
                self.guardar_warp_jd(_sql, True)
                _sql.jd.df = ''

            df1 = df1.replace(np.nan, 0)
            df1 = df1.replace('nan', 0)
            df1 = df1.reset_index()
            df1.columns = [f"fx_{i+1}" for i in range(df1.shape[1])]

            df1 = df1.round(3)
            fecha = _jd.fecha_hoy
            nombre = f"{_jd.contri}_{fecha}_"
            fragmentado = self.db.uf.fragmentar()
            placebo = str(int(random.uniform(15, 100000))).zfill(10)

            if str(_jd.tramite).strip() == '':
                _jd.tramite = '19042008'

            enlace = f""" <a href="get_informe/{fragmentado}02{placebo}/{_jd.tramite}/{_jd.usuario}/{_jd.num_acceso}" download="{nombre}_CADIVA.xlsx" """
            enlace += """ target="_blank" id='dev_a_cadiva' class="btn btn-soft-dark btn-border a_desca_interna">Descargar CA</a> """
            placebo = str(int(random.uniform(15, 100000))).zfill(10)
            enlace_infos = f""" <a href="get_informe/{fragmentado}04{placebo}/{_jd.tramite}/{_jd.usuario}/{_jd.num_acceso}" download="{nombre}_VALIDA.xlsx" """
            enlace_infos += """ target="_blank" id='dev_a_informes' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Validaciones</a> """

            if _jd.tramite == '19042008':
                _jd.tramite = ''

            _jd.razon_social = self.db.get_scalar(_sql.get_sql_razon_social_())
            end = timer()
            _his.time_procesa_cadena = str(timedelta(seconds=end-start))
            df_supervisores = pd.DataFrame()
            if int(_jd.grabar) == 1:
                df_historia, _his = self.proyectar_historia(_sql, _his)
                df_supervisores = self.db.get_vector(_sql.get_sql_supervisores_())
            else:
                df_historia = pd.DataFrame()

            session.modified = True
            fecha_actual = self.db.get_fecha_ymd()
            _sql.jd.df = ''
            self.db.uf.his = _his
            self.db.uf.pi = _sql.jd
            st_time = datetime.datetime.strptime(_his.time_inicia, "%Y-%m-%d %H:%M:%S")
            ed_time = datetime.datetime.strptime(str(fecha_actual), "%Y-%m-%d %H:%M:%S")
            differ = (ed_time - st_time).total_seconds()
            atencion_en = str(datetime.timedelta(seconds=differ))
            print(f"{self.db.uf.CYAN} _____________   {fecha_actual}  (CHAIN REWRITE) CON EL ACCESO  {_jd.num_acceso} para el usuario {_jd.usuario} tramite {_jd.tramite}  {self.db.uf.RESET} ")
            print(f"{self.db.uf.GREEN} _____________ATENDIDO EN :  {atencion_en} ______s_____   {self.db.uf.RESET} ")
        else:
            print(f" NO EXISTEN RETENCIONES PAR PROCESAR en {_jd.num_acceso} para el usuario {_jd.usuario} tramite {_jd.tramite}  ")

        resultado = {
            "declas": df1.to_dict('records'),
            "nfilas":  len(df1.columns)-1,
            "resumen1": df_resumen_periodos,
            "resumen2": df_liquidacion,
            "resumen3": df_analizados,
            "resumen4": df_resultados,
            "resumen3_5": df_verifica,
            "enlace": enlace,
            "enlace_infos": enlace_infos,
            "historia": df_historia.to_dict('records'),
            "supervisores": df_supervisores.to_dict('records'),
            "atendido_en": atencion_en,
            "valida": 1
        }

        return resultado

    def proyectar_historia(self, _sql, _his):
        '''historia del caso para mensajes de cierre'''
        dt_snt_varios = self.db.get_vector(_sql.get_sql_snt_datos_cadena())
        if not dt_snt_varios.empty:
            _his.snt_fecha_ingreso = dt_snt_varios['fecha_ingreso'].iloc[0]
            _his.snt_monto_solicitado = dt_snt_varios['monto_solicitado'].iloc[0]
            _his.snt_monto_a_devolver = dt_snt_varios['monto_a_devolver'].iloc[0]

        df_historia = pd.DataFrame({"contri": [_sql.jd.contri], "razon_social": [_sql.jd.razon_social], "fecha_ingreso": [_his.snt_fecha_ingreso],
                                    "monto_solicitado": [_his.snt_monto_solicitado], "monto_a_devolver": [_his.snt_monto_a_devolver],
                                    "periodo_inicial": [_sql.jd.periodo_inicial], "periodo_final": [_sql.jd.periodo_final],
                                    "devolver": [0], "tramite": [_sql.jd.tramite]
                                    })
        return df_historia, _his

    def get_cadena_procesada(self, _sql):
        '''se obtiene la cadena procesada'''
        return self.db.get_vector(_sql.get_sql_iva_procesado())

    def get_resumen_periodos(self, _sql):
        '''resumen periodos'''
        return self.db.get_vector(_sql.get_sql_resumen_periodos())

    def get_resumen_liquidacion(self, _sql):
        ''' resumen de liquidacion'''
        return self.db.get_vector(_sql.get_sql_resumen_liquidacion())

    def get_resumen_analizados(self, _sql):
        '''resumen analizdos'''
        return self.db.get_vector(_sql.get_sql_resumen_analizados())

    def get_resumen_verificados(self, _sql):
        '''resumen verificados'''
        return self.db.get_vector(_sql.get_sql_resumen_verifica())

    def get_resumen_resultados(self, _sql):
        '''resumen resultados'''
        return self.db.get_vector(_sql.get_sql_resumen_resultados())

    def get_resumen_resultados_obs(self, _sql):
        '''resumen observaciones'''
        return self.db.get_scalar(_sql.get_sql_resumen_resultados_obs())
