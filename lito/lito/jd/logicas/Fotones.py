"""Fotones, desde Agosto 2023
Funcionalidades:
  - Sirve para realizar opereaciones de mantenimiento.

METODOS

 - fn(fusionar)                   Actualizaciones varias
 - fn(fisionar)                   Grabado del Caso
 - fn(vocado)                     DEvoluciones de volcados de DAtaframes

+---------------+-------------+-----------------------------------------------+
| Fecha         | Modifier    | Descripcion                                   |
+---------------+-------------+-----------------------------------------------+
| 11SEP2023     | jagonzaj    | Se crean los 3 metodos de                     |
|               |             |  mantenimiento del sistema                    |
+---------------+-------------+-----------------------------------------------+

ESTANDAR PEP8

"""

import pandas
from flask import session

from datos import Consultas, Cambios, Reportes
from logicas import Materiales


class Reemplazantes(Materiales.Universales):
    '''construccion del reporte'''

    def __init__(self, db):
        '''constructor inicial'''
        self.db = db
        self.cn = Consultas.Papel(db)

    def fusionar(self):
        '''fusionar'''
        res = 0
        _jd = self.db.uf.pi
        _jd.fecha_hoy = self.db.get_fecha_ymd()
        _his = self.db.uf.his
        _sql = Cambios.Afectacion(_jd)
        _sql.nav = self.db.uf.navegante
        match(int(self.db.uf.pi.expediente)):
            case 1:
                res = self.db.get_actualizar(_sql.upd_sql_diez_once())
                _his.monto_a_devolver_calculado = _sql.jd.el_once
                print(f"""Actualizado el monto a devolver a 
                          self.db.uf.his.monto_a_devolver_calculado
                          {_his.monto_a_devolver_calculado}  tramite  ->
                          {_sql.jd.tramite}""")
            case 10:
                res =\
                    self.db.get_actualizar(_sql.upd_sql_estadisticas_pre_informe())
                _sql_may = Reportes.Globales(_jd)
                self.guardar_mayoreo(_sql_may)
                _his.time_providencia = self.db.get_fecha_ymd_hms()

            case 1500 | 1600:
                res = 1
                _sql.jd.tramite = self.db.uf.pi.tramite
            case 9999:
                res = self.db.get_actualizar(_sql.upd_sql_tramite_aprobado())
            case 9998:
                res = self.db.get_actualizar(_sql.upd_sql_tramite_aprobado_3ra())
            case 9997:
                res = self.db.get_actualizar(_sql.upd_sql_tramite_devolver())

        retorno = {"valida": res}
        session.modified = True

        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd

        return retorno

    def fisionar(self):
        '''
            1: observaciones de la tabla
        '''
        res = 0
        _jd = self.db.uf.pi
        _jd.fecha_hoy = self.db.get_fecha_ymd()
        _his = self.db.uf.his
        _sql = Cambios.Afectacion(_jd)

        match(self.db.uf.pi.escena):
            case 'F':
                _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                _sql.jd.tabla_relacional = \
                    self.db.config.TB_PG_DEV_OBSERVACIONES
                _sql.jd.tabla_esquema = \
                    f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                observa = {"observaciones": [_sql.jd.observaciones],
                           "tipo": [1]}
                _sql.jd.df = pandas.DataFrame.from_dict(observa)
                res = self.guardar_warp_jd(_sql, cabecera=True)
                _sql.jd.df = ''

            case 'Z':
                num_acceso = -1
                if session.get('num_acceso') is not None:
                    num_acceso = int(session['num_acceso'])

                _his.time_graba_memoria = self.db.get_fecha_ymd_hms()
                _his.time_providencia = _his.time_inicia if _his.time_providencia == '' else _his.time_providencia
                _his.time_elige_declas_nc = self.db.uf.his.time_elige_declas_nc if _his.time_elige_declas_nc != '' else _his.time_inicia
                diccionario_venus = []
                _sql.jd.df = ''
                diccionario_venus.append(
                    {"usuario_id": 1, "ipv4": _sql.jd.ipv4,
                     "time_informe_revision": _sql.jd.time_informe_revision,
                     "num_retenciones_proce": _sql.jd.num_retenciones_proce,
                     "num_retenciones_dupli": _sql.jd.num_retenciones_dupli,
                     "num_retenciones_excel": _sql.jd.num_retenciones_excel,
                     "num_tramites_encontrados": _his.num_tramites_encontrados,
                     "num_tramites_objetivos": _his.num_tramites_objetivos,
                     "num_declaraciones_subjetivas": _his.num_declaraciones_subjetivas,
                     "num_decla_mensual_subjetivas": _his.num_decla_mensual_subjetivas,
                     "numeros_semestrales_subjetivas": _his.numeros_semestrales_subjetivas,
                     "num_terceros_subjetivos": _his.num_terceros_subjetivos,
                     "num_declas_objetivas_mensual": _his.num_declas_objetivas_mensual,
                     "num_declas_periodos_analizados": _his.num_declas_periodos_analizados,
                     "num_declaraciones_cumplen": _his.num_declaraciones_cumplen,
                     "num_declaraciones_no_cumplen": _his.num_declaraciones_no_cumplen,
                     "num_excel_filas": _his.num_excel_filas,
                     "num_excel_val_ret_blanks": _his.num_excel_val_ret_blanks,
                     "num_excel_val_ret_invalid": _his.num_excel_val_ret_invalid,
                     "monto_excel_identificado": _his.monto_excel_identificado,
                     "num_excel_fec_emi_invalid": _his.num_excel_fec_emi_invalid,
                     "num_excel_num_fails": _his.num_excel_num_fails,
                     "num_providencias": _his.num_providencias,
                     "time_procesa_excel": _his.time_procesa_excel,
                     "time_excel_a_db": _his.time_excel_a_db,
                     "time_procesa_cadena": _his.time_procesa_cadena,
                     "time_inicia": _his.time_inicia,
                     "time_elige_declas_nc": _his.time_elige_declas_nc,
                     "time_providencia": _his.time_providencia,
                     "time_graba_cadena": _his.time_graba_cadena,
                     "time_graba_memoria": _his.time_graba_memoria,
                     "num_fantasmas": _his.num_fantasmas,
                     "num_fallecidos": _his.num_fallecidos,
                     "num_ffpv": _his.num_ffpv,
                     "snt_fecha_ingreso": _his.snt_fecha_ingreso,
                     "fila": num_acceso,
                     "snt_monto_solicitado": _his.snt_monto_solicitado,
                     "snt_monto_a_devolver": _his.snt_monto_a_devolver,
                     "monto_a_devolver_calculado": _his.monto_a_devolver_calculado,
                     "num_descartados": _his.num_descartados
                     })
                df_venus = pandas.DataFrame(diccionario_venus)
                # A df_venus["estado"] = 'SAV'
                # PASO 0 ->  INA  El analista lo esta trabajando
                # PASO 1 ->  SAV   Guardado por el analista
                # PASO 2 ->  APR   Aprobado por su supervisor
                # PASO 3 ->  APR   Aprobado por su supervisor
                # PASO 4 ->  FIN   Analistat lo finaliza
                # PASO 5 ->  BOR   Analista/Supervisor lo borra
                # Analista
                # va a ver los en estado APR, FIN, INA
                # Supervisor
                # va a ver los en estado SAV, APR, FIN
                _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_PUBLIC
                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_MEMORIA_CASOS
                _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                _sql.jd.df = df_venus
                df_venus["estado"] = 'SAV'
                self.guardar_warp_jd(_sql, True, 'SAV')
                _sql.jd.df = ''
                res = 1
                venusino = self.db.get_scalar(_sql.get_sql_ultima_memoria_ingresado())
                _sql.jd.memoria = venusino
                print(f" {self.db.uf.CYAN}   RECORDING  {venusino} \n MEMORIA {_sql.jd.memoria} \n GRABADO \n {df_venus} {self.db.uf.RESET} ")
                self.db.uf.pi.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                for tabla in self.db.uf.tablas_temporales:
                    _sql.jd.tabla_relacional = tabla
                    _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                    self.db.get_actualizar(_sql.upd_sql_memoria_salvada())
                _sql.jd.df = ''
                self.db.uf.his = _his
                self.db.uf.pi = _sql.jd

        retorno = {"valida": res}
        return retorno

    def volcado(self, _sql):
        '''volcado'''
        resultado = {}
        match(int(_sql.jd.ufuf)):
            case 0:
                self.db.uf.pi.huesped = '1'
                df_ina = self.db.get_vector(_sql.get_sql_resumen_tramites())
                df_ina = df_ina.fillna(0)
                if not df_ina.empty:
                    df_ina["pre_enlace_excel"] = df_ina.apply(lambda fila: self.db.uf.fragmentar_varios(fila["contri"], fila["periodo_inicial"], fila["periodo_final"]), axis=1)
                    df_ina["id"] = df_ina["id"].astype(str)
                    df_ina["pre_enlace_excel"] = df_ina["pre_enlace_excel"] + '06' + df_ina["id"].str.zfill(10)
                    df_ina["enlace_excel"] = df_ina.apply(lambda x: f""" <a href="get_informe/{x["pre_enlace_excel"]}/19042008/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="uname.xlsx"
                                                          target="_blank" id='dev_caso_a_{x["id"]}' class="btn btn-soft-dark btn-border">
                                                          <img src="../static/images/exce.png" alt="" class="img-fluid d-block"></a> """, axis=1)
                _sql.jd.huesped = '2'
                df_apr = self.db.get_vector(_sql.get_sql_resumen_tramites())
                df_apr = df_apr.fillna(0)

                if not df_apr.empty:
                    df_apr["pre_enlace_excel"] = df_apr.apply(lambda fila: self.db.uf.fragmentar_varios(fila["contri"], fila["periodo_inicial"], fila["periodo_final"]), axis=1)
                    df_apr["id"] = df_apr["id"].astype(str)
                    df_apr["pre_enlace_excel"] = df_apr["pre_enlace_excel"] + '07' + df_apr["id"].str.zfill(10)
                    df_apr["enlace_excel"] = df_apr.apply(lambda x: f""" <a href="get_informe/{x["pre_enlace_excel"]}/19042008/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="uname.xlsx"
                                                          target="_blank" id='dev_caso_a_{x["id"]}' class="btn btn-soft-dark btn-border">
                                                          <img src="../static/images/exce.png" alt="" class="img-fluid d-block"></a> """, axis=1)

                _sql.jd.huesped = '3'
                df_tercera = self.db.get_vector(_sql.get_sql_resumen_tramites())
                df_tercera = df_tercera.fillna(0)
                if not df_tercera.empty:
                    df_tercera["pre_enlace_excel"] = df_tercera.apply(lambda fila: self.db.uf.fragmentar_varios(fila["contri"], fila["periodo_inicial"], fila["periodo_final"]), axis=1)
                    df_tercera["id"] = df_tercera["id"].astype(str)
                    df_tercera["pre_enlace_excel"] = df_tercera["pre_enlace_excel"] + '08' + df_tercera["id"].str.zfill(10)
                    df_tercera["enlace_excel"] = df_tercera.apply(lambda x: f""" <a href="get_informe/{x["pre_enlace_excel"]}/19042008/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="uname.xlsx"
                                                                  target="_blank" id='dev_caso_a_{x["id"]}' class="btn btn-soft-dark btn-border">
                                                                  <img src="../static/images/exce.png" alt="" class="img-fluid d-block"></a> """, axis=1)
                _sql.jd.huesped = '4'
                df_cuarta = self.db.get_vector(_sql.get_sql_resumen_tramites())
                df_cuarta = df_cuarta.fillna(0)
                if not df_cuarta.empty:
                    df_cuarta["pre_enlace_excel"] = df_cuarta.apply(lambda fila: self.db.uf.fragmentar_varios(fila["contri"], fila["periodo_inicial"], fila["periodo_final"]), axis=1)
                    df_cuarta["id"] = df_cuarta["id"].astype(str)
                    df_cuarta["pre_enlace_excel"] = df_cuarta["pre_enlace_excel"] + '09' + df_cuarta["id"].str.zfill(10)
                    df_cuarta["enlace_excel"] = df_cuarta.apply(lambda x: f""" <a href="get_informe/{x["pre_enlace_excel"]}/19042008/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="uname.xlsx"
                                                                target="_blank" id='dev_caso_a_{x["id"]}' class="btn btn-soft-dark btn-border">
                                                                <img src="../static/images/exce.png" alt="" class="img-fluid d-block"></a> """, axis=1)

                df_supervisores = self.db.get_vector(_sql.get_sql_supervisores())
                resultado = {"volca_ina":  df_ina.to_dict("records"),
                             "volca_apr":  df_apr.to_dict("records"),
                             "volca_tercera":  df_tercera.to_dict("records"),
                             "volca_cuarta":  df_cuarta.to_dict("records"),
                             "df_supervisores":  df_supervisores.to_dict("records")
                        }
            case -12:
                resultado = \
                    self.db.get_vector(_sql.get_sql_declaraciones_contri())
            case -13:
                resultado = self.db.get_vector(_sql.get_sql_futuras())
            case -14:
                # print(f"_sql.get_sql_cadena_iva_reporte_eq() {_sql.get_sql_cadena_iva_reporte_eq()}")
                resultado = \
                    self.db.get_vector(_sql.get_sql_cadena_iva_reporte_eq())
            case -17:
                resultado = \
                    self.db.get_vector(_sql.get_sql_listado_out_range())
            case -1:
                df_supervisores = \
                    self.db.get_vector(_sql.get_sql_supervisores())
                resultado = {"df_supervisores":
                             df_supervisores.to_dict("records")}
            case -81:
                resultado = {"res": -1}
            case _:
                _sql.jd.memoria = int(_sql.jd.ufuf)
                df_sin_grupos = \
                    self.db.get_vector(_sql.get_sql_resumen_tramites_grupo())
                resultado = {"df_sin_grupos":
                             df_sin_grupos.to_dict("records")}
        return resultado
