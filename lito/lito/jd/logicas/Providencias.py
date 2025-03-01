"""Providencias, desde Mayo 2023
Funcionalidades:
  - Sirve para trabajar con las retenciones que no cruzan,
  ayudando a mostrar en pantallas como providencias.

  son las que se pintan en rojo
El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

COMPORTAMIENTO:

 - fn(tratar_providencias)             tramites Previos del contri
                                       en cadenas de iva
 - fn(get_providencias_revisadas)      devuelve una trama json con la
                                       informacion total ded las
                                       providencias para el caso

+-------------------+-------------------+-------------------------+
| Fecha      | Modifier    | Descripcion                          |
+-------------------+-------------------+-------------------------+
| 19MAY2023  | jagonzaj    | Se crea el proceso para mostrar las  |
|            |             |  providedncias                       |
| 30JUN2023  | jagonzaj    | Se incluye color rojo en el          |
|            |             |  background de las celdas para       |
|            |             |  revelar la razon de porque no cruza |
|            |             |  la retencion                        |
+-------------------+-------------------+-------------------------+

ESTANDAR PEP8
REVISADO CON SONARLINT
"""
from timeit import default_timer as timer
from datetime import timedelta
from datos import Consultas, RetencionesQ
import pandas as pd
import time, random


class Encontradas:
    '''Para pintar en rojo'''
    def __init__(self, db):
        '''constructor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)

    def tratar_providencias(self, _sql, recortar=False):
        '''tratar providencias'''
        longitud_real = 0
        longitud_fisicas = 0
        df_providencia = self.db.get_df_from_pg(_sql.get_sql_providenciadas())
        num_proovidencias = len(df_providencia.index)
        filtrar_fisicas = False
        if num_proovidencias > 2000:
            filtrar_fisicas = True

        df_providencia = df_providencia.fillna(0)
        df_providencia = \
            df_providencia.sort_values(by=['autorizacion'], ascending=True)
        df_providencia = df_providencia.reset_index()
        if not df_providencia.empty:
            df_hay = df_providencia.copy()
            df_contadas = (df_hay.groupby(['autorizacion']).size().reset_index(name='conteo'))
            df_contadas = df_contadas[df_contadas["conteo"] > 1]
            considerar = df_contadas["autorizacion"].unique().tolist()

            for auto in considerar:
                df_corresponden = df_providencia[df_providencia['autorizacion'].isin([auto])]
                if "index" in df_corresponden.columns:
                    df_corresponden = df_corresponden.drop(['index'], axis=1)
                if "level_0" in df_corresponden.columns:
                    df_corresponden = df_corresponden.drop(['level_0'], axis=1)
                indices_llenos = df_corresponden[df_corresponden['numero_autorizacion_pintar'].apply(lambda x: len(str(x)) > 5)].index
                indices_vacios = df_corresponden[df_corresponden['numero_autorizacion_pintar'] == 0].index
                df_contadas_corr = (df_corresponden.groupby(['secuencial_retencion']).size().reset_index(name='conteo'))
                if not df_contadas_corr.empty:
                    df_errantes = df_contadas_corr[df_contadas_corr["conteo"] == 1]
                    lista_errantes = pd.unique(df_errantes["secuencial_retencion"])
                    indices_errantes = df_corresponden[df_corresponden['secuencial_retencion'].isin(lista_errantes)].index
                    if len(indices_errantes) > 0:
                        for x in indices_errantes:
                            if x in indices_llenos:
                                indices_llenos = indices_llenos.drop(x)
                    if len(indices_vacios) > 0 and len(indices_llenos) > 0:
                        df_providencia.drop(indices_llenos, inplace=True)

            df_hay = df_providencia.copy()
            df_contadas = (df_hay.groupby(['autorizacion', 'secuencial_retencion']).size().reset_index(name='conteo'))
            df_contadas = df_contadas[df_contadas["conteo"] > 1]
            for ix, auto in df_contadas.iterrows():
                df_corresponden = df_providencia[df_providencia['autorizacion'].isin([auto["autorizacion"]]) & df_providencia['secuencial_retencion'].isin([auto["secuencial_retencion"]])]
                # print(f"{ix} 53  df_corresponden \n {df_corresponden}")
                indices_llenos = df_corresponden[ df_corresponden['fecha_emision_pintar'].apply(lambda x: len(str(x)) == 10)].index
                indices_vacios = df_corresponden[ df_corresponden['fecha_emision_pintar'] == 0].index
                df_contadas_corr = (df_corresponden.groupby(['secuencial_retencion']).size().reset_index(name='conteo'))
                if not df_contadas_corr.empty:
                    df_errantes = df_contadas_corr[df_contadas_corr["conteo"] == 1]
                    lista_errantes = pd.unique(df_errantes["secuencial_retencion"])
                    indices_errantes = df_corresponden[df_corresponden['secuencial_retencion'].isin(lista_errantes)].index
                    if len(indices_errantes) > 0:
                        for x in indices_errantes:
                            if x in indices_llenos:
                                indices_llenos = indices_llenos.drop(x)

                if len(indices_vacios)> 0 and len(indices_llenos) > 0:
                    df_providencia.drop(indices_llenos, inplace=True)

            if "index" in df_providencia.columns:
                df_providencia = df_providencia.drop(['index'], axis=1)

            df_providencia = df_providencia.drop_duplicates()

            df_providencia = df_providencia.sort_values(by=['anio','mes','autorizacion'], ascending=True)
            longitud_real = len(df_providencia.index) 

            if filtrar_fisicas and recortar:
                df_providencia_fis = df_providencia.copy() 
                df_providencia_fis = df_providencia_fis[df_providencia_fis["autorizacion"].str.len() < 20]
                longitud_fisicas = len(df_providencia_fis.index)

                if longitud_fisicas > 1000:
                    df_providencia_fis = df_providencia_fis[:999]
                    df_providencia = df_providencia_fis.copy()

                if longitud_fisicas == 0:
                    df_providencia = df_providencia[:999]

        return df_providencia, longitud_real, longitud_fisicas

    def get_providencias_revisadas(self):
        '''revision de providencias'''
        _his = self.db.uf.his
        _jd = self.db.uf.pi
        _sql = RetencionesQ.NoCruzan(_jd)           
        _sql.jd.fecha_hoy = self.db.get_fecha_ymd()

        df_fantasma = \
            self.db.get_df_from_pg(_sql.get_sql_informe_filtros(" es_fantasma = 'si'"))
        df_fallecido = \
            self.db.get_df_from_pg(_sql.get_sql_informe_filtros(" es_fallecido = 'si'"))
        df_fantasma = df_fantasma.fillna(0)
        df_fallecido = df_fallecido.fillna(0)

        if isinstance(_sql.jd.periodo_inicial, pd.Timestamp):
            _sql.jd.periodo_inicial = str(_sql.jd.periodo_inicial)[:10]

        if isinstance(self.db.uf.pi.periodo_final, pd.Timestamp):
            _sql.jd.periodo_final = str(_sql.jd.periodo_final)[:10]

        df_providencia, longitud_real, longitud_fisicas = \
            self.tratar_providencias(_sql, recortar=True)
        df_fantasma_, longitud_fan = self.db.get_planck(df_fantasma)
        df_fallecido_, longitud_fall = self.db.get_planck(df_fallecido)
        longitud_fan = len(df_fantasma.index)
        longitud_fall = len(df_fallecido.index)
        df_providencia_,  longitud_prov = self.db.get_planck(df_providencia)
        longitud_prov = len(df_providencia.index)

        self.db.uf.his.num_providencias = longitud_prov
        # contri_abot = self.db.uf.abot(self.db.uf.pi.contri)
        fragmentado = self.db.uf.fragmentar_h(_sql.jd.contri, _sql.jd.periodo_inicial_org, _sql.jd.periodo_final_org)

        fecha = self.db.get_fecha_ymd()
        nombre = f"PROV_{_sql.jd.contri}_{fecha}_PROVID.xlsx"
        placebo = str(int(random.uniform(15, 100000))).zfill(10)
        if str(_sql.jd.tramite).strip() == '':
            _sql.jd.tramite = '19042008'
        enlace = f""" <a href="get_informe/{fragmentado}01{placebo}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="{nombre}"
                        target="_blank" id='dev_a_provid' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Providencias</a> """
        resultado = {
            "jd_providencias": df_providencia_,
            "longitud_prov": longitud_prov,
            "longitud_real": longitud_real,
            "longitud_fisicas": longitud_fisicas,
            "longitud_excel": self.db.uf.his.num_excel_filas,
            "jd_fantasma": df_fantasma_,
            "longitud_fan": longitud_fan,
            "jd_fallecido": df_fallecido_,
            "longitud_fall": longitud_fall,
            "enlace": enlace,
            "valida": 1
        }
        return resultado
