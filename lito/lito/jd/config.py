r"""Configuracion, desde Enero 2023
Funcionalidades:
  - Sirve para administrar los parametrros globales para la applicacion.

Contiene propiedades unicamente
+-------------------+-------------------+------------------------------------+
| Fecha             | Modifier          | Descripcion                        |
+-------------------+-------------------+------------------------------------+
| 15DIC2022         | jagonzaj          |   se incluyen nparametros segun    |
|                   |                   |    demanda                         |
+-------------------+-------------------+------------------------------------+

ESTANDAR PEP8

"""

import os
import json
import logging
import sys
import toml


file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


class JSONLogFormatter(logging.Formatter):
    '''Formateo JSON '''

    def format(self, record):
        log_data = {
            'date': self.formatTime(record, self.datefmt),
            'levelname': record.levelname,
            'message': record.getMessage(),
            'pathname': record.pathname,
            'line': record.lineno
        }
        return json.dumps(log_data)


class Config:
    '''PARAMETROS DE CONIGURACION'''
    tom_quien = "c.toml"
    dimesion = toml.load(file_dir + "/" + f'{tom_quien}')
    DB_DEV_HOST = dimesion.get('database').get('host')
    DB_DEV_DB = dimesion.get('database').get('name')
    DB_DEV_USER = dimesion.get('database').get('usuario')
    DB_DEV_PASS = dimesion.get('database').get('password')
    SECRET_KEY = dimesion.get('configuracion').get('secret_key')
    ALGORITM = dimesion.get('configuracion').get('algorithm')
    COOKIE_SESSION_ID_KEY = dimesion.get('configuracion').get('galleta')
    SQLALCHEMY_DATABASE_URI =\
        dimesion.get('database').get('sqlalchemy_database_uri')
    SQLALCHEMY_TRACK_MODIFICATIONS =\
        False if int(dimesion.get('database').get(
            'sqlalchemy_track_modifications')) == 0 else True
    UPLOAD_FOLDER = dimesion.get('configuracion').get('upload_folder')
    ARCHIVO_RETENCION_COLS = dimesion.get('configuracion').get('columnas')
    NUM_COLUMNAS_ARCHIVO_RETENCION = dimesion.get(
        'configuracion').get('num_columnas')
    EXTENSIONES_ALLOW = dimesion.get('configuracion').get('extensiones')
    TAMANHIO_PAGINA = dimesion.get('configuracion').get('paginacion')
    UPLOAD_FOLDER_XLSX = dimesion.get(
        'configuracion').get('upload_folder_xlsx')
    CAMPO_DE_VISION = dimesion.get('configuracion').get('campo_vision')

    DATE_TIME_64 = dimesion.get('configuracion').get('datetime64')
    FORMATO_YMD_HMS = dimesion.get('configuracion').get('formato_Ymd_HMS')

    CAMPOS_DECLARACION_ORIGEN = dimesion.get(
        'configuracion').get('campos_declaraciones_origen')
    CAMPOS_DECLARACION_ORIGEN_RED = dimesion.get(
        'configuracion').get('campos_declaraciones_origen_red')

    CAMPOS_LIQUIDACION = dimesion.get(
        'configuracion').get('cammpos_liquidacion')

    # TABLAS
    TB_PG_ESQUEMA_TEMPORAL = dimesion.get('tablas_pg').get('esquema_temporal')
    TB_PG_ESQUEMA_PUBLIC = dimesion.get('tablas_pg').get('esquema_public')

    # CONTRI CATASTRO PY
    TB_PG_DEV_ESTADISTICA_BASE = dimesion.get(
        'tablas_pg').get('tabla_dev_estadistica_base')
    TB_PG_DEV_TRAMITES_CONS = dimesion.get(
        'tablas_pg').get('tabla_dev_tramites_cons')
    TB_PG_DEV_RUC_CONSULTADOS = dimesion.get(
        'tablas_pg').get('tabla_dev_ruc_consultados')

    # LISTADO PY
    TB_PG_DEV_DECLARACIONES_VALIDAS = dimesion.get(
        'tablas_pg').get('tabla_dev_declaraciones_validas')
    TB_PG_DEV_CARGAS_ARCHIVOS = dimesion.get(
        'tablas_pg').get('tabla_dev_cargas_archivos')
    TB_PG_DEV_CARGAS_ARCHIVOS_NV = dimesion.get(
        'tablas_pg').get('tabla_dev_cargas_archivos_nv')

    # CADENA PY
    TB_PG_DEV_RESUMEN_PERIODO = dimesion.get(
        'tablas_pg').get('tabla_dev_resumen_periodo')
    TB_PG_DEV_CAD_IVA_PROCESA = dimesion.get(
        'tablas_pg').get('tabla_dev_cad_iva_procesa')
    TB_PG_DEV_CUADRO_LIQUIDACION = dimesion.get(
        'tablas_pg').get('tabla_dev_cuadro_liquidacion')
    TB_PG_DEV_RESUMEN_ANALIZADOS = dimesion.get(
        'tablas_pg').get('tabla_dev_resumen_analizados')
    TB_PG_DEV_RESUMEN_VERIFICA = dimesion.get(
        'tablas_pg').get('tabla_dev_resumen_verifica')
    TB_PG_DEV_RESUMEN_RESULTADOS = dimesion.get(
        'tablas_pg').get('tabla_dev_resumen_resultados')
    TB_PG_DEV_PRE_CADENA_IVA = dimesion.get(
        'tablas_pg').get('tabla_dev_pre_cadena_iva')
    TB_PG_DEV_PRE_ANALISIS_PREVIO = dimesion.get(
        'tablas_pg').get('tabla_dev_analisis_previo')

    # DECLARACIONES PY
    TB_PG_DEV_RESULTADO_ANALISIS_RETENCION = dimesion.get(
        'tablas_pg').get('tabla_dev_resultado_analisis_retencion')

    # INFORME PY
    TB_PG_DEV_RESUMEN_CADENA = dimesion.get(
        'tablas_pg').get('tabla_dev_resumen_cadena')
    TB_PG_DEV_INFORME_RETENCION = dimesion.get(
        'tablas_pg').get('tabla_dev_informe_retencion')

    TB_PG_DEV_PROVIDENCIAS_VALS = dimesion.get(
        'tablas_pg').get('tabla_dev_providencias_vals')

    # FUTURO PY
    TB_PG_DEV_COMPENSA_FUTURO = dimesion.get(
        'tablas_pg').get('tabla_dev_compensa_futuro')

    # FOTONES PY
    TB_PG_DEV_OBSERVACIONES = dimesion.get(
        'tablas_pg').get('tabla_dev_observaciones')
    TB_PG_DEV_MEMORIA_CASOS = dimesion.get(
        'tablas_pg').get('tabla_dev_memoria_casos')

    maquina_roja = True
    server_win64_RAM = False
    maquina_black = False

    SERVER_ONLINE = 'SIN DEFINIR'
    if maquina_roja:
        SERVER_ONLINE = dimesion.get('configuracion').get('maquina_roja')
    if server_win64_RAM:
        SERVER_ONLINE = dimesion.get('configuracion').get('server_win64_RAM')
    if maquina_black:
        SERVER_ONLINE = dimesion.get('configuracion').get('maquina_black')
