"""Declaraciones, desde Marzo 2023
-*- coding: utf-8 -*-
Funcionalidades:
  - Sirve para traer la informacion del contribuyente entre otras validaciones.

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+
Se obtiene sus declaraciones validas via automatico o proceso manual
COMPORTAMIENTO:

 - fn(procesar_camino_adq)      procesa camino aquisiciones en funcion
                                    de los adhesivos validos
 - fn(procesar_camino_ret)      procesa camino retenciones en funcion
                                    de los adhesivos validos
 - fn(identificar_camino)       se identifica el camino a seguir
 - fn(destino_123)              se aplican formulas a algunos casilleros
                                    de las declaraciones, para obtener las
                                    diferencias de adquisiciones y retenciones
                                    en los periodos elegidos
 - fn(get_bus_seleccionadas)    en funcion de las declaraciones validas
                                con los adhesivos y las celdas formuladas
                                se obtienen:
                                declaraciones-periodo (declas): precadena
                                con las declaraciones de cada pepriodo
                                donde se ppuede evidencias las diferencias
                                periodos:  los periodos que fueron analizados
                                enlace :  el rrespectivo reporte

+---------------+-------------------+----------------------------------------+
| Fecha         | Modifier          | Descripcion                            |
+---------------+-------------------+----------------------------------------+
| 01MAR2023     | jagonzaj          |   Se utilizan las formulas segun el    |
|               |                   |       papel de trabajo                 |
| 19JUN2024     | jagonzaj          |   En revision con J Estrella se hacen  |
|               |                   |       algunos ajustes a las formulas   |
+---------------+-------------------+----------------------------------------+

ESTANDAR PEP8
REVISADO CON SONARLINT 4.3.0 (Exluida la regla de longitud minima de lineas
en una funcion,
y la longitud de linea se trabaja con 240 caracteres)
"""

import pandas as pd
import random
import numpy as numerico

from datos import Consultas, RetencionesQ
from logicas import Materiales
from datos.cortas import a_tres, nub, val_en, a_dos


class Transpuesta(Materiales.Universales):
    '''revision de las declaraciones'''

    def __init__(self, db):
        '''constructor inicial'''
        self.db = db
        self.cn = Consultas.Papel(db)

    def procesar_camino_adq(self, camino, X) -> float:
        '''procesar adquisiciones'''
        valor_ct = 9999
        match camino:
            case '1': valor_ct = a_tres(self.db.uf.fx(X.get("18")) - self.db.uf.fx(X.get("22")))
            case '2': valor_ct = a_tres(self.db.uf.fx(X.get("18")))
            case '3':
                if a_dos(self.db.uf.fx(X.get("18")) - self.db.uf.fx(X.get("22"))) < 0.00:
                    valor_ct = a_dos(self.db.uf.fx(X.get("18")) - self.db.uf.fx(X.get("22")))
                else:
                    valor_ct = 9999

            case '':
                valor_ct = a_dos(self.db.uf.fx(X.get("18")) + self.db.uf.fx(X.get("23")))

            case '-1':
                if a_dos(self.db.uf.fx(X.get("18")) + self.db.uf.fx(X.get("23"))) == 0.00:
                    valor_ct = 0.00
                elif self.db.uf.fx(X.get("22")) > self.db.uf.fx(X.get("18")):
                    if self.db.uf.fx(X.get("25")) == 0:
                        valor_ct = 0.00
                    else:
                        valor_ct = a_dos(self.db.uf.fx(X.get("18")) + self.db.uf.fx(X.get("23")))
                else:
                    valor_ct = a_dos(self.db.uf.fx(X.get("18")) - self.db.uf.fx(X.get("22")))

            case '4':   valor_ct = 0.00
            case _: valor_ct = 9999

        return valor_ct

    def procesar_camino_ret(self, camino, X) -> float:
        '''procesar retenciones'''
        valor_ct = 9999

        match camino:
            case '1': valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("24")), 2)
            case '2': valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("24")) - self.db.uf.fx(X.get("22")), 2)
            case '3': valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("18")) + self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("24")) - self.db.uf.fx(X.get("22")), 2)
            case '': valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("24")), 2)

            case '-1':
                if self.db.uf.fx(X.get("18")) > 0 and self.db.uf.fx(X.get("25")) == 0.00:
                    valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("18")) + self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("25")) + self.db.uf.fx(X.get("24")) - self.db.uf.fx(X.get("22")), 2)
                elif self.db.uf.fx(X.get("18")) <= 0 and self.db.uf.fx(X.get("25")) == 0.00:
                    valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("24")) - self.db.uf.fx(X.get("22")), 2)
                else:
                    valor_ct = self.db.uf.redondear(self.db.uf.fx(X.get("19")) + self.db.uf.fx(X.get("24")), 2)
            case '4':   valor_ct = 0
            case _: valor_ct = 9999

        return valor_ct

    def identificar_camino(self, X, diferencia_arr_ct, diferencia_x_ct, diferencia_adquisiciones,  diferencia_retenciones):
        '''se identifica el camino a seguir'''
        resultado_camino = ''
        el_18 = self.db.uf.redondear(self.db.uf.fx(X.get("18")) + abs(diferencia_arr_ct), 2)
        el_19 = self.db.uf.redondear(self.db.uf.fx(X.get("19")) + abs(diferencia_x_ct), 2)
        el_25 = self.db.uf.redondear(self.db.uf.fx(X.get("25")) - (diferencia_adquisiciones), 2)
        el_26 = self.db.uf.redondear(self.db.uf.fx(X.get("26")) - (diferencia_retenciones), 2)

        if self.db.uf.fx(X.get("22")) > 0:
            if el_18 > 0:
                if a_dos((el_18 - self.db.uf.fx(X.get("22")))) == el_25:
                    resultado_camino = '1'
                else:
                    if self.db.uf.redondear(el_19 + self.db.uf.fx(X.get("24")) - self.db.uf.fx(X.get("22")), 2) == el_26:
                        resultado_camino = '2'
                    else:
                        if self.db.uf.redondear(el_18 + el_19 + self.db.uf.fx(X.get("24")), 2) > self.db.uf.fx(X.get("22")):
                            if self.db.uf.redondear((el_18 + el_19 + self.db.uf.fx(X.get("24")) - self.db.uf.fx(X.get("22"))), 2) == el_26:
                                resultado_camino = '3'
                            else:
                                if self.db.uf.redondear(el_18 + el_19 + self.db.uf.fx(X.get("24")), 2) < self.db.uf.fx(X.get("22")):
                                    resultado_camino = '4'
                                else:
                                    resultado_camino = '-1'
                        else:
                            resultado_camino = '4'
            else:
                if self.db.uf.redondear(self.db.uf.fx(X.get("19"))+self.db.uf.fx(X.get("24")), 2) > 0:
                    if self.db.uf.redondear((el_19 + self.db.uf.fx(X.get("24"))-self.db.uf.fx(X.get("22"))), 2) == el_26:
                        resultado_camino = '2'
                    else:
                        if self.db.uf.redondear(el_18 + el_19 + self.db.uf.fx(X.get("24")), 2) < self.db.uf.fx(X.get("22")):
                            resultado_camino = '4'
                        else:
                            resultado_camino = '-1'
                else:
                    resultado_camino = '4'
        else:
            resultado_camino = ''

        return resultado_camino

    def destino_123(self, df):
        '''ubicando caminos'''
        resultado_camino = ''
        lista_caminos = []
        lis_diferencia_arr_ct = []
        lis_diferencia_x_ct = []
        lis_diferencia_adquisiciones = []
        lis_diferencia_retenciones = []
        Y = {}
        k = 0
        list_cal_adq = []
        list_cal_ret = []
        diferencia_arr_ct = 0
        diferencia_x_ct = 0
        col_anterior = ''
        val_ant_a = 0
        val_ant_b = 0
        val_ant_c = 0
        val_ant_d = 0
        for (columna, celdavalor) in df.items():
            totalizado = []
            lista = celdavalor.values
            ix = 0
            df.at["diferencia_arr_ct", columna] = 0
            df.at["diferencia_x_ct", columna] = 0
            X = {"0": "CAMINO"}
            for elemento in lista:
                if ix > 5:
                    X[f"{ix+8}"] = \
                        str(elemento).replace("$", "").replace(",", "")
                    variante = str(elemento)
                    if variante.find("$") >= 0:
                        variante = variante.replace("$", "").replace(",", "")
                    totalizado.append(self.db.uf.fx(variante))
                ix += 1
            if k == 0:
                df.at["diferencia_arr_ct", columna] = 0
                df.at["diferencia_x_ct", columna] = 0
                lis_diferencia_arr_ct.append(0)
                lis_diferencia_x_ct.append(0)
                # 1 Y = X
            else:
                diferencia_arr_ct = a_dos(self.db.uf.fx(X.get("14")) - self.db.uf.fx(Y.get("25")))
                diferencia_x_ct = a_dos(self.db.uf.fx(X.get("15")) - self.db.uf.fx(Y.get("26")))
                if abs(diferencia_arr_ct) == abs(val_ant_a) and abs(val_ant_a) > 0:
                    diferencia_arr_ct = 0
                    df.at["diferencia_arr_ct", col_anterior] = 0.00
                if abs(diferencia_x_ct) == abs(val_ant_b) and \
                        abs(val_ant_b) > 0:
                    diferencia_x_ct = 0
                    df.at["diferencia_x_ct", col_anterior] = 0.00
                df.at["diferencia_arr_ct", columna] = diferencia_arr_ct
                df.at["diferencia_x_ct", columna] = diferencia_x_ct
                lis_diferencia_arr_ct.append(diferencia_arr_ct)
                lis_diferencia_x_ct.append(diferencia_x_ct)
                val_ant_a = diferencia_arr_ct
                val_ant_b = diferencia_x_ct
                #  END DIFF A_B
            Y = X
            k += 1
            resultado_camino = self.identificar_camino(X, 0, 0, 0, 0)
            diferencia_adquisiciones = 0
            calcular_ct_adq = self.procesar_camino_adq(resultado_camino, X)
            if calcular_ct_adq <= 0:
                if self.db.uf.fx(X.get("25")) == 0.0:
                    diferencia_adquisiciones = 0.0
                else:
                    diferencia_adquisiciones = \
                        a_dos(self.db.uf.fx(X.get("25")))
            elif self.db.uf.fx(X.get("25")) != calcular_ct_adq:
                diferencia_adquisiciones = \
                    a_dos((self.db.uf.fx(X.get("25")) - calcular_ct_adq))
            calcular_ct_ret = self.procesar_camino_ret(resultado_camino, X)
            df.at["calculo_ct_adq", columna] = calcular_ct_adq
            df.at["calculo_ct_ret", columna] = calcular_ct_ret
            if abs(diferencia_adquisiciones) == abs(val_ant_c) and \
                    abs(val_ant_c) > 0:
                diferencia_adquisiciones = 0
                df.at["diferencia_adquisiciones", col_anterior] = 0.00
            df.at["diferencia_adquisiciones", columna] = \
                a_dos(diferencia_adquisiciones)
            diferencia_retenciones = \
                a_dos(self.db.uf.fx(X.get("26")) - calcular_ct_ret)
            if abs(diferencia_retenciones) == abs(val_ant_d) and \
                    abs(val_ant_d) > 0:
                diferencia_retenciones = 0
                df.at["diferencia_retenciones", col_anterior] = 0.00
            df.at["diferencia_retenciones", columna] = diferencia_retenciones
            ix += 1
            val_ant_c = diferencia_adquisiciones
            val_ant_d = diferencia_retenciones
            if resultado_camino == '-1':
                resultado_camino = \
                    self.identificar_camino(X,
                                            diferencia_arr_ct,
                                            diferencia_x_ct,
                                            a_dos(diferencia_adquisiciones),
                                            diferencia_retenciones)
            lista_caminos.append(resultado_camino)
            df.at["camino", columna] = resultado_camino
            lis_diferencia_adquisiciones.append(a_dos(diferencia_adquisiciones))
            lis_diferencia_retenciones.append(a_dos(self.db.uf.fx(X.get("26")) - calcular_ct_ret))

            list_cal_adq.append(a_dos(calcular_ct_adq))
            list_cal_ret.append(a_dos(calcular_ct_ret))
            col_anterior = columna

        return df, lista_caminos, lis_diferencia_adquisiciones, lis_diferencia_retenciones, lis_diferencia_arr_ct, lis_diferencia_x_ct, list_cal_adq, list_cal_ret

    def get_bus_seleccionadas(self):
        '''    #declaraciones seleccionadas para presentacion vertical,
                hoja analisis'''
        _his = self.db.uf.his
        _jd = self.db.uf.pi
        _sql = RetencionesQ.Declaraciones(_jd)
        _sql.jd.fecha_hoy = self.db.get_fecha_ymd()
        df_declas = []
        _his.time_elige_declas_nc = _sql.jd.fecha_hoy
        consulta = _sql.get_sql_declaracion_transpuesta()
        df = self.db.get_vector(consulta)
        _his.num_declas_objetivas_mensual = len(df.index)
        df.sort_values(by=['anio_fiscal', 'mes_fiscal'],
                       ascending=True,
                       inplace=True,
                       ignore_index=True)
        df.index.rename('variable', inplace=True)
        df2 = df.copy()
        hay_semestrales = self.db.get_scalar(_sql.we_have_semestrales())
        if hay_semestrales == 0:
            _his.frecuenciamiento = "MENSUAL"
        else:
            _his.frecuenciamiento = "SEMESTRAL"
        df2["contri"] = _sql.jd.contri
        df2["fecha_analisis"] = _sql.jd.fecha_hoy
        numero_veces = self.db.get_scalar(_sql.num_declas_validas())
        if numero_veces > 0:
            self.db.get_actualizar(_sql.reset_declas_validas())
        formato_decimal = "${:,.2f}"
        df2["fecha_analisis"] = pd.to_datetime(df2["fecha_analisis"])
        df["sct_adquisicion_mesanterior"] = df["sct_adquisicion_mesanterior"].map(formato_decimal.format)
        df["sct_retenciones_mesanterior"] = df["sct_retenciones_mesanterior"].map(formato_decimal.format)
        df["ajuste_x_adquisiciones"] = df["ajuste_x_adquisiciones"].map(formato_decimal.format)
        df["ajuste_x_retenciones"] = df["ajuste_x_retenciones"].map(formato_decimal.format)
        df["sct_mes_anterior"] = df["sct_mes_anterior"].map(formato_decimal.format)
        df["sct_mesanterior_retenciones"] = df["sct_mesanterior_retenciones"].map(formato_decimal.format)
        df["total_impuestos_mes_actual"] = df["total_impuestos_mes_actual"].map(formato_decimal.format)
        df["ct_factor_proporcionalidad"] = df["ct_factor_proporcionalidad"].map(formato_decimal.format)
        df["impuesto_causado"] = df["impuesto_causado"].map(formato_decimal.format)
        df["ct_mes_actual"] = df["ct_mes_actual"].map(formato_decimal.format)
        df["sct_x_adquisiciones"] = df["sct_x_adquisiciones"].map(formato_decimal.format)
        df["sct_x_retenciones"] = df["sct_x_retenciones"].map(formato_decimal.format)
        df["tot_impuesto_pagar_x_percepcion"] = df["tot_impuesto_pagar_x_percepcion"].map(formato_decimal.format)
        df["saldo_crt_clo_ipr_msi_2220"] = df["saldo_crt_clo_ipr_msi_2220"].map(formato_decimal.format)
        df["total_pagado"] = df["total_pagado"].map(formato_decimal.format)
        df["total_impuesto_a_pagar_2610"] = df["total_impuesto_a_pagar_2610"].map(formato_decimal.format)
        df_periodos_analisis = df[["anio_fiscal", "mes_fiscal", "numero_adhesivo","retenciones_fuente_iva"]]
        df['retenciones_fuente_iva'] = df_periodos_analisis["retenciones_fuente_iva"].map(formato_decimal.format)
        df_periodos_analisis = df_periodos_analisis.drop_duplicates()
        df1 = df.T
        df1["descripcion"] = df1.index
        df1, lista_caminos, lis_diferencia_adquisiciones, \
            lis_diferencia_retenciones, lis_diferencia_arr_ct, \
            lis_diferencia_x_ct, list_cal_adq, \
            list_cal_ret = self.destino_123(df1)
        lista_caminos = lista_caminos[:-1]
        lis_diferencia_adquisiciones = lis_diferencia_adquisiciones[:-1]
        lis_diferencia_retenciones = lis_diferencia_retenciones[:-1]
        lis_diferencia_arr_ct = lis_diferencia_arr_ct[:-1]
        lis_diferencia_x_ct = lis_diferencia_x_ct[:-1]
        list_cal_adq = list_cal_adq[:-1]
        list_cal_ret = list_cal_ret[:-1]

        df2["camino"] = lista_caminos
        df2["diferencia_arr_ct"] = lis_diferencia_arr_ct
        df2["diferencia_x_ct"] = lis_diferencia_x_ct
        df2["diferencia_adquisiciones"] = lis_diferencia_adquisiciones
        df2["diferencia_retenciones"] = lis_diferencia_retenciones
        df2["calculo_ct_adq"] = list_cal_adq
        df2["calculo_ct_ret"] = list_cal_ret

        df_cum = df2.copy()
        df_cum_todas = \
            df_cum.loc[:,
                       ~df_cum.columns.isin(['diferencia_arr_ct',
                                             'diferencia_x_ct',
                                             'diferencia_adquisiciones',
                                             'diferencia_retenciones',
                                             'totales', 'contri',
                                             'fecha_analisis',
                                             'calculo_ct_adq',
                                             'calculo_ct_ret'])]

        df_cum_todas["ciclo"] =\
            numerico.where(df_cum_todas["mes_fiscal"].astype(int) < 7, 1, 2)

        df_cum_todas = self.set_periocidad(df_cum_todas)
        df_cum_todas = self.borrar_columnas(df_cum_todas,
                                            ['variable', 'camino'])

        _sql.jd.df = df_cum_todas
        _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
        _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_PRE_ANALISIS_PREVIO
        self.guardar_warp_jd(_sql, cabecera=True)
        _sql.jd.df = ''

        _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
        _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_CAD_IVA_PROCESA
        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        self.db.get_reseto_tabla_estandar_jd(_sql)
        _sql.jd.tabla_relacional = \
            self.db.config.TB_PG_DEV_RESULTADO_ANALISIS_RETENCION

        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        self.db.get_reseto_tabla_estandar_jd(_sql)
        _sql.jd.tabla_relacional = \
            self.db.config.TB_PG_DEV_DECLARACIONES_VALIDAS
        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        _sql.jd.df = df2
        self.guardar_warp_jd(_sql, True)
        _sql.jd.df = ''

        df1 = df1.reset_index()
        df1 = df1.round(2)
        df1.columns = [f"fx_{i+1}" for i in range(df1.shape[1])]
        df_declas = df1.to_dict('records')
        df_periodos = df_periodos_analisis.to_dict('records')
        _his.num_declas_periodos_analizados = len(df_periodos_analisis.index)

        fecha = self.db.get_fecha_ymd()
        nombre = f"{_sql.jd.contri}_{fecha}_"
        fragmentado = self.db.uf.fragmentar()
        placebo = str(int(random.uniform(15 << 2, 100000))).zfill(10)
        seccion = fragmentado, placebo, nombre
        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd
        if _sql.jd.tramite == '':
            _sql.jd.tramite = '19042008'

        enlace = f""" <a href="get_informe/{seccion[0]}16{seccion[1]}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="{seccion[2]}_ANALISIS.xlsx"
                        target="_blank" id='dev_a_cadena_f1' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Analisis Cadena</a> """

        if _sql.jd.tramite == '19042008':
            _sql.jd.tramite = ''

        resultado = {
            "declas": df_declas,
            "nfilas":  len(df1.columns)-1,
            "periodos": df_periodos,
            "enlace_cad_f1": enlace

        }
        return resultado
