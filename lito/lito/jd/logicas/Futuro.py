"""Compensación a Futuro, desde Mayo 2023
Funcionalidades:
  - Sirve para compensar a futuro siempre y cuando existan un n>0 de
    declaraciones entre el periodo final y mes actual.

El contri  110XXXXXXXXXX001 solicita devoluciones de retenciones de IVA
para el periodo
2022-01-01              2022-12-31

    Para este ejemplo se toma como fecha actual Enero 2024

    Se arman periodos  a compensar-futuro desde
                Enero 2023      a       Diciembre 2023


 - fn(destino_futura)                   Realiza las cadenas futuras para
                                        compensar según formular provistas
                                        desde Junio 2023
 - fn(actualizar_futuro_horizontal)     Guarda la tabla d resultados
                                         en pantalla
 - fn(get_bus_seleccionadas_futuras)    administra y actualiza los valores de
                                        cada celda segun donde se
                                        realice el cambio,
                                        actualizando los valores


+-------------+----------+----------------------------------------------------+
| Fecha       | Modifier |     Descripcion                                    |
+-------------+----------+--------------+-------------------------------------+
| 23ENE2023   | jagonzaj | Se cambia la forma de consulta                     |
|             |          | de que si existe la tabla                          |
|             |          | futura-pasada agregando el usuario                 |
|             |          | periodo                                            |
+-------------+----------+----------------------------------------------------+

ESTANDAR PEP8
"""

import pandas
import random

from datos import Consultas, RetencionesQ
from logicas import Materiales


class Pasado(Materiales.Universales):
    """Caracteristicas Futuras version 1.0.2
    -------------
    - Incluir criterio de la zonal 6        Octubre 2024
    - incluir en reporte general, 50% desarrollo no se incluye por otros
        desarrollos en curso, Abril 2024
    """
    __version__ = "1.0.1"

    def __init__(self, db):
        '''constructor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)
        self.df = pandas.DataFrame()
        self.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
        self.dimension_futura = self.db.config.TB_PG_DEV_COMPENSA_FUTURO

    def destino_futura(self, df, suma_saldos,  l5):
        '''destino futura'''
        cabecera = True
        anterior = float(suma_saldos)
        columna = 1
        for (columna, celdavalor) in df.items():
            lista = celdavalor.values
            ix = 0
            x = {"0": "CAMINO"}
            for elemento in lista:
                x[f"{ix}"] = str(elemento).replace("$", "").replace(",", "")
                ix += 1
            if cabecera:
                if float(anterior) == -1.00:
                    anterior = float(df.at["saldo_cred_resulta_next_mes", columna])

                if float(l5) != -1.00 and int(self.db.uf.pi.grabar) == 10:
                    df.at["sct_credito_mes_anterior_rca_adq_ret", columna] = float(l5)
                anterior = anterior + 0
            else:
                df.at["sct_credito_mes_anterior_rca_adq_ret", columna] = anterior

            df.at["saldo_de_ct_mes_anterior", columna] = self.db.uf.redondear(df.at["sct_credito_mes_anterior_rca_adq_ret", columna] - self.db.uf.fx(x.get("7")), 2)

            if df.at["saldo_de_ct_mes_anterior", columna] + self.db.uf.fx(x.get("10")) + self.db.uf.fx(x.get("11")) + self.db.uf.fx(x.get("12")) + self.db.uf.fx(x.get("13")) > self.db.uf.fx(x.get("9")):
                pre_dic = df.at["saldo_de_ct_mes_anterior", columna] + self.db.uf.fx(x.get("10")) + self.db.uf.fx(x.get("11"))
                pre_dic += self.db.uf.fx(x.get("12")) + self.db.uf.fx(x.get("13")) - self.db.uf.fx(x.get("9"))
                df.at["saldo_cred_resulta_next_mes", columna] = self.db.uf.redondear(pre_dic, 2)
            else:
                df.at["saldo_cred_resulta_next_mes", columna] = 0.00

            if df.at["saldo_de_ct_mes_anterior", columna] + self.db.uf.fx(x.get("10")) + self.db.uf.fx(x.get("11")) + self.db.uf.fx(x.get("12")) + self.db.uf.fx(x.get("13")) > self.db.uf.fx(x.get("9")):
                df.at["impuesto_pagar_resulta_mes", columna] = 0.00
            else:
                pre_dic = self.db.uf.fx(x.get("9")) - df.at["saldo_de_ct_mes_anterior", columna]
                pre_dic += -self.db.uf.fx(x.get("10")) - self.db.uf.fx(x.get("11")) - self.db.uf.fx(x.get("12")) - self.db.uf.fx(x.get("13"))
                df.at["impuesto_pagar_resulta_mes", columna] = self.db.uf.redondear(pre_dic, 2)

            anterior = df.at["saldo_cred_resulta_next_mes", columna]
            cabecera = False
            columna += 1
        return df

    def actualizar_futuro_horizontal(self, _sql):
        '''actualizar futuro horizontal'''
        vacio = 0
        _sql.jd.esquema = self.esquema
        _sql.jd.tabla_relacional = self.dimension_futura
        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        if not self.df.empty:
            df_grabar = self.df.copy()
            _sql.jd.df = df_grabar
            self.guardar_warp_jd(_sql, True)
            _sql.jd.df = ''
        else:
            vacio = 1
        return vacio

    def get_bus_seleccionadas_futuras(self):
        """ FUNCIONALIDAD:      Administra las fuunciones de esta clase, su
                idea se proveer la grid de compensación a futuro si hay
                declaraciones futuras para el periodo
                solicitado pero seran pasadas para la fecha actual
                indiferente de la epoca.
                También si se indica puede grabar un valor para un período,
                lo cual cambia la grid la misma que será redibujada.
            PARAMETROS :
            self(compensa)                          :   Trae el valor y periodo
                                                        a modificar
            self(grabar)                            :   Indica si se debe
                                                        grabar algún valor o es
                                                        el estado inicial de
                                                        carga de la tabla.
            GENERA:

            df_declas                           :   DataFrame con el cuadro de
                                                    declaraciones futuras
                                                    a pintar en el
                                                    interfaz gráfica
            suma_impuesto_pagar                 :   Sirve para actualizar el
                                                    cuadro de verificaciones
                                                    hacia atrás
            valor_declarado_ultimo_mes_xct_riva :   valor declarado del ultimo
                                                    mes en el periodo pedido
                                                    que es el pasado, no es el
                                                    periodo futuro que aqui
                                                    se calcula
            vacio                               :   Sirve para ocultar la grid
                                                    de compensacion a futuro en
                                                    el caso de
                                                    El periodo a realizar la
                                                    cadena llegue al mes actual
                                                    o luego del periodo
                                                    solicitado el contribuyente
                                                    no tenga declaraciones
                                                    realizadas
            enlace_futuro                       :   es el link de descarga del
                                                    reporte
            nfilas_futuras                      :   numero de ilas de la grid

            EXCEPCIONES:
            implementacion pendiente, si no hay datos no se realiza el proceso
        """

        _jd = self.db.uf.pi
        _jd.fecha_hoy = self.db.get_fecha_ymd()
        _his = self.db.uf.his
        _sql = RetencionesQ.MuyFuturas(_jd)

        vacio = 0
        divisores_l4 = _sql.jd.compensa.split('_')
        grabado_futuro = int(_sql.jd.grabar)
        numero_veces = self.db.get_scalar(_sql.get_sql_futuros_conteo())
        if numero_veces == 0 or grabado_futuro == 10:
            consulta = _sql.get_sql_declaracion_transpuesta_futura()
            df = self.db.get_vector(consulta)
            _sql.jd.df = df
            self.actualizar_futuro_horizontal(_sql)
            _sql.jd.df = ''
        else:
            df = self.db.get_vector(_sql.get_sql_declaracion_transpuesta_futura_diaria())
            if len(divisores_l4) == 2 and not df.empty:
                for ix, fila in df.iterrows():
                    adhesivo = fila["numero_adhesivo"]
                    if ix == int(divisores_l4[1])-2:
                        consulta = self.cn.get_upd_divisores_futuros(divisores_l4[0], adhesivo, _sql.jd.contri)
                        self.db.get_actualizar(consulta)
                df = self.db.get_vector(_sql.get_sql_declaracion_transpuesta_futura_diaria())

            if df.empty:
                vacio = 1

        valor_declarado_ultimo_mes_xct_riva = self.db.get_scalar(_sql.get_ultimo_diez())
        df1 = df.T
        df1 = self.destino_futura(df1, _sql.jd.suma_arrastre, _sql.jd.suma_analisis)
        df1_copia = df1.copy()
        df1_re = df1_copia.T
        self.df = df1_re
        vacio = self.actualizar_futuro_horizontal(_sql)

        df1_re["impuesto_pagar_resulta_mes"] = df1_re["impuesto_pagar_resulta_mes"].astype('Float64')
        df1_re["impuesto_pagar_resulta_mes"] = df1_re["impuesto_pagar_resulta_mes"].round(2)
        suma_impuesto_pagar = df1_re["impuesto_pagar_resulta_mes"].sum()
        df1 = df1.reset_index()
        df1.columns = [f"fx_{i+1}" for i in range(df1.shape[1])]
        df1 = df1.fillna(0)
        df_declas = df1.to_dict('records')
        _his.num_futuras = len(df1.columns) - 1
        fecha = self.db.get_fecha_ymd()
        nombre = f"{_sql.jd.contri}_{fecha}"
        fragmentado = self.db.uf.fragmentar()
        placebo = str(int(random.uniform(15 << 2, 100000))).zfill(10)
        seccion = fragmentado, placebo, nombre
        pre_dic = f""" <a href="get_informe/{seccion[0]}15{seccion[1]}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="{seccion[2]}_FUTURA.xlsx"   """
        pre_dic += """ target="_blank" id='dev_a_futuro' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Comp. Futura</a> """
        enlace = pre_dic
        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd
        resultado = {
            "declas_futura": df_declas,
            "nfilas_futuras": len(df1.columns) - 1,
            "suma_impuesto_pagar": suma_impuesto_pagar,
            "valor_Declarado_ultimo_mes_xct_riva": valor_declarado_ultimo_mes_xct_riva,
            "vacio": vacio,
            "enlace_futuro": enlace,
            "valida": 1
        }
        return resultado
