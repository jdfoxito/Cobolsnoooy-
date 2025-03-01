"""Informe, desde Marzo 2023
Funcionalidades: Generaar el informe de revision y su paginacion
ENTRADA:
    +-------------------+-------------------+-------------------+
    | 0500XXXXXXXX001   | 2021-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+
Se establecera un rango entre la fecha inicial y final
+-------------+------------+--------------------------------------------------+
| Fecha       | Modifier   | Descripcion                                      |
+-------------+------------+--------------------------------------------------+
| 03MAR2023   | jagonzaj   | Informe de revision inicial por base para obtener|
|             |            | las retenciones cruzan y no cruzan               |
| 19ABR2023   | jagonzaj   | proceso con multihilo para el informe de revision|
| 19ENE2024   | jagonzaj   | proceso de duplicados se cambia a uno que incluye|
|             |            | mas casos, por casos recientes                   |
| 15MAR2023   | jagonzaj   | se elimina la Complejidad Ciclomática            |
|             |            | (Thomas McCabe,1976), en algunos metodos que     |
|             |            |       pasaban de 15 en esta metrica              |
|             |            |   M = E − N + 2P                                 |
|             |            |          M = Complejidad ciclomática ().         |
|             |            |          E = Núm de aristas del grafo. Una arista|
|             |            |              conecta dos vértices si una sentenci|
|             |            |               puede ser ejecutada inmediatamente |
|             |            |               después de la 1ra.                 |
|             |            |          N = Número de nodos del grafo           |
|             |            |               correspondientes a sentencias      |
|             |            |               del programa.                      |
|             |            |          P = Número de componentes conexos,      |
|             |            |               nodos de salida.                   |
+-------------+------------+--------------------------------------------------+

ESTANDAR PEP8
REVISADO CON SONARLINT 4.3.0
"""

import json 
import os
import csv
import numpy, random 
import pandas as pd
import math
from datetime import datetime
from timeit import default_timer as timer
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from joblib import Parallel, delayed, parallel_backend
from logicas import Materiales
from flask import session 
from datos import Consultas, RetencionesQ


class Revision(Materiales.Universales):
    '''informe generado '''
    df_listado_excel = ''
    df_administracion = ''
    df_listado_completo = ''
    df_resultado_aparente = ''
    tercero = ''
    autorizacion_tercero = ''
    fecha_tercero = ''    
    secuencia_tercero = ''    
    tipo_frecuencia = 'MENSUAL'
    df_serie_periodo_neptuno = pd.DataFrame()   
    df_duplicados_encontrados = pd.DataFrame()  
    df_serie_periodo_semestral = pd.DataFrame()      
    df_para_duplicados = pd.DataFrame()

    def __init__(self, db):
        '''constructor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)   
        self.df_periodos_listado = []
        self.df_periodos_listado_suma = 0
        self.calculo_tipo = 1     
        self.usuario = ''   
        pd.options.mode.copy_on_write = True        
        pd.set_option('future.no_silent_downcasting', True)

    def get_consolidar_resumen_vectorizado(self, df_consolidar, renombrar_por):
        '''consolidar resumen'''
        df_consolidado = pd.DataFrame({'anio':[],'mes':[], renombrar_por:[]} )
        if not df_consolidar.empty:
            if self.tipo_frecuencia == "MENSUAL":
                df_consolidado = pd.DataFrame(df_consolidar.groupby(['anio', 'mes'])["valor_retencion"].sum()).reset_index()    
                df_consolidado['valor_retencion']= df_consolidado['valor_retencion'].apply(lambda x:self.db.uf.redondear(x, 3))
            if self.tipo_frecuencia == "SEMESTRAL" and not df_consolidar.empty:
                df_consolidado = pd.DataFrame(df_consolidar.groupby(['frecuencia'])['valor_retencion'].sum()).reset_index()    
                df_consolidado['valor_retencion']= df_consolidado['valor_retencion'].apply(lambda x:self.db.uf.redondear(x, 3))
                df_consolidado[['anio', 'mes']] = df_consolidado['frecuencia'].str.split('_', expand=True)
                df_consolidado = df_consolidado.drop('frecuencia', axis=1)

            df_consolidado["anio"] = df_consolidado["anio"].astype(int) 
            df_consolidado["mes"] = df_consolidado["mes"].astype(int)             

            df_consolidado.rename(columns={'valor_retencion': renombrar_por}, inplace=True)
        return df_consolidado, len(df_consolidado.index)    
    
    def get_consolidar_resumen_vectorizado_free(self, df_consolidar, renombrar_por, valor_retencion_columna):
        '''consolidar resumen '''
        df_consolidado = pd.DataFrame({'anio': [], 'mes': [], renombrar_por: []})
        if not df_consolidar.empty:
            if self.tipo_frecuencia == "MENSUAL":
                df_consolidado = pd.DataFrame(df_consolidar.groupby(['anio', 'mes'])[valor_retencion_columna].sum()).reset_index()    
                df_consolidado[valor_retencion_columna] = df_consolidado[valor_retencion_columna].apply(lambda x:self.db.uf.redondear(x, 3))
            if self.tipo_frecuencia == "SEMESTRAL":
                df_consolidado = pd.DataFrame(df_consolidar.groupby(['frecuencia'])[valor_retencion_columna].sum()).reset_index()    
                df_consolidado[valor_retencion_columna] = df_consolidado[valor_retencion_columna].apply(lambda x:self.db.uf.redondear(x, 3))
                df_consolidado[['anio', 'mes']] = df_consolidado['frecuencia'].str.split('_', expand=True)
                #df_consolidado.iloc[:]["anio"] = df_consolidado["anio"].astype(int) 
                #df_consolidado.iloc[:]["mes"] = df_consolidado["mes"].astype(int)             
                df_consolidado = df_consolidado.drop('frecuencia', axis=1)

            df_consolidado["anio"] = df_consolidado["anio"].astype(int) 
            df_consolidado["mes"] = df_consolidado["mes"].astype(int)             
        
            df_consolidado.rename(columns={valor_retencion_columna: renombrar_por}, inplace=True)
        return df_consolidado, len(df_consolidado.index)        
    
    def get_merge_multiples(self, df_unir, tipo, claves):
        '''combinar multiples dataframes'''
        all_merged = df_unir[0]
        for to_merge in df_unir[1:]:
            all_merged = pd.merge(
                left=all_merged
                , right=to_merge
                , how=tipo
                , on=[claves[0], claves[1]]
                )
        return all_merged
    
    def get_no_listado(self, a, b, c, d, e):
        '''no listado'''
        r = 0
        if min(a, c) - b >= 0:
            r = b - d - e    
        return r

    def get_negados_dups(self, a, b, c, d):
        '''negados duplicados'''
        return a + b + c + d

    def get_aceptados_cadena(self, a, c, e, f, g):
        '''aceptados cadena'''
        r = 0
        if (a - c - e - f - g) > 0:
            r = a - c - e - f - g    
        if r < 0:
            r = 0
        return r        

    def get_vncf(self, a, b, c):
        '''get vcnf'''
        d = 0
        if min(a, b) - c >= 0:
            d = min(a, b) - c
        return d

    def get_dif_actualizar(self, a, b):
        '''diferencia actualizar'''
        c = 0
        if a - b >= 0:
            c = a - b
        return c

    def set_periodos_consecutivos(self, _sql):
        '''perdiodos consecutivos'''
        df_serie_p = pd.date_range(start=f'{_sql.jd.periodo_inicial}', end=f'{_sql.jd.periodo_final}', freq="MS")
        lista_p = []
        for x_p in df_serie_p:
            lista_p.append({"anio": int(str(x_p)[0:4]), "mes":  int(str(x_p)[5:7])})
        return pd.DataFrame(lista_p)

    def get_guardar_para_providencias(self, df_retorno_papel, _sql) -> None:
        '''guardado de provicdencias'''
        df_no_enlazan = df_retorno_papel[(df_retorno_papel['cruza'].astype('string') == 'no')]
        df_no_enlazandb = df_no_enlazan.copy()
        df_no_enlazandb.rename(columns={'numero_documento': 'contri'}, inplace=True)       

        if "index" in df_no_enlazandb.columns:
            df_no_enlazandb.drop("index", axis=1, inplace=True)

        _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
        _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_PROVIDENCIAS_VALS
        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        self.db.get_reseto_tabla_estandar_jd(_sql)
         
        df_no_enlazandb = df_no_enlazandb.drop('fecha_emi_ret', axis=1)
        df_no_enlazandb = self.db.preparar_dataframe(df_no_enlazandb)
        df_no_enlazandb["valor_retencion_aceptado"] = 0
        _sql.jd.df = df_no_enlazandb
        self.db.guardar_dataframe_jd(_sql)            
        _sql.jd.df = ''
        self.db.guardar_dataframe_pg(df_no_enlazandb, _sql.jd.tabla_relacional, _sql.jd.esquema)
        
    def get_lista_indices(self, df_for_dup, df_duplicados_, _sql):
        df_cine = df_for_dup.drop_duplicates()
        lista_indices = []        
        for ix, filas in df_cine.iterrows():
            auto = filas["autorizacion"]
            valr = filas["valor_retencion"]
            sql_ref = _sql.get_lista_indices(auto, valr)
            i_remover = self.db.get_scalar(sql_ref)
            if i_remover > 1:
                df_indices = df_duplicados_.loc[(df_duplicados_['autorizacion'] == auto) & (df_duplicados_['valor_retencion'] == valr)]
                lista_indices += df_indices.index.values.tolist()          
        return lista_indices

    def borrar_columnas(self, df, columnas):
        '''borrado de columnas'''
        for x in columnas:
            if x in df.columns:
                df = df.drop(x, axis=1)    
        return df

    def set_frecuencia_picky(self, df_semestral, df_target):
        df_target_2021 = pd.DataFrame()
        df_target_2011 = pd.DataFrame()
        if "frecuencia" not in df_target.columns: 
            df_target["frecuencia"] = ''
            df_target["cod_impuesto"] = ''
            df_target["pre_frecuencia"] = df_target["anio"].astype(str) + df_target["mes"].astype(str)
            df_semestral_2021 = df_semestral[df_semestral["codigo_impuesto"].astype(int) == 2021]
            df_semestral_2011 = df_semestral[df_semestral["codigo_impuesto"].astype(int) == 2011]
            df_target_2011 = pd.merge(df_semestral_2011, df_target, on=['anio','mes'], how='inner')  
            df_target_2011 = self.borrar_columnas(df_target_2011, ['frecuencia_y','fecha_ini', 'fecha_fin', 'level_0' ]) 
            if "frecuencia_x" in df_target_2011.columns:
                df_target_2011.rename(columns={'frecuencia_x': 'frecuencia'}, inplace=True)        
            pre_frecuencias = pd.unique(df_target_2011["pre_frecuencia"])
            df_target_2021 = df_target[~df_target["pre_frecuencia"].isin(pre_frecuencias)] 
            df_target_2011 = df_target[df_target["pre_frecuencia"].isin(pre_frecuencias)] 
            df_target_2011["frecuencia"] = df_target_2011["anio"].astype(str) + "_" + df_target_2011["mes"].astype(str)  
            df_target_2011["cod_impuesto"] = '2011'
            df_target_2021 = df_target_2021.reset_index()
            for ix, fila in df_target_2021.iterrows():
                anio = int(fila["anio"])
                mes = int(fila["mes"])
                for iy, periodo in df_semestral_2021.iterrows():
                    anio_ref = int(periodo["anio"])
                    mes_ref = int(periodo["mes"])
                    if anio == anio_ref and mes < 7 and mes <= mes_ref and mes_ref < 7:
                        df_target_2021.at[ix, "frecuencia"] = periodo["frecuencia"]
                        df_target_2021.at[ix, "cod_impuesto"] = periodo["codigo_impuesto"]
                    elif anio == anio_ref and mes > 6 and  mes_ref > 6:
                        df_target_2021.at[ ix, "frecuencia"] = periodo["frecuencia"]
                        df_target_2021.at[ ix, "cod_impuesto"] = periodo["codigo_impuesto"]                        
            if not df_target_2021.empty:                        
                df_target_2021_x = df_target_2021[df_target_2021["frecuencia"].str.len()==0]
                df_target_2021_y = df_target_2021[df_target_2021["frecuencia"].str.len() >0]
                df_target_2021_x["frecuencia"] = df_target_2021_x["anio"].astype(str)+"_" + df_target_2021_x["mes"].astype(str)
                if not df_target_2021_y.empty:
                    df_target_2021 = pd.concat([df_target_2021_x, df_target_2021_y])
                else:
                    df_target_2021 = df_target_2021_x
                
            if 'level_0' in df_target_2011.columns:
                df_target_2011 = df_target_2011.drop('level_0', axis=1) 
                
            if 'level_0' in df_target_2021.columns:
                df_target_2021 = df_target_2021.drop('level_0', axis=1)    

            df_target_2011 = df_target_2011.reset_index()
            df_target_2021 = df_target_2021.reset_index()
            
            if 'level_0' in df_target_2011.columns:
                df_target_2011 = df_target_2011.drop('level_0', axis=1) 
                
            if 'level_0' in df_target_2021.columns:
                df_target_2021 = df_target_2021.drop('level_0', axis=1)             
                        
            if 'index' in df_target_2021.columns:
                df_target_2021 = df_target_2021.drop('index', axis=1)  

            if 'index' in df_target_2011.columns:
                df_target_2011 = df_target_2011.drop('index', axis=1)  

            df_target = pd.concat([df_target_2011,  df_target_2021])
        if 'pre_frecuencia' in df_target.columns:
            df_target = df_target.drop('pre_frecuencia', axis=1)    

        if 'level_0' in df_target.columns:
            df_target = df_target.drop('level_0', axis=1)    
                       
        if 'index' in df_target.columns:
            df_target = df_target.drop('index', axis=1)  

        df_NAN = df_target[(df_target["frecuencia"] == '') | (df_target["frecuencia"].isna()) | (df_target["frecuencia"] == 'NaN') ]
        for ix, fila in df_NAN.iterrows():
            df_target.at[ix, "frecuencia"] = str(fila["anio"])+"_"+str(fila["mes"])
            
        return df_target

    def get_neptuno(self, df_serie_periodo_semestral, dg_target):
        '''consolidar frecuencias'''
        dg_target = self.set_frecuencia_picky(df_serie_periodo_semestral, dg_target).copy()
        
        dg_target = pd.DataFrame(dg_target.groupby(['frecuencia'])["valor_retencion"].sum()).reset_index()
        dg_target[['anio', 'mes']] = dg_target['frecuencia'].str.split('_', expand=True)
        dg_target["anio"] = dg_target["anio"].astype(str).astype(int) 
        dg_target["mes"] = dg_target["mes"].astype(str).astype(int)             
        frecuencias_habilitadas = pd.unique(dg_target["frecuencia"]).tolist()
        df_semestral_relleno = df_serie_periodo_semestral[~(df_serie_periodo_semestral["frecuencia"].isin(frecuencias_habilitadas))]
        dg_target_pre = pd.DataFrame()
        if not df_semestral_relleno.empty:
            df_n1 = dg_target.copy() 
            dg_target_pre = df_semestral_relleno[['frecuencia', 'anio', 'mes']]
            dg_target_pre["valor_retencion"] = 0.0
            dg_target_pre = pd.concat([dg_target_pre, df_n1]) 
            dg_target = dg_target_pre
        
        dg_target = dg_target.reset_index() 
        return dg_target

    def get_periodos(self, df_pangea, df_retorno_papel, _sql):
        '''get periodos'''
        len_duplicados = 0
        df_serie_periodo = pd.DataFrame()
        df_duplicados_ = pd.DataFrame()
        df_pangea_sumas = pd.DataFrame()
        df_duplicados = pd.DataFrame()
        df_para_dups = pd.DataFrame()
        if self.tipo_frecuencia == "SEMESTRAL":
            df_retorno_papel = self.set_frecuencia_picky(self.df_serie_periodo_semestral, df_retorno_papel)

        dup_conar = pd.DataFrame()
        if self.tipo_frecuencia == "MENSUAL":
            df_serie_periodo = self.set_periodos_consecutivos(_sql)
            df_serie_periodo["anio"] = df_serie_periodo["anio"].astype(int) 
            df_serie_periodo["mes"] = df_serie_periodo["mes"].astype(int)             

        if self.tipo_frecuencia == "SEMESTRAL":
            df_serie_periodo = self.df_serie_periodo_semestral[["anio", "mes"]]

        if not df_serie_periodo.empty:   
            _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
            _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_RESULTADO_ANALISIS_RETENCION
            _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
            self.db.get_reseto_tabla_estandar_jd(_sql)

            if self.tipo_frecuencia == "MENSUAL":
                df_pangea_sumas = pd.DataFrame(df_pangea.groupby(['anio', 'mes'])["valor_retencion"].sum()).reset_index()

            if self.tipo_frecuencia == "SEMESTRAL":
                df_pangea_sumas = self.get_neptuno(self.df_serie_periodo_semestral, df_pangea)

            df_para_dups = self.df_listado_completo
            df_duplicados_ = self.df_duplicados_encontrados

            self.df_listado_completo["valor_retencion"] = self.df_listado_completo["valor_retenido"] 
            self.df_listado_completo['fecha_emision'] = pd.to_datetime(self.df_listado_completo['fecha_emision'])
            self.df_listado_completo['anio'] = self.df_listado_completo['fecha_emision'].dt.year
            self.df_listado_completo['mes'] = self.df_listado_completo['fecha_emision'].dt.month            
            df_periodos_cero_arch = pd.DataFrame()
            if not df_para_dups.empty:
                df_for_dup = df_duplicados_[['autorizacion', 'valor_retencion']]
                lista_indices = self.get_lista_indices(df_for_dup, df_duplicados_, _sql)
                df_duplicados_.drop(lista_indices, inplace=True)
                dup_conar = df_duplicados_.groupby(['autorizacion']).count()
                dup_conar = pd.DataFrame(dup_conar).reset_index()                  
                dup_conar = dup_conar[['autorizacion', 'agente_retencion']]
                dup_conar.rename(columns={'agente_retencion': 'conteo'}, inplace=True)
                df_duplicados, len_duplicados = self.db.get_lorentz(df_duplicados_)
                df_archivos_periodos = df_para_dups[['anio', 'mes']]
                df_archivos_periodos = df_archivos_periodos.drop_duplicates()
                df_archivos_periodos["anio"] = df_archivos_periodos["anio"].astype(int) 
                df_archivos_periodos["mes"] = df_archivos_periodos["mes"].astype(int) 
                if self.tipo_frecuencia == "MENSUAL":
                    df_periodos_cero_arch = df_serie_periodo.merge(df_archivos_periodos, indicator=True, how='left').loc[lambda x: x['_merge'] != 'both']

            # 1 que pasa si no hay periodos cero
            df_periodos_cero_arch_a = pd.DataFrame()
            if not df_periodos_cero_arch.empty:
                df_periodos_cero_arch_a = df_periodos_cero_arch[['anio', 'mes']] 
                df_periodos_cero_arch_a["valor_retencion"] = 0.00

            df_perceros_sumas_ = pd.DataFrame()
            if self.tipo_frecuencia == "MENSUAL":
                df_perceros_sumas_ = pd.DataFrame(df_retorno_papel.groupby(['anio', 'mes'])["valor_retencion"].sum()).reset_index()

            if self.tipo_frecuencia == "SEMESTRAL":
                df_perceros_sumas_ = pd.DataFrame(df_retorno_papel.groupby(['frecuencia'])["valor_retencion"].sum()).reset_index()
                df_perceros_sumas_[['anio', 'mes']] = df_perceros_sumas_['frecuencia'].str.split('_', expand=True)
                df_perceros_sumas_["anio"] = df_perceros_sumas_["anio"].astype(int) 
                df_perceros_sumas_["mes"] = df_perceros_sumas_["mes"].astype(int) 

            df_perceros_sumas_a = df_perceros_sumas_[['anio', 'mes']]
            df_perceros_sumas_a["anio"] = df_perceros_sumas_a["anio"].astype(int) 
            df_perceros_sumas_a["mes"] = df_perceros_sumas_a["mes"].astype(int) 
            df_no_aceptado = pd.DataFrame()
            if len(df_pangea_sumas.index) != len(df_serie_periodo.index):
                if self.tipo_frecuencia == "MENSUAL":
                    df_no_aceptado = df_serie_periodo.merge(df_pangea_sumas, indicator=True, how='left').loc[lambda x: x['_merge'] != 'both']

                if self.tipo_frecuencia == "SEMESTRAL":
                    df_no_aceptado = df_pangea_sumas

            df_pangea_sumas_a = df_pangea_sumas[['anio', 'mes']]
            df_pangea_sumas_a["anio"] = df_pangea_sumas_a["anio"].astype(int)
            df_pangea_sumas_a["mes"] = df_pangea_sumas_a["mes"].astype(int)
        
            df_periodos_cero = df_perceros_sumas_a.merge(df_pangea_sumas_a, indicator=True, how='left').loc[lambda x: x['_merge'] != 'both']
            df_periodos_cero["valor_retencion"] = 0

            if not df_periodos_cero_arch_a.empty:
                df_periodos_cero_c = pd.concat([df_periodos_cero[['anio', 'mes','valor_retencion']], df_periodos_cero_arch_a ])
                df_pangea_sumas = pd.concat([df_pangea_sumas, df_periodos_cero_c]).reset_index()
                df_pangea_sumas = df_pangea_sumas.drop('index', axis=1).reset_index()

            df_pangea_sumas = df_pangea_sumas[['anio', 'mes', 'valor_retencion']]
            if not df_no_aceptado.empty:
                df_no_aceptado["valor_retencion"] = 0.0
                df_pangea_sumas = pd.concat([df_pangea_sumas, df_no_aceptado]).reset_index()
                
            df_pangea_sumas.sort_values(['anio', 'mes'],ascending=[True, True], inplace=True)            
            df_pangea_sumas['anio'] = df_pangea_sumas['anio'].astype(int)
            df_pangea_sumas = df_pangea_sumas[df_pangea_sumas['anio'] > 0]
            df_pangea_sumas = df_pangea_sumas.groupby(['anio', 'mes']).agg({'valor_retencion':'sum'}).reset_index()        
            df_pangea_sumas["anio"] = df_pangea_sumas["anio"].astype(int)
            df_pangea_sumas["mes"] = df_pangea_sumas["mes"].astype(int)         
            df_pangea_sumas = self.db.preparar_dataframe(df_pangea_sumas)                        
            if "frecuencia" in df_pangea_sumas.columns:
                df_pangea_sumas = df_pangea_sumas.drop('frecuencia', axis=1)     

            _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_RESULTADO_ANALISIS_RETENCION            
            _sql.jd.df = df_pangea_sumas

            self.guardar_warp_jd(_sql, cabecera=True)
            _sql.jd.df = ''            
        return df_duplicados_, df_duplicados, len_duplicados, dup_conar, df_para_dups
        
    def get_crear_estadistica(self,
                              df_retenciones,
                              df_declarados,
                              _sql,
                              _his):
        '''armando el informe'''
        df_declarados["anio"] = df_declarados["anio"].astype(int)
        df_declarados["mes"] = df_declarados["mes"].astype(int)     
        
        df_serie_periodo = pd.DataFrame()
        self.tipo_frecuencia = _his.frecuenciamiento 
        if self.tipo_frecuencia == "SEMESTRAL":
            self.df_serie_periodo_semestral = self.get_periodos_semestrales(_sql)
       
            df_serie_periodo = self.df_serie_periodo_semestral[["anio","mes"]]
            df_serie_periodo["anio"] = df_serie_periodo["anio"].astype(int) 
            df_serie_periodo["mes"] = df_serie_periodo["mes"].astype(int)             
            self.df_serie_periodo_neptuno = df_serie_periodo 
      
        df_retenciones["anio"] = df_retenciones["anio"].astype(int)
        df_retenciones["mes"] = df_retenciones["mes"].astype(int)     
        df_retenciones.sort_values(['anio', 'mes', 'fecha_emi_retencion'], ascending=[True, True, True], inplace=True)            

        df_serie_periodo = self.set_periodos_consecutivos(_sql)

        if self.tipo_frecuencia == "SEMESTRAL":        
            df_serie_periodo = self.df_serie_periodo_neptuno
            df_retenciones = self.set_frecuencia_picky(self.df_serie_periodo_semestral, df_retenciones)
            df_retenciones = df_retenciones.reset_index()
            df_retenciones["anio"] = df_retenciones["anio"].astype(int)
            df_retenciones["mes"] = df_retenciones["mes"].astype(int)     
            df_retenciones.sort_values(['anio', 'mes', 'fecha_emi_retencion'], ascending=[True, True, True], inplace=True)            
        else:
            df_retenciones["cod_impuesto"] = '2011'
            df_retenciones["frecuencia"] = df_retenciones["anio"].astype(str) + df_retenciones["mes"].astype(str)            

        self.get_guardar_para_providencias(df_retenciones, _sql)
        
        df_serie_periodo["anio"] = df_serie_periodo["anio"].astype(int) 
        df_serie_periodo["mes"] = df_serie_periodo["mes"].astype(int)             

        print(f"df_serie_periodo {df_serie_periodo}")

        df_no_pasan = df_retenciones[(df_retenciones['es_fantasma'].astype('string') == 'si') | (df_retenciones['es_fallecido'].astype('string') == 'si') | (df_retenciones['es_ffpv'].astype('string') == 'si') | (df_retenciones['cruza'].astype('string') == 'no')]
        
        df_acepttados = df_retenciones[(df_retenciones['es_fantasma'].astype('string') == '') & (df_retenciones['es_fallecido'].astype('string') == '') & (df_retenciones['es_ffpv'].astype('string') == '') & (df_retenciones['conclusion'].astype('string') == 'si')]
        df_duplicados_, df_duplicados_ret, len_duplicado, df_conteo_dups, df_listado_clean = self.get_periodos(df_acepttados, df_retenciones, _sql)
        if "level_0" in df_listado_clean.columns:
            df_listado_clean.drop("level_0", axis=1, inplace=True)             

        if self.tipo_frecuencia == "SEMESTRAL":
            df_listado_clean = self.set_frecuencia_picky(self.df_serie_periodo_semestral, df_listado_clean)
            df_listado_clean = df_listado_clean.reset_index()

        df_ingresados, len_ingresados = self.get_consolidar_resumen_vectorizado_free(df_listado_clean, "ingresados", "valor_retenido")
        len_no_pasan = 0
        # 3 if not df_no_pasan.empty:
        df_no_pasan, len_no_pasan = self.get_consolidar_resumen_vectorizado(df_no_pasan, "negados_x_any")
        # 3 else:

        df_acepttados, len_aceptados = self.get_consolidar_resumen_vectorizado(df_acepttados,"aceptados")
        # 4 fantasmas

        df_ghost = df_retenciones[(df_retenciones['es_fantasma'].astype('string') == 'si')]
        _his.num_fantasmas = len(df_ghost.index)
        df_ghost, len_fantasmas = self.get_consolidar_resumen_vectorizado_free(df_ghost, "fantasmas", "valor_retenido_listado")
        _his.num_fantasmas = len(df_ghost.index)
        # endfantasmas

        # 10 esfallecido
        df_deadpool = df_retenciones[(df_retenciones['es_fallecido'].astype('string') == 'si')]
        _his.num_fallecidos = len(df_deadpool.index)
        df_deadpool, len_falles = self.get_consolidar_resumen_vectorizado_free(df_deadpool, "fallecidos", "valor_retenido_listado")
        # 9 endesfallecido
        # 8 esffpv

        # 6 df_no_base.eval("no_constan_base = total_impuesto_a_pagar - retenciones_a_devolver",inplace=True)
        df_esffpv = df_retenciones[(df_retenciones['es_ffpv'].astype('string') == 'si')]
        _his.num_ffpv = len(df_esffpv.index)
        df_esffpv, len_ffpv = self.get_consolidar_resumen_vectorizado(df_esffpv, "esffpv")
        # 4 end_esffpv

        # 3 no cruzan
        df_no_enlazan = df_retenciones[(df_retenciones['cruza'].astype('string') == 'no')]
        df_no_enlazan, len_nocruzan = self.get_consolidar_resumen_vectorizado_free(df_no_enlazan, "nocruzan", "valor_retenido_listado")
        df_no_reporta, len_no_reporta = self.get_consolidar_resumen_vectorizado_free(df_retenciones, "valor_no_reporta", "no_reporta")

        # 2 no cruzan
        df_cruzan = df_retenciones[(df_retenciones['cruza'].astype('string') == 'si')]
        df_cruzan, len_cruzan_fe_fi = self.get_consolidar_resumen_vectorizado(df_cruzan, "cruzan_fe_fi")

        # 1 . solo no cruzaron
        df_no_cruzan_sin_obs = df_retenciones[(df_retenciones['es_fantasma'].astype('string') == '') & (df_retenciones['es_fallecido'].astype('string') == '') & (df_retenciones['es_ffpv'].astype('string') == '') & (df_retenciones['cruza'].astype('string') == 'no')   ]
        df_no_cruzan_sin_obs, len_no_pasan_sinobs = self.get_consolidar_resumen_vectorizado(df_no_cruzan_sin_obs, "no_cruzaron_sin_obs")

        # 6 duplicados
        df_duplicado = pd.DataFrame(columns=['anio', 'mes', 'duplicados'])
        len_duplicado = 0
        if not df_duplicados_.empty:
            print(f" df_duplicados_   {df_duplicados_.columns} ")
            df_duplicado, len_duplicado = self.get_consolidar_resumen_vectorizado(df_duplicados_,"duplicados")
            len_duplicado = len(df_duplicados_.index)
  
        df_unir = [df_serie_periodo, df_declarados, df_ingresados,
                   df_acepttados, df_no_pasan,  df_ghost, df_deadpool,
                   df_esffpv, df_no_enlazan, df_duplicado,
                   df_no_cruzan_sin_obs, df_cruzan, df_no_reporta]

        claves = ['anio', 'mes']
        tipo = 'left'
        df_pre_informe = self.get_merge_multiples(df_unir, tipo, claves)

        df_pre_informe = df_pre_informe.fillna(0)
        df_pre_informe['negados_dups'] = df_pre_informe.apply(lambda r : self.get_negados_dups(r["fantasmas"] ,r["fallecidos"],  r["duplicados"], r["valor_no_reporta"] ), axis=1)
        df_pre_informe['mayores'] = df_pre_informe["retenciones_fuente_iva"]
        # 1 no en listado ncf and ncb                                                                  A                       B               C              D                   E
        df_pre_informe['no_listado'] = df_pre_informe.apply(lambda r : self.get_no_listado(r['retenciones_fuente_iva'], r['ingresados'], r['mayores'], r['aceptados'],  r["negados_dups"]), axis=1)    
        # 2 comprobantes no sustentados
        df_pre_informe['v_ncf'] = df_pre_informe['no_cruzaron_sin_obs']
        df_pre_informe['diferencia_actualizar'] = df_pre_informe.apply(lambda row : self.get_dif_actualizar(row['retenciones_fuente_iva'], row['mayores']), axis=1)
        df_pre_informe['no_consta_base'] = df_pre_informe.apply(lambda row: self.get_no_base(row['retenciones_fuente_iva'], row['mayores'], row['ingresados']), axis=1)
        df_pre_informe = df_pre_informe.fillna(0)
        # 2 . RESULTADO FINAL                                                                                        A                           C                                   E               F               G               
        df_pre_informe['aceptados_cadena'] = df_pre_informe.apply(lambda r: self.get_aceptados_cadena(r['retenciones_fuente_iva'], r['diferencia_actualizar'] ,  r['no_consta_base'], r["nocruzan"], r["negados_dups"]    ), axis = 1)
        df_pre_informe = df_pre_informe.fillna(0)
        df_pre_informe = df_pre_informe.round(2)
        if "index" in df_pre_informe.columns:
            df_pre_informe.drop("index", axis=1, inplace=True)        
      
        _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
        # 4  _sql.jd.tabla_relacional = "dev_resumen_cadena"
        _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_RESUMEN_CADENA
        _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
        _sql.jd.df = df_pre_informe
        self.guardar_warp_jd(_sql, True)        
        _sql.jd.df = '' 
        df_longitudes = pd.DataFrame({"longitudes": [len_ingresados,
                                                     len_no_pasan,
                                                     len_aceptados,
                                                     len_fantasmas,
                                                     len_falles, len_ffpv,
                                                     len_nocruzan,
                                                     len_no_pasan_sinobs,
                                                     len_duplicado,
                                                     len_cruzan_fe_fi,
                                                     len_no_reporta]})
        return df_pre_informe, df_ingresados, df_longitudes, df_duplicados_ret, df_conteo_dups, _his

    def get_no_base(self, a, b, c):
        '''no constan en base'''
        d = 0
        if min(a, b) - c >= 0:
            d = min(a, b) - c
        return d

    def get_pagina_ir(self, _sql, pagina, num_filas):
        '''numero de pagina para ir'''
        _sql.jd.procedencia = 'interna'
        contri_real = self.db.uf.costelo(_sql.jd.contri_real)
        if num_filas == -1:
            num_filas = self.db.get_scalar( _sql.get_sql_informe_retencion_num_filas(contri_real) )
            df_ingresados = self.db.get_vector(_sql.get_sql_informe_retencion_ing_sumarizado(contri_real))  
            df_ingresado_exp, len_ingresado = self.db.get_lorentz(df_ingresados)

        _sql.jd.contri_real = contri_real
        df_paginado, df_pagina, tiene_previa, tiene_siguiente = self.get_paginar_compras(_sql, pagina, num_filas)
        df_paginado, len_paginado = self.db.get_lorentz(df_paginado)
        df_pagina, len_pagina = self.db.get_lorentz(df_pagina)
        len_paginado = tiene_previa
        len_pagina = tiene_siguiente    
        return {"longitudcompras": num_filas,
                "df_ingresado_exp": df_ingresado_exp, 
                "df_paginado_exp": df_paginado,
                "df_pagina_exp": df_pagina,
                "tiene_previa": len_paginado,
                "tiene_siguiente": len_pagina,
                "valida": 1}
            
    def get_paginar_compras(self, _sql, pagina, num_filas):
        '''paginacion de compras'''
        if not str(pagina).isnumeric():
            pagina = 1
        inicial = 0 
        tiene_previa = 0  
        tiene_siguiente = 0
        contri = self.db.uf.abot(_sql.jd.contri_real)        
        final = int(self.db.config.TAMANHIO_PAGINA)
        numero_paginas = math.ceil(num_filas/final)
        campo_de_vision = self.db.config.CAMPO_DE_VISION
        pagina_inicial = 1
        pagina_final = numero_paginas 
        endurance = (0 if pagina == 1 else pagina) + campo_de_vision
        if numero_paginas >= endurance:
            pagina_inicial = pagina
            pagina_final = (0 if pagina == 1 else pagina) + campo_de_vision             
        else:
            pagina_inicial = numero_paginas - campo_de_vision
            pagina_final = numero_paginas            
            if pagina_inicial < 0:
                pagina_inicial = 1

        lista = []
        entre_a = 0
        entre_b = 0
        final = pagina*self.db.config.TAMANHIO_PAGINA
        inicial = pagina*self.db.config.TAMANHIO_PAGINA - self.db.config.TAMANHIO_PAGINA + 1
        if pagina == 1:
            inicial = 0
        if pagina == numero_paginas:
            final = num_filas 
        entre_a = inicial
        entre_b = final
        if numero_paginas == 1:
            pagina_inicial = 0
            pagina_final = 0
            pagina = 0
            tiene_previa = 0
            tiene_siguiente = 0
        
        lista.append({"paginas":campo_de_vision,  "inicial":pagina_inicial,"final":pagina_final, "contri":contri,"actual":pagina, "num_paginas": numero_paginas })
        _sql.jd.procedencia == 'interna'
        df_pagina = self.db.get_vector(_sql.get_sql_informe_retencion(_sql.jd.contri, entre_a, entre_b))
        return pd.DataFrame(lista), df_pagina, tiene_previa, tiene_siguiente   
        
    def get_posible_ffpv(self, _sql, fila):
        '''    #version nueva AGOSTO 2023'''
        _sql.jd.tercero = fila["agente_retencion"]
        _sql.jd.autorizacion_tercero = fila["autorizacion"]
        _sql.jd.fecha_tercero = fila["fecha_emision"]
        _sql.jd.secuencia_tercero = fila["comprobante"]
        return self.db.get_vector(_sql.get_sql_posible_ffpv())
                        
    def get_periodos_parciales(self, fila, _sql):
        '''periodos parciales'''
        _sql.jd.periodo_inicial = fila["fecha_ini"]
        _sql.jd.periodo_final = fila["fecha_fin"]
        match(self.calculo_tipo):
            case 1:    
                df_retorno_papel = self.db.get_vector(_sql.get_sql_listado_explora_parcial())
            case 2:
                df_retorno_papel = self.db.get_vector(_sql.get_sql_listado_parcial())
            case 3:
                df_retorno_papel = self.db.get_vector(_sql.get_sql_administracion_parcial())

        if "fecha_ini" not in df_retorno_papel.columns and self.calculo_tipo in [1]:
            df_retorno_papel["fecha_ini"] = fila["fecha_ini"]
            df_retorno_papel["fecha_fin"] = fila["fecha_fin"]
        return df_retorno_papel     

    def get_retenciones_lr(self, _sql):
        '''retenciones en general'''
        df_final = pd.DataFrame()
        _periodo_inicial, _periodo_final = _sql.jd.periodo_inicial_org, _sql.jd.periodo_final_org
        with parallel_backend(backend="threading"):
            parallel = Parallel(verbose=0)
            resultados = parallel([delayed(self.get_periodos_parciales)(fila, _sql)  for ix, fila in self.df.iterrows()])
        if len(resultados) > 0:
            eliminado_vacios = []
            for xdf in resultados:
                if not xdf.empty:
                    eliminado_vacios.append(xdf)
            if len(eliminado_vacios)>0:
                df_final = pd.concat(eliminado_vacios)    

        _sql.jd.periodo_inicial = _periodo_inicial  
        _sql.jd.periodo_final = _periodo_final 
        return df_final    

    def get_periodos_semestrales(self, _sql):
        '''periodos semestrales'''
        df_posibles_periodos = self.db.get_vector(_sql.get_sql_adhesivos_parciales() )
        df_posibles_periodos["fecha_ini"] = ''
        df_posibles_periodos["fecha_fin"] = ''
        df_posibles_periodos["anio"] = df_posibles_periodos["anio_fiscal"].astype(int)
        df_posibles_periodos["mes"] = df_posibles_periodos["mes_fiscal"].astype(int)
        df_posibles_periodos["frecuencia"] = ''
        if not df_posibles_periodos.empty:
            df_posibles_periodos["anio_fiscal"] = df_posibles_periodos["anio_fiscal"].astype(int) 
            df_posibles_periodos["mes_fiscal"] = df_posibles_periodos["mes_fiscal"].astype(int) 
            df_posibles_periodos["codigo_impuesto"] = df_posibles_periodos["codigo_impuesto"].astype(int) 
            for ix, fila in df_posibles_periodos.iterrows():
                if fila["codigo_impuesto"] == 2021:
                    if fila["mes_fiscal"] == 12:
                        df_posibles_periodos.at[ix, "fecha_ini"] = str(fila["anio_fiscal"]) + '-07-01' 
                        df_posibles_periodos.at[ix, "fecha_fin"] = str(fila["anio_fiscal"]) + '-12-31'
                        df_posibles_periodos.at[ix, "frecuencia"] = str(fila["anio_fiscal"]) + "_12" 
 
                    if fila["mes_fiscal"] == 6:
                        df_posibles_periodos.at[ix, "fecha_ini"] = str(fila["anio_fiscal"]) + '-01-01' 
                        df_posibles_periodos.at[ix, "fecha_fin"] = str(fila["anio_fiscal"]) + '-06-30'
                        df_posibles_periodos.at[ix, "frecuencia"] = str(fila["anio_fiscal"]) + "_6" 

                elif fila["codigo_impuesto"] == 2011:
                    df_posibles_periodos.at[ ix, "fecha_ini"] = str(fila["anio_fiscal"]) + '-' + str(fila["mes_fiscal"]) + '-01'
                    input_dt = datetime(int(fila["anio_fiscal"]) , int(fila["mes_fiscal"]), 1)
                    resfecha = input_dt + relativedelta(day=31) 
                    df_posibles_periodos.at[ix, "fecha_fin"] = str(resfecha)
                    df_posibles_periodos.at[ix, "frecuencia"] = str(fila["anio_fiscal"]) + "_" + str(fila["mes_fiscal"])

        return df_posibles_periodos[['fecha_ini', 'fecha_fin', 'anio', 'mes', 'frecuencia', 'codigo_impuesto']]

    def get_retenciones_unificado(self, _sql):
        '''retenciones unificado'''
        self.df_listado_excel = pd.DataFrame()
        self.df_administracion = pd.DataFrame()
        self.calculo_tipo = 1
        self.df = _sql.jd.df_periodos_talves
        df_peri_valid_listado = self.get_retenciones_lr(_sql)
        if not df_peri_valid_listado.empty and not self.df.empty:
            self.df_periodos_listado = df_peri_valid_listado[df_peri_valid_listado["conteo"] > 0]
            self.df_periodos_listado_suma = df_peri_valid_listado["conteo"].sum()        
            self.calculo_tipo = 2
            self.df = self.df_periodos_listado
            self.df_listado_excel = self.get_retenciones_lr(_sql).reset_index()
            self.calculo_tipo = 3
            self.df = _sql.jd.df_periodos_talves
            self.df_administracion = self.get_retenciones_lr(_sql).reset_index()
        return self.df_periodos_listado_suma

    def get_limpieza_df(self, dfx):
        '''lipieza df'''
        if "index_x" in dfx.columns:
            dfx.drop("index_x", axis=1, inplace=True)
        if "index_y" in dfx.columns:
            dfx.drop("index_y", axis=1, inplace=True)
        if "_merge" in dfx.columns:
            dfx.drop("_merge", axis=1, inplace=True)
        if "level_0" in dfx.columns:
            dfx.drop("level_0", axis=1, inplace=True)
        if "index" in dfx.columns:
            dfx.drop("index", axis=1, inplace=True)

        return dfx
    
    def get_obtener_conjunto(self, df_listado,  df_admin, direccion, columnas):
        ''' inner es both  '''
        envase = 'both'
        df_pendientes = pd.merge(df_listado, df_admin, how=direccion,
                                 indicator=True,
                                 on=columnas, suffixes=('_x', '_y')).reset_index()    
        match direccion:
            case "left": envase = 'left_only' 
            case "right": envase = 'right_only' 

        if "level_0" in df_pendientes.columns:
            df_pendientes = df_pendientes.drop(['level_0'], axis=1)     

        df_pendientes = df_pendientes[df_pendientes["_merge"] == envase].reset_index()
        df_pendientes = self.get_limpieza_df(df_pendientes)
          
        if "autorizacion" in df_pendientes.columns:
            df_pendientes["autorizacion"] = df_pendientes["autorizacion"].astype(str)
            df_pendientes["autorizacion"] = df_pendientes["autorizacion"].replace(".0", '') 

        df_pendientes = df_pendientes.fillna(value=0)
        df_pendientes.drop_duplicates(inplace=True)
        return df_pendientes

    def get_obtener_conjunto_inta(self, df_listado,  df_admin, direccion, columnas):
        '''
            inner es both
        '''
        envase = 'both'
        df_pendientes = pd.merge(df_listado, df_admin, how=direccion, indicator=True, on=columnas, suffixes=('_x', '_y')).reset_index()    
        match direccion:
            case "left": envase = 'left_only' 
            case "right": envase = 'right_only' 
    
        df_pendientes = df_pendientes[df_pendientes["_merge"] == envase].reset_index()
        df_pendientes = self.get_limpieza_df(df_pendientes)
        df_pendientes.fillna(value=0, inplace=True)
        return df_pendientes

    def igualar_fase_1(self, df):
        '''igualado de columnas'''
        if "agente_retencion" in df.columns:
            df["agente_retencion"] = df["agente_retencion"].astype(str) 
        if "autorizacion" in df.columns:
            df["autorizacion"] = df["autorizacion"].astype(str) 
        if "contri" in df.columns:
            df["contri"] = df["contri"].astype(str) 
        if "fecha_emision" in df.columns:
            df["fecha_emision"] = df["fecha_emision"].astype(str) 
        if "comprobante" in df.columns:
            df["comprobante"] = df["comprobante"].astype(int) 
        if "valor_retenido" in df.columns:
            df["valor_retenido"] = df["valor_retenido"].astype('float64') 
        return df        
        
    def get_eliminar_index(self, df, columnas):
        '''elimininar indices'''
        for cols in columnas:
            if cols in df.columns:
                df = df.drop(cols, axis=1) 
        
        return df

    def agregar_numeracion(self, df, columnas):
        '''agreagra numeracion'''
        df = self.get_eliminar_index(df, ["index"])
        df = df.reset_index()
        df = df.sort_values(by=columnas)
        df = self.get_eliminar_index(df, ["index"])
        df["numeracion"] = df.groupby(columnas).cumcount().add(1)
        df["numeracion"] = df["numeracion"].astype(int)
        return df
    
    def depracion_x_y(self, df):
        '''se elimnan columnas adicionales de los crces'''
        df = self.get_eliminar_index(df, ["es_fantasma_x", "es_fallecido_x", "razon_social_x" , "numero_documento_sustento_x", "justificada", "numeracion"])

        if "numero_documento_sustento_y" in df.columns:
            df.rename(columns={'numero_documento_sustento_y': 'numero_documento_sustento'}, inplace=True)

        if "razon_social_y" in df.columns:
            df.rename(columns={'razon_social_y': 'razon_social'}, inplace=True)

        if "es_fantasma_y" in df.columns:
            df.rename(columns={'es_fantasma_y': 'es_fantasma'}, inplace=True)

        if "es_fallecido_y" in df.columns:
            df.rename(columns={'es_fallecido_y': 'es_fallecido'}, inplace=True)
        return df        

    def fx_clean_celda_vacia(self, x):
        '''limpia celdas'''
        if x is None:
            x = ''
        x = x.strip()
        if len(x) == 0:
            x = '0'
        else:
            x
        return x

    def get_amarres(self):
        '''get amarres'''
        pd.set_option('future.no_silent_downcasting', True)
        df_final = pd.DataFrame()
        df_pendientes_sin_solucion = pd.DataFrame()
        df_cruzan_z1 = pd.DataFrame()
        df_cruza_dups = pd.DataFrame()
        columnas_finales = ['contri', 'agente_retencion', 'razon_social', 'fecha_emision', 'autorizacion', 'comprobante',  'es_fantasma', 'es_fallecido',
                            'numero_documento_sustento', 'valor_retenido', 'valor_retenido_listado', 'valor_retenido_administracion', 'no_reporta']

        columnas_reconstruccion_admin = ['agente_retencion',	'contri',	'fecha_emision',	'comprobante',	'autorizacion',	'valor_retenido']

        if not self.df_listado_excel.empty and not self.df_administracion.empty:

            self.df_administracion['comprobante'] = self.df_administracion['comprobante'].apply(lambda x: self.fx_clean_celda_vacia(x))
            self.df_listado_excel['comprobante'] = self.df_listado_excel['comprobante'].astype(int) 
            self.df_administracion['comprobante'] = self.df_administracion['comprobante'].astype(int) 

            self.df_listado_excel['valor_retenido'] = self.df_listado_excel['valor_retenido'].apply(lambda x: self.db.uf.redondear(x, 2))
            self.df_administracion['valor_retenido'] = self.df_administracion['valor_retenido'].apply(lambda x: self.db.uf.redondear(x, 2))

            self.df_listado_excel = self.get_eliminar_index(self.df_listado_excel, ["indice"])
            self.df_listado_excel = self.df_listado_excel.round(2)
            self.df_administracion = self.df_administracion.round(2)
            df_administracion_original = self.df_administracion.copy()

            df_administracion_original = self.agregar_numeracion(df_administracion_original, columnas_reconstruccion_admin)
            interseccion_columnas_dups = ['contri', 'agente_retencion',  'autorizacion', 'comprobante',  'fecha_emision', 'valor_retenido']

            df_listado_sin_dups = self.df_listado_excel[interseccion_columnas_dups] 
            df_cine_A = df_listado_sin_dups[df_listado_sin_dups.duplicated(keep='first')].reset_index()
            df_cine_B = df_listado_sin_dups[df_listado_sin_dups.duplicated(keep=False)].reset_index()

            if len(df_cine_A.index) > 0 and "comprobante" in df_cine_A.columns:
                df_cine_A['comprobante'] = df_cine_A['comprobante'].astype(int) 

            if len(df_cine_B.index) > 0 and "comprobante" in df_cine_B.columns:
                df_cine_B['comprobante'] = df_cine_B['comprobante'].astype(int)

            if "index" in self.df_listado_excel.columns:
                self.df_listado_excel = self.df_listado_excel.drop('index', axis=1)

            if "index" in df_cine_A.columns:
                df_cine_A = df_cine_A.drop('index', axis=1)

            if "index" in df_cine_B.columns:
                df_cine_B = df_cine_B.drop('index', axis=1)

            df_sin_dups_ = self.df_listado_excel.merge(df_cine_A, on=interseccion_columnas_dups, how='outer', indicator=True)
            df_sin_dups = df_sin_dups_[df_sin_dups_['_merge'] == 'left_only']
            df_sin_dups = df_sin_dups.reset_index()            

            columnas_listado = ["agente_retencion", "autorizacion", "contri", "fecha_emision", "comprobante", "valor_retenido"]
            self.df_listado_excel = df_sin_dups[interseccion_columnas_dups]
            self.df_listado_excel["es_fantasma"] = ''
            self.df_listado_excel["es_fallecido"] = ''

            df_cine_B["es_fantasma"] = ''
            df_cine_B["es_fallecido"] = ''

            df_admin_futuras = pd.DataFrame()
            if not df_cine_B.empty:
                self.df_administracion = self.igualar_fase_1(self.df_administracion)
                df_cine_B = self.igualar_fase_1(df_cine_B)
                df_cine_B['comprobante'] = df_cine_B['comprobante'].astype(int)
                self.df_administracion['comprobante'] = self.df_administracion['comprobante'].astype(int)
                df_admin_futuras = self.get_obtener_conjunto(df_cine_B, self.df_administracion, "inner", columnas_listado)
                df_admin_futuras['comprobante'] = df_admin_futuras['comprobante'].astype(int)

            df_administracion_rs = self.df_administracion[["autorizacion", "razon_social"]]
            df_administracion_rs = df_administracion_rs.drop_duplicates()

            df_administracion_sin_cod_sus = self.df_administracion[interseccion_columnas_dups]

            self.df_listado_excel = self.df_listado_excel.drop_duplicates()
            self.df_administracion = df_administracion_sin_cod_sus.drop_duplicates()
            self.df_listado_excel.fillna(value=0, inplace=True)
            self.df_administracion.fillna(value=0, inplace=True)
            self.df_listado_excel = self.igualar_fase_1(self.df_listado_excel)
            self.df_administracion["comprobante"] = self.df_administracion["comprobante"].fillna(value=0)
            self.df_administracion = self.igualar_fase_1(self.df_administracion)
            df_administracion_original["comprobante"] = df_administracion_original["comprobante"].fillna(value=0)
            df_administracion_original = self.igualar_fase_1(df_administracion_original)

            self.df_listado_excel['comprobante'] = self.df_listado_excel['comprobante'].astype(int)
            self.df_administracion['comprobante'] = self.df_administracion['comprobante'].astype(int)
            df_administracion_original['comprobante'] = df_administracion_original['comprobante'].astype(int)

            lista_auts = pd.unique(self.df_listado_excel["autorizacion"])
            self.df_administracion = self.df_administracion[self.df_administracion["autorizacion"].isin(lista_auts)]

            if "index" in self.df_administracion.columns:
                self.df_administracion = self.df_administracion.drop('index', axis=1)

            df_cruzan_px = self.get_obtener_conjunto_inta(self.df_listado_excel, self.df_administracion, "inner", columnas_listado)
            df_cruzan_px = self.agregar_numeracion(df_cruzan_px, columnas_reconstruccion_admin)
            df_cruzan_px = self.get_obtener_conjunto(df_cruzan_px, df_administracion_original, "inner", columnas_reconstruccion_admin.append('numeracion'))
            df_cruzan_px["valor_retenido_listado"] = df_cruzan_px["valor_retenido"] 
            df_cruzan_px["valor_retenido_administracion"] = df_cruzan_px["valor_retenido"]
            df_cruzan_px["no_reporta"] = 0

            df_admin_pendientes = self.get_obtener_conjunto_inta(self.df_listado_excel, self.df_administracion, "right", columnas_listado)
            df_lista_pendientes = self.get_obtener_conjunto_inta(self.df_listado_excel, self.df_administracion, "left", columnas_listado)

            df_lista_pendientes["es_fantasma"] = ''
            df_lista_pendientes["es_fallecido"] = ''

            if "numero_documento_sustento" in df_lista_pendientes.columns.to_list():
                df_lista_pendientes.drop("numero_documento_sustento", axis=1, inplace=True)

            if "razon_social" in df_lista_pendientes.columns.to_list():
                df_lista_pendientes.drop("razon_social", axis=1, inplace=True)

            df_lista_pendientes_v = df_lista_pendientes.drop_duplicates(ignore_index=True)
            df_lista_pendientes_v = df_lista_pendientes_v.sort_values(by='autorizacion', ascending=False)

            if self.db.uf.pi.and_errante == 'E':
                df_admin_pendientes_n4 = df_admin_pendientes.copy()
                df_lista_pendientes_n4 = df_lista_pendientes.copy()
                columnas_listado_n4 = ["agente_retencion", "autorizacion", "contri", "fecha_emision",  "valor_retenido"]
                df_cruzan_z1 = pd.DataFrame()
                if not df_lista_pendientes.empty:
                    df_cruzan_z1 = self.get_obtener_conjunto_inta(df_lista_pendientes_n4, df_admin_pendientes_n4,  "inner", columnas_listado_n4)
                    df_admin_pendientes_n5 = self.get_obtener_conjunto_inta(df_lista_pendientes_n4, df_admin_pendientes_n4, "right", columnas_listado_n4)
                    df_lista_pendientes_n5 = self.get_obtener_conjunto_inta(df_lista_pendientes_n4, df_admin_pendientes_n4,  "left", columnas_listado_n4)
                    # 5 print(f"1034   {self.db.get_fecha_ymd()}" )

                    df_cruzan_z1["valor_retenido_listado"] = df_cruzan_z1["valor_retenido"] 
                    df_cruzan_z1["valor_retenido_administracion"] = df_cruzan_z1["valor_retenido"]
                    df_cruzan_z1["no_reporta"] = 0
                    df_admin_pendientes = df_admin_pendientes_n5.copy()
                    df_lista_pendientes = df_lista_pendientes_n5.copy()
                    eliminar = ["comprobante_x", "es_fantasma_x", "es_fallecido_x", "comprobante_y", "es_fantasma_y", "es_fallecido_y"]
                    for xol in eliminar:
                        if xol in df_cruzan_z1.columns:
                            if xol.endswith("_y"):
                                df_cruzan_z1.drop(xol, axis=1, inplace=True)
                            else:
                                df_cruzan_z1.rename(columns={xol: xol.replace("_x", "")}, inplace=True)

                        if xol in df_admin_pendientes.columns:
                            if xol.endswith("_x"):
                                df_admin_pendientes.drop(xol, axis=1, inplace=True)                   
                            else:
                                df_admin_pendientes.rename(columns={xol: xol.replace("_y", "")}, inplace=True)

                        if xol in df_lista_pendientes.columns:
                            if xol.endswith("_y"):
                                df_lista_pendientes.drop(xol, axis=1, inplace=True)            
                            else:
                                df_lista_pendientes.rename(columns={xol: xol.replace("_x", "")}, inplace=True)

                    df_cruzan_z1 = df_cruzan_z1.merge(df_administracion_rs, on="autorizacion", how="left").ffill(axis=1)  # .drop("price_x", axis=1)

            df_pendientes_sin_saldo_contenedor = pd.DataFrame()
            df_pendientes_sin_saldo = pd.DataFrame()
            df_cruzan_con_saldo = pd.DataFrame()
            if self.db.uf.pi.and_errante == 'F':
                df_pendientes_sin_solucion = df_lista_pendientes.copy()
                if not df_pendientes_sin_solucion.empty:
                    df_pendientes_sin_solucion["justificada"] = "NO"
                    df_pendientes_sin_solucion["valor_retenido_listado"] = df_pendientes_sin_solucion["valor_retenido"]
                    df_pendientes_sin_solucion["valor_retenido_administracion"] = 0.0
                    df_pendientes_sin_solucion["razon_social"] = ''
                    df_pendientes_sin_solucion["numero_documento_sustento"] = '0'
                    df_pendientes_sin_solucion["no_reporta"] = 0.0

            if self.db.uf.pi.and_errante == 'E':
                lista_pendientes_auts = pd.unique(df_lista_pendientes["autorizacion"]).tolist()
                df_admin_pendientes = df_admin_pendientes[df_admin_pendientes["autorizacion"].isin(lista_pendientes_auts)]
                admin_pendientes_auts = pd.unique(df_admin_pendientes["autorizacion"]).tolist()
                lista_pendientes_auts.sort()
                admin_pendientes_auts.sort()
                if lista_pendientes_auts == admin_pendientes_auts:
                    pendientes_auts = []
                else:
                    pendientes_auts = set(lista_pendientes_auts) - set(admin_pendientes_auts)

                df_pendientes_sin_solucion = df_lista_pendientes.copy()
                df_pendientes_sin_solucion = df_pendientes_sin_solucion[0:0]
                df_pendientes_sin_solucion = df_lista_pendientes[df_lista_pendientes["autorizacion"].isin(pendientes_auts)]
                lista_sin_soluciones = []

                if len(df_pendientes_sin_solucion.index) > 0:
                    df_pendientes_sin_solucion["justificada"] = "NO"
                    df_pendientes_sin_solucion["valor_retenido_listado"] = df_pendientes_sin_solucion["valor_retenido"]
                    df_pendientes_sin_solucion["valor_retenido_administracion"] = 0.0
                    df_pendientes_sin_solucion["razon_social"] = ''
                    df_pendientes_sin_solucion["numero_documento_sustento"] = '0'
                    df_pendientes_sin_solucion["no_reporta"] = 0.0                

                    lista_sin_soluciones = pd.unique(df_pendientes_sin_solucion["autorizacion"]).tolist()

                df_lista_pendientes_posibles = df_lista_pendientes[~(df_lista_pendientes["autorizacion"].isin(lista_sin_soluciones))]
                lista_procesados = []
                lista_pendientes_auts_l1 = []
                if not df_lista_pendientes_posibles.empty:
                    df_lista_pendientes_posibles["justificada"] = "NO"  
                    df_lista_pendientes_posibles["valor_retenido_listado"] = df_lista_pendientes_posibles["valor_retenido"]  
                    df_lista_pendientes_posibles["valor_retenido_administracion"] = 0.0
                    df_lista_pendientes_posibles["razon_social"] = ''
                    df_lista_pendientes_posibles["numero_documento_sustento"] = '0'
                    df_lista_pendientes_posibles["no_reporta"] = 0.0
                    lista_pendientes_auts_l1 = pd.unique(df_lista_pendientes_posibles["autorizacion"]).tolist()

                lista_admins = []
                if not df_cine_B.empty:
                    df_cine_B["justificada"] = "NO"  
                    df_cine_B["valor_retenido_listado"] = df_cine_B["valor_retenido"]  
                    df_cine_B["valor_retenido_administracion"] = 0.0
                    df_cine_B["razon_social"] = ''
                    df_cine_B["numero_documento_sustento"] = '0'
                    df_cine_B["no_reporta"] = 0.0

                df_admin_pendientes = self.igualar_fase_1(df_admin_pendientes)
                df_admin_futuras = self.igualar_fase_1(df_admin_futuras)                    

                if len(df_admin_pendientes.index)>0:
                    columnas_reconstruccion_admin = ['agente_retencion', 'contri', 'fecha_emision', 'comprobante', 'autorizacion', 'valor_retenido']                    
                    df_admin_pendientes['comprobante'] = df_admin_pendientes['comprobante'].astype(int) 

                    df_admin_pendientes = self.igualar_fase_1(df_admin_pendientes)
                    df_administracion_original = self.igualar_fase_1(df_administracion_original)

                    df_admin_pendientes = self.get_obtener_conjunto(df_admin_pendientes, df_administracion_original, "inner", columnas_reconstruccion_admin)
                    df_admin_pendientes = self.get_eliminar_index(df_admin_pendientes, ["numero_documento_sustento_x", "razon_social_x"])
                    if "numero_documento_sustento_y" in df_admin_pendientes.columns:
                        df_admin_pendientes.rename(columns={'numero_documento_sustento_y':'numero_documento_sustento'}, inplace=True)

                    if "razon_social_y" in df_admin_pendientes.columns:
                        df_admin_pendientes.rename(columns={'razon_social_y':'razon_social'}, inplace=True)

                if not df_admin_futuras.empty and not df_cine_B.empty:
                    columnas_reconstruccion_admin = ['agente_retencion', 'contri', 'fecha_emision', 'comprobante',	'autorizacion',	'valor_retenido']

                    df_admin_futuras = self.agregar_numeracion(df_admin_futuras, columnas_reconstruccion_admin)                
                    df_cine_B = self.agregar_numeracion(df_cine_B, columnas_reconstruccion_admin)                

                    df_admin_futuras = self.igualar_fase_1(df_admin_futuras)
                    df_cine_B = self.igualar_fase_1(df_cine_B)

                    columnas_reconstruccion_admin.append("numeracion")

                    df_cruza_dups = self.get_obtener_conjunto(df_cine_B, df_admin_futuras, "inner", columnas_reconstruccion_admin)
                    df_cruza_dups_pend = self.get_obtener_conjunto(df_cine_B, df_admin_futuras, "left", columnas_reconstruccion_admin)
               
                    df_cruza_dups = self.depracion_x_y(df_cruza_dups)
                    df_cruza_dups_pend = self.depracion_x_y(df_cruza_dups_pend)
                    df_cruza_dups["es_fantasma"] = ''
                    df_cruza_dups["es_fallecido"] = ''

                for retencion in lista_pendientes_auts_l1:
                    df_seccion_admin = df_admin_pendientes[df_admin_pendientes["autorizacion"] == retencion] 
                    df_lista_admin = df_lista_pendientes_posibles[df_lista_pendientes_posibles["autorizacion"] == retencion]
                    df_lista_admin = df_lista_admin.reset_index()
                    df_seccion_admin.sort_values(['valor_retenido'], ascending = [True], inplace=True)          
                    df_lista_admin.sort_values(['valor_retenido'], ascending = [True], inplace=True)                              
                    
                    df_lista_admin = df_lista_admin.reset_index()
                    df_seccion_admin = df_seccion_admin.reset_index()

                    nota_de_credito = 0
                    contabilizador = 0
                    lista_procesados = []
                    ix = 0
                    
                    for ix, fila in df_seccion_admin.iterrows():    
                        valor_para_descontar = self.db.uf.redondear(float(fila.valor_retenido), 2) + nota_de_credito          
                        razon_social = fila.razon_social
                        numero_documento_sustento = fila.numero_documento_sustento
                        contabilizador = 0
                        valor_retenido_administracion = 0
                        ix_jd = 0
                        for ix_jd, fila_satelite in df_lista_admin.iterrows():
                            if ix_jd not in lista_procesados:
                                valor_comprobante_listado = self.db.uf.redondear(float(fila_satelite.valor_retenido), 2)
                                contabilizador += self.db.uf.redondear(valor_comprobante_listado, 2)
                                contabilizador = self.db.uf.redondear(contabilizador, 2)
                                pagar = False
                                valor_justificado = 0
                                diferencia = 0
                                nota_de_credito = valor_para_descontar
                                if valor_para_descontar - valor_comprobante_listado >= 0:            
                                    pagar = True
                                    valor_para_descontar -= self.db.uf.redondear(valor_comprobante_listado, 2)
                                    valor_para_descontar = self.db.uf.redondear(valor_para_descontar, 2)
                                    valor_comprobante_listado = self.db.uf.redondear(valor_comprobante_listado, 2)
                                    valor_justificado = valor_comprobante_listado    
                                    valor_retenido_administracion = valor_comprobante_listado
                                else:
                                    if ((ix + 1 == len(df_seccion_admin)) or (ix_jd + 1 >= len(df_lista_admin)) and  (ix + 1 == len(df_seccion_admin))) and valor_para_descontar > 0:
                                        pagar = True
                                        valor_justificado = valor_para_descontar  
                                        diferencia = abs(valor_comprobante_listado - valor_para_descontar) 
                                        valor_para_descontar = 0
                                        valor_retenido_administracion = valor_justificado

                                valor_justificado = self.db.uf.redondear(valor_justificado, 2)
                                if pagar:
                                    df_lista_admin.at[ix_jd, "valor_retenido"] =  valor_justificado
                                    df_lista_admin.at[ix_jd, "valor_retenido_listado"] = valor_comprobante_listado
                                    df_lista_admin.at[ix_jd, "valor_retenido_administracion"] = valor_retenido_administracion
                                    df_lista_admin.at[ix_jd, "razon_social"] = str(razon_social)
                                    df_lista_admin.at[ix_jd, "numero_documento_sustento"] = str(numero_documento_sustento)
                                    df_lista_admin.at[ix_jd, "no_reporta"] = diferencia  
                                    df_lista_admin.at[ix_jd, "justificada"] = "SI"
                                    valor_comprobante_listado = self.db.uf.redondear(valor_comprobante_listado,2)
                                    valor_para_descontar = self.db.uf.redondear(valor_para_descontar,2)
                                    nota_de_credito = 0
                                    lista_procesados.append(int(ix_jd))

                                if valor_para_descontar < 0:
                                   break
               
                    lista_admins.append(df_lista_admin)

                if len(lista_admins) > 0:
                    df_pendientes_sin_saldo_contenedor = pd.concat(lista_admins)
                else:
                    df_pendientes_sin_saldo_contenedor = df_lista_pendientes_posibles 

                if not df_pendientes_sin_saldo_contenedor.empty:
                    df_pendientes_sin_saldo = df_pendientes_sin_saldo_contenedor[df_pendientes_sin_saldo_contenedor["justificada"] == 'NO']
                    df_pendientes_sin_saldo["valor_retenido_listado"] = df_pendientes_sin_saldo["valor_retenido"] 
                    df_cruzan_con_saldo = df_pendientes_sin_saldo_contenedor[df_pendientes_sin_saldo_contenedor["justificada"] == 'SI']

            df_pendientes = pd.DataFrame()
            if not df_pendientes_sin_saldo.empty and not df_pendientes_sin_solucion.empty:
                df_pendientes = pd.concat([df_pendientes_sin_saldo, df_pendientes_sin_solucion])

            if not df_pendientes_sin_saldo.empty and df_pendientes.empty and df_pendientes_sin_solucion.empty:
                df_pendientes = df_pendientes_sin_saldo

            if not df_pendientes_sin_solucion.empty and df_pendientes.empty and df_pendientes_sin_saldo.empty:
                df_pendientes = df_pendientes_sin_solucion

            if not df_pendientes.empty:
                df_pendientes = df_pendientes[columnas_finales]
                df_pendientes["cruza"] = 'no'

            df_final_cruzan = pd.DataFrame()

            if not df_cruzan_px.empty:
                df_cruzan_px = df_cruzan_px[columnas_finales]            

            if not df_cruzan_px.empty and not df_cruzan_con_saldo.empty:  
                df_cruzan_con_saldo = df_cruzan_con_saldo[columnas_finales]
                df_final_cruzan = pd.concat([df_cruzan_px, df_cruzan_con_saldo])

            if df_final_cruzan.empty and not df_cruzan_px.empty:  
                df_final_cruzan = df_cruzan_px

            if df_final_cruzan.empty and df_cruzan_px.empty and not df_cruzan_con_saldo.empty:  
                df_cruzan_con_saldo = df_cruzan_con_saldo[columnas_finales]
                df_final_cruzan = df_cruzan_con_saldo

            if not df_cruzan_z1.empty and not df_final_cruzan.empty: 
                df_final_cruzan = df_final_cruzan.fillna(0)
                df_final_cruzan = pd.concat([df_cruzan_z1, df_final_cruzan])
                
            elif not df_cruzan_z1.empty and df_final_cruzan.empty:  
                df_cruzan_z1 = df_cruzan_z1.fillna(0)
                df_final_cruzan = df_cruzan_z1

            if not df_final_cruzan.empty and not df_cruza_dups.empty:
                df_final_cruzan = pd.concat([df_final_cruzan, df_cruza_dups]).reset_index()

            if df_final_cruzan.empty and not df_cruza_dups.empty:
                df_final_cruzan = df_cruza_dups
                
            if not df_final_cruzan.empty:
                df_final_cruzan["cruza"] = 'si'

            df_final = pd.DataFrame() 

            if not df_pendientes.empty and self.db.uf.pi.and_errante == 'E':
                df_pendientes = df_pendientes.merge(df_administracion_rs,
                                                    on="autorizacion",
                                                    how="left").ffill(axis=1)

                if "razon_social_y" in df_pendientes.columns:
                    df_pendientes.rename(columns={'razon_social_y':'razon_social'}, inplace = True)

                df_pendientes = self.get_eliminar_index(df_pendientes, ["razon_social_x"])

            if not df_final_cruzan.empty and not df_pendientes.empty:
                df_final = pd.concat([df_final_cruzan, df_pendientes]).reset_index()

            if not df_final_cruzan.empty and df_final.empty:
                df_final = df_final_cruzan

            if not df_pendientes.empty and df_final.empty:
                df_final = df_pendientes

            if not df_final.empty:
                df_final = df_final.fillna(0)                
                df_final['diferencia'] = df_final.apply(lambda row : self.get_calculo_diferencia(row['cruza'], row['valor_retenido_listado'], row['valor_retenido_administracion']), axis = 1)
                df_final["es_fantasma"] = numpy.where(df_final["es_fantasma"] == "0", '', df_final["es_fantasma"])
                df_final["es_fallecido"] = numpy.where(df_final["es_fallecido"] == "0", '', df_final["es_fallecido"])
                df_final["razon_social"] = numpy.where(df_final["razon_social"] == "0", '', df_final["razon_social"])
                df_final.fillna(value='', inplace=True)
                df_final["conclusion"] = numpy.where( (df_final["es_fantasma"] == '') & (df_final["es_fallecido"] == '') & (df_final["cruza"] == "si") , 'si', 'no')
                df_final = df_final.drop_duplicates()
        elif not self.df_listado_excel.empty and self.df_administracion.empty:                  
            self.df_listado_excel["valor_retenido"] = self.df_listado_excel["valor_retenido"].round(2)
            df_final = self.df_listado_excel.copy()
            df_final = df_final.fillna(0)
            df_final["valor_retenido_listado"] = df_final["valor_retenido"]  
            df_final["valor_retenido_administracion"] = 0.0
            df_final["razon_social"] = ''
            df_final["numero_documento_sustento"] = '0'
            df_final["no_reporta"] = 0.0
            df_final = self.get_eliminar_index(df_final, ["index", "indice"])
            df_final['diferencia'] = 0
            df_final["cruza"] = 'no'
            df_final["es_fantasma"] = numpy.where(df_final["es_fantasma"] == "0", '', df_final["es_fantasma"])
            df_final["es_fallecido"] = numpy.where(df_final["es_fallecido"] == "0", '', df_final["es_fallecido"])
            df_final["razon_social"] = numpy.where(df_final["razon_social"] == "0", '', df_final["razon_social"])
            df_final.fillna(value='',inplace=True)
            df_final["conclusion"] = numpy.where( (df_final["es_fantasma"] == '') & (df_final["es_fallecido"] == '') & (df_final["cruza"] == "si") , 'si', 'no')
            df_final = df_final.drop_duplicates()
        return df_final
    
    def get_calculo_valor_retenido(self, val_listado, val_admin):
        '''case when  a.valor_retenido > cur.valor_retenido   then   
            cur.valor_retenido  else
            case when  cur.valor_retenido > a.valor_retenido then 
            a.valor_retenido else cur.valor_retenido  end
            end valor_retenido        '''
        val_retenido = 0
        if val_listado > val_admin:
            val_retenido = self.db.uf.redondear(float(val_admin), 2)
        elif val_admin >= val_listado:
            val_retenido = self.db.uf.redondear(float(val_listado), 2)
             
        return self.db.uf.redondear(float(val_retenido), 2)
    
    def get_calculo_no_reporta(self, val_listado, val_admin):
        '''calculo no reporta'''
        val_retenido = 0
        if val_listado == val_admin:
            val_retenido = 0
        elif val_listado > val_admin:
            val_retenido = self.db.uf.redondear(self.db.uf.redondear(float(val_listado), 2) - self.db.uf.redondear(float(val_admin), 2), 2)
        return self.db.uf.redondear(float(val_retenido), 2)
    
    def get_calculo_diferencia(self, cruza, val_listado, val_admin) :
        '''calculo diferencia'''
        val_retenido = 0
        if cruza == 'si':
            if val_listado - val_admin < 0:
                val_retenido = 0
            else:
                val_retenido = self.db.uf.redondear(self.db.uf.redondear(float(val_listado), 2) - self.db.uf.redondear(float(val_admin), 2), 2)
        return self.db.uf.redondear(float(val_retenido), 2)

    # octubre 2024

    def get_rangos(self, codigo_impuesto, mes):
        '''get rango octubre 2024'''
        if codigo_impuesto == 2011:
            return mes, mes
        if codigo_impuesto == 2021:
            if mes == 6:
                return 1, 6

            if mes == 12:
                return 7, 12

    def obtener_campo_unico(self, df, clave):
        '''obtencion de campo unico'''
        df[clave] = df[clave].astype(str)
        clave_a = df[clave].unique().tolist()
        valor_clave = ''.join(clave_a)
        return valor_clave

    def get_periodo_cercano(self, df_declarado, anio, mes):
        '''octubre 2024 '''
        df_declarado.anio = df_declarado.anio.astype(int)
        df_declarado.mes = df_declarado.mes.astype(int)
        df_declarado.minimo = df_declarado.minimo.astype(int)
        df_declarado.maximo = df_declarado.maximo.astype(int)
        df_test = df_declarado[(df_declarado.anio == anio) & (df_declarado.mes == mes)]
        if df_test.empty:
            df_test = df_declarado[(df_declarado.anio.astype(int) == anio)]
            df_test = df_test[(mes >= df_test.minimo) & (mes <= df_test.maximo)]
        anio_dev = self.obtener_campo_unico(df_test, 'anio')
        mes_dev = self.obtener_campo_unico(df_test, 'mes')

        return str(anio_dev).zfill(4) + "-" + str(mes_dev).zfill(2)

    # fin octubre 2024

    def buscar_duplicados_particular(self, df_declarados):
        '''dupliucados particular'''
        df_duplicado = pd.DataFrame()
        df_no_duplicado = pd.DataFrame()
        interseccion_columnas = ['contri', 'agente_retencion',
                                 'autorizacion', 'comprobante',
                                 'fecha_emision', 'valor_retenido']

        df_pre_cine = self.df_para_duplicados[interseccion_columnas].reset_index() 
        df_pre_cine["contri"] = df_pre_cine["contri"].astype(str)
        df_pre_cine["agente_retencion"] = df_pre_cine["agente_retencion"].astype(str)
        df_pre_cine["autorizacion"] = df_pre_cine["autorizacion"].astype(str)
        df_pre_cine["comprobante"] = df_pre_cine["comprobante"].astype(int)
        df_pre_cine["fecha_emision"] = df_pre_cine["fecha_emision"].astype(str)
        df_pre_cine["valor_retenido"] = df_pre_cine["valor_retenido"].astype(float)
        df_pre_cine.drop({'index'}, axis=1, inplace=True)
        df_duplicado = df_pre_cine.copy()
        df_duplicado['valor_retencion'] = df_duplicado['valor_retenido']
        df_duplicado = df_duplicado[0:0].copy(deep=True)
        df_cine = df_pre_cine.copy()
        df_cine = df_cine[df_cine.duplicated(keep='first')].reset_index()
        df_cine = df_cine.drop_duplicates(subset=interseccion_columnas)
        df_cine.drop({'index'}, axis=1, inplace=True)
        df_cine_restaurado = df_pre_cine.copy()
        df_cine_restaurado = df_pre_cine[df_pre_cine.duplicated(keep=False)].reset_index()

        # print(f"df_cine {df_cine}")
        # print(f"df_cine_restaurado {df_cine_restaurado}")

        if "index" in df_cine_restaurado.columns:
            df_cine_restaurado.drop({'index'}, axis=1, inplace=True)
        if "level_0" in df_cine_restaurado.columns:
            df_cine_restaurado.drop({'level_0'}, axis=1, inplace=True)

        interseccion_columnas = ['contri', 'agente_retencion', 'autorizacion', 'fecha_emision', 'numeracion']
        lista_dups = []
        lista_no_dups = []
        for ix, fila in df_cine.iterrows():
            contri = fila["contri"]             
            agente_retencion = fila["agente_retencion"]             
            aut = fila["autorizacion"] 
            comprobante = fila["comprobante"] 
            fecha_emision = str(fila["fecha_emision"])[:10] 
            valor_retenido = self.db.uf.redondear(float(fila["valor_retenido"]), 2) 

            df_cine_restaurado["fecha_emision"] = df_cine_restaurado["fecha_emision"].astype(str)
            df_cine_restaurado["fecha_emision"] = df_cine_restaurado['fecha_emision'].str[:10]    
            df_requeridas = df_cine_restaurado[df_cine_restaurado["autorizacion"] == aut]

            # print(f"df_cine_restaurado {df_cine_restaurado}")

            num_requeridas = len(df_requeridas.index)
            # df_posible_duplicado = pd.DataFrame()

            # print(self.cn.get_sql_duplicados(contri, agente_retencion, aut, comprobante, fecha_emision, valor_retenido))

            df_disponible_grupo = self.db.get_vector(self.cn.get_sql_duplicados(contri, agente_retencion, aut, comprobante, fecha_emision, valor_retenido))

            # print(f"df_disponible_grupo {df_disponible_grupo}")

            df_cine_restaurado_focal = df_cine_restaurado[(df_cine_restaurado["contri"].astype(str) == contri)  & (df_cine_restaurado["agente_retencion"].astype(str) == agente_retencion) & 
                                                          (df_cine_restaurado["autorizacion"].astype(str) == aut) & (df_cine_restaurado["comprobante"].astype(int) == comprobante) & 
                                                          (df_cine_restaurado["fecha_emision"].astype(str) == fecha_emision) & (df_cine_restaurado["valor_retenido"].astype(float) == valor_retenido)]
           
            if "index" in df_disponible_grupo.columns:
                df_disponible_grupo.drop({'index'}, axis=1, inplace=True)

            num_disponibles = len(df_disponible_grupo.index)

            # print(f" -->  num_disponibles {num_disponibles} num_requeridas {num_requeridas} ")

            if num_disponibles > 0 and num_requeridas > 0:
                df_posibles_con_sustentos = df_disponible_grupo[['contri', 'agente_retencion', 'autorizacion', 'comprobante', 'fecha_emision', 'valor_retenido', 'numero_documento_sustento']].reset_index()
                if "index" in df_posibles_con_sustentos.columns:
                    df_posibles_con_sustentos.drop({'index'}, axis=1, inplace=True)

                df_posibles_con_sustentos["numeracion"] = df_posibles_con_sustentos.groupby(['autorizacion', 'valor_retenido', 'fecha_emision'])['comprobante'].cumcount() + 1 
                df_cine_restaurado_focal["numeracion"] = df_cine_restaurado_focal.groupby(['autorizacion', 'valor_retenido', 'fecha_emision',])['comprobante'].cumcount() + 1

                interseccion_columnas = ['contri', 'agente_retencion', 'autorizacion', 'comprobante', 'fecha_emision', 'valor_retenido', 'numeracion']

                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"contri", str)    
                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"agente_retencion", str)    
                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"autorizacion", str)    
                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"fecha_emision", str)    
                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"comprobante", str)        
                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"numeracion", str)        
                self.igualar_a_dos(df_cine_restaurado_focal, df_posibles_con_sustentos,"valor_retenido", str)        

                df_posibles_con_sustentos.sort_values(['autorizacion', 'valor_retenido', 'fecha_emision', 'numeracion'], ascending=[True, True, True, True], inplace=True, ignore_index=True)
                df_cine_restaurado_focal.sort_values(['autorizacion', 'valor_retenido', 'fecha_emision', 'numeracion'], ascending=[True, True, True, True], inplace=True, ignore_index=True)

                df_posible_no_duplicado = self.get_obtener_conjunto_inta(df_cine_restaurado_focal, df_posibles_con_sustentos, "inner", interseccion_columnas)   
                df_posible_duplicado_derecha = self.get_obtener_conjunto_inta(df_cine_restaurado_focal, df_posibles_con_sustentos, "right", interseccion_columnas)   
                df_posible_duplicado_left = self.get_obtener_conjunto_inta(df_cine_restaurado_focal, df_posibles_con_sustentos, "left", interseccion_columnas)   
                posibles_duplicados = len(df_posible_duplicado_left.index)

                # print(f"1416 df_posible_no_duplicado {df_posible_no_duplicado}")
                # print(f"1417 df_posible_duplicado_derecha {df_posible_duplicado_derecha}")
                # print(f"1418 df_posible_duplicado_left   {df_posible_duplicado_left}")
                # print(f"1419 posibles_duplicados {posibles_duplicados} <= num_requeridas  {num_requeridas}")

                if posibles_duplicados <= num_requeridas:
                    df_cine_restaurado_exp = df_cine_restaurado.copy()
                    df_cine_restaurado_exp = df_cine_restaurado_exp[['contri', 'agente_retencion',  'autorizacion', 'comprobante',  'fecha_emision', 'valor_retenido']]
                    if "index" in df_cine_restaurado_exp.columns:
                        df_cine_restaurado_exp.drop({'index'}, axis=1, inplace=True)
                    if not df_posible_duplicado_left.empty:
                        lista_dups.append(df_posible_duplicado_left)

                if not df_posible_no_duplicado.empty:
                    lista_no_dups.append(df_posible_no_duplicado)

        if len(lista_dups) > 0:
            df_duplicado = pd.concat(lista_dups)

        if len(lista_no_dups) > 0:
            df_no_duplicado = pd.concat(lista_no_dups)

        # print(f"1482 df_duplicado \n {df_duplicado}")
        # print(f"1483  df_no_duplicado \n {df_no_duplicado}")
        # print(f"1484  df_cine_restaurado \n {df_cine_restaurado}")
        # print(f"1485  df_cine \n {df_cine}")

        if df_duplicado.empty and df_no_duplicado.empty and not df_cine_restaurado.empty:
            df_duplicado = df_cine_restaurado
            df_duplicado["valor_retencion"] = df_duplicado["valor_retenido"]

        if not df_duplicado.empty: 
            df_duplicado = self.procesa_grupos_aparentes(df_duplicado, df_declarados)
            print(f" {self.db.uf.GREEN} df_duplicado \n {df_duplicado} {self.db.uf.RESET}")

        if not df_no_duplicado.empty:
            df_no_duplicado = self.procesa_grupos_aparentes(df_no_duplicado, df_declarados)
            df_no_duplicado["duplicado"] = 'no'

        # print(f"1493 df_duplicado \n {df_duplicado}")
        # print(f"1494  df_no_duplicado \n {df_no_duplicado}")

        return df_duplicado, df_no_duplicado                    

    def procesa_grupos_aparentes(self, df_duplicado, df_declarados):
        '''procesa grupos aparentes'''
        if not df_duplicado.empty:
            df_duplicado["duplicado"] = 'si'
            df_duplicado.drop_duplicates(inplace=True, ignore_index=True)
            df_duplicado['fecha_emision'] = pd.to_datetime(df_duplicado['fecha_emision'])
            df_duplicado['anio'] = df_duplicado['fecha_emision'].dt.year
            df_duplicado['mes'] = df_duplicado['fecha_emision'].dt.month        

            if not df_duplicado.empty:
                df_impuestos = df_declarados[["anio", "mes", "codigo_impuesto"]]

                df_duplicado['anio'] = df_duplicado['anio'].astype(int)
                df_duplicado['mes'] = df_duplicado['mes'].astype(int)        

                df_impuestos['anio'] = df_impuestos['anio'].astype(int)
                df_impuestos['mes'] = df_impuestos['mes'].astype(int)        
                
                df_impuestos["periodo"] = df_impuestos["anio"].astype(str).str.zfill(4) + "-" + df_impuestos["mes"].astype(str).str.zfill(2)

                df_impuestos[["minimo", "maximo"]] = df_impuestos.apply(lambda fila: self.get_rangos(int(fila["codigo_impuesto"]), int(fila["mes"])), axis=1).to_list()
                df_duplicado["periodo"] = df_duplicado.apply(lambda fila: self.get_periodo_cercano(df_impuestos, int(fila["anio"]), int(fila["mes"])), axis=1)

                df_duplicado = self.get_obtener_conjunto(df_duplicado, df_impuestos, "inner", ["periodo"])   

                df_duplicado.rename(columns={'anio_x': 'anio'}, inplace=True)
                df_duplicado.rename(columns={'mes_x': 'mes'}, inplace=True)

                df_duplicado.drop("anio_y", axis=1, inplace=True)
                df_duplicado.drop("mes_y", axis=1, inplace=True)

                df_duplicado["frecuencia"] = df_duplicado["anio"].astype(str) + "_" + df_duplicado["mes"].astype(str)  
                df_duplicado["fecha_emision"] = df_duplicado["fecha_emision"].astype(str)
                df_duplicado["fecha_emision"] = df_duplicado["fecha_emision"] + ' '
        
        if "valor_retencion" not in df_duplicado.columns:
            df_duplicado['valor_retencion'] = df_duplicado['valor_retenido']
            df_duplicado['valor_retencion'] = df_duplicado['valor_retenido'].astype(float)

        #         print(f" {self.db.uf.GREEN} df_duplicado \n {df_duplicado} {self.db.uf.RESET}")
        return df_duplicado

    def igualar_a_dos(self, df_a, df_b, columna, tipo):
        '''igualar a 2'''
        df_a[columna] = df_a[columna].astype(str)
        df_b[columna] = df_b[columna].astype(str) 
        df_a[columna]= df_a[columna].str.strip()
        df_b[columna]= df_b[columna].str.strip()
        df_a[columna] = df_a[columna].astype(tipo)
        df_b[columna] = df_b[columna].astype(tipo) 

    def fx_agente_retencion(self, df):
        '''agente de retencion'''
        if not self.df_listado_excel.empty and 'agente_retencion' in self.df_listado_excel.columns: 
            self.df_listado_excel['agente_retencion'] = self.df_listado_excel['agente_retencion'].astype(str)
            self.df_listado_excel['agente_retencion'] = self.df_listado_excel['agente_retencion'].str.strip()
            self.df_listado_excel['agente_retencion'] = self.df_listado_excel['agente_retencion'].str.replace(".0", '')
            self.df_listado_excel['agente_retencion'] = self.df_listado_excel['agente_retencion'].str.replace(".", '')            
            self.df_listado_excel['agente_retencion'] = self.df_listado_excel['agente_retencion'].apply(lambda x: x.zfill(13))
        return df

    def buscando_retenciones(self, df_declarados,  _sql):
        '''buscando retenciones'''
        start_tiempo = timer()
        df_electronicas = pd.DataFrame()
        df_cine = pd.DataFrame()
        df_fisicas = pd.DataFrame()
        df_retenciones = pd.DataFrame()
        self.db.uf.pi.and_errante = 'E'
        _sql.jd.and_errante = 'E'
        self.db.uf.pi.usuario = _sql.jd.usuario  
        num_cargadas_excel = self.get_retenciones_unificado(_sql)
        self.df_listado_excel = self.fx_agente_retencion(self.df_listado_excel)
        df_electronicas_ = self.df_listado_excel
        num_elecs, num_fisis = 0, 0
        if num_cargadas_excel > 0:
            df_electronicas = self.get_amarres()
            num_elecs = len(self.df_listado_excel.index)
            if not df_electronicas.empty:
                df_electronicas["es_ffpv"] = ''
                num_elecs = self.df_periodos_listado_suma
           
        _sql.jd.and_errante = 'F'
        # _sql.jd.usuario =  _sql.jd.usuario
        num_cargadas_excel = self.get_retenciones_unificado(_sql)
        self.df_listado_excel = self.fx_agente_retencion(self.df_listado_excel)        
        df_fisicas_ = self.df_listado_excel
        if num_cargadas_excel > 0:
            df_fisicas = self.get_amarres()
            num_fisis = len(self.df_listado_excel.index)
            if not df_fisicas.empty:
                df_fisicas.fillna(value='0', inplace=True)
                df_fisicas["comprobante"] = df_fisicas["comprobante"].astype(int)
                df_fisicas["autorizacion"] = df_fisicas["autorizacion"].astype(str)
                df_fisicas["agente_retencion"] = df_fisicas["agente_retencion"].astype(str)
                df_fisicas["fecha_emision"] = df_fisicas["fecha_emision"].astype(str)
                df_ffpv = pd.DataFrame()
                with parallel_backend(backend="threading"):
                    parallel = Parallel(verbose=0)
                    resultados = parallel([delayed(self.get_posible_ffpv)(_sql, fila)  for ix,fila in df_fisicas.iterrows()])
                if len(resultados) > 0:
                    df_ffpv = pd.concat(resultados).reset_index()    
                    df_ffpv["comprobante"] = df_ffpv["comprobante"].astype(int)
                    df_ffpv["autorizacion"] = df_ffpv["autorizacion"].astype(str)
                    df_ffpv["agente_retencion"] = df_ffpv["agente_retencion"].astype(str)
                    df_ffpv["fecha_emision"] = df_ffpv["fecha_emision"].astype(str)

                if "index" in df_fisicas:
                    df_fisicas.drop({'index'}, axis=1, inplace=True)

                if "index" in df_ffpv:
                    df_ffpv.drop({'index'}, axis=1, inplace=True)

                df_cruzan_ffpvs = self.get_obtener_conjunto(df_fisicas, df_ffpv, "inner", ['autorizacion','agente_retencion','comprobante','fecha_emision'])
                df_no_cruzan_ffpvs = self.get_obtener_conjunto(df_fisicas, df_ffpv, "left", ['autorizacion','agente_retencion','comprobante','fecha_emision'])

                df_fisicas = pd.concat([df_no_cruzan_ffpvs, df_cruzan_ffpvs]).reset_index()
                df_fisicas["es_ffpv"] = numpy.where(df_fisicas["es_ffpv"] == "0", 'si', df_fisicas["es_ffpv"])           

        if len(df_electronicas.index) > 0 or len(df_fisicas.index) > 0:

            if "level_0" in df_electronicas:
                df_electronicas.drop({'level_0'}, axis=1, inplace=True)            

            if "level_0" in df_fisicas:
                df_fisicas.drop({'level_0'}, axis=1, inplace=True)            

            df_retenciones = pd.concat([df_electronicas, df_fisicas]).reset_index()
            self.df_listado_completo = pd.concat([df_electronicas_, df_fisicas_]).reset_index()
            self.df_listado_completo.drop({'index'}, axis=1, inplace=True)

            self.df_para_duplicados = self.df_listado_completo            
            if len(df_retenciones.index)> len(self.df_listado_completo):
                self.df_para_duplicados = df_retenciones

            if len(df_retenciones.index) != len(self.df_listado_completo):
 
                if "level_0" in df_retenciones:
                    df_retenciones.drop({'level_0'},axis=1, inplace=True)

                if "level_0" in self.df_listado_completo:
                    self.df_listado_completo.drop({'level_0'},axis=1, inplace=True)

            if "index" in df_retenciones.columns: 
                df_retenciones.drop({'index'}, axis=1, inplace=True)

            if "level_0" in df_retenciones.columns: 
                df_retenciones.drop({'level_0'}, axis=1, inplace=True)

            df_retenciones["cruza"] = numpy.where((df_retenciones["es_ffpv"] == "si"), 'no', df_retenciones["cruza"])
            df_retenciones["valor_retenido"] = numpy.where((df_retenciones["cruza"] == "no"), 0.0, df_retenciones["valor_retenido"])
            df_retenciones["conclusion"] = numpy.where((df_retenciones["conclusion"] == "no") | (df_retenciones["cruza"] == "no") | (df_retenciones["es_ffpv"] == "si"), 'no', "si")
            df_retenciones["fecha_emi_retencion"] = df_retenciones["fecha_emision"]
            df_retenciones["fecha_emi_ret"] = df_retenciones["fecha_emision"]
            df_retenciones["ruc_contrib_informan"] = df_retenciones["agente_retencion"]
            df_retenciones["secuencial_retencion"] = df_retenciones["comprobante"]
            df_retenciones["numero_documento"] = df_retenciones["contri"]
            df_retenciones["valor_retencion"] = df_retenciones["valor_retenido"]
            df_retenciones['fecha_emi_ret'] = pd.to_datetime(df_retenciones['fecha_emi_ret'])
            df_retenciones['anio'] = df_retenciones['fecha_emi_ret'].dt.year
            df_retenciones['mes'] = df_retenciones['fecha_emi_ret'].dt.month
            self.df_resultado_aparente = df_retenciones.copy()
            df_cine, df_no_cine = self.buscar_duplicados_particular(df_declarados)
            df_retenciones.drop(['fecha_emision','agente_retencion','contri','valor_retenido','comprobante'],inplace=True,axis=1)

            # print(f"df_cine \n {df_cine}")
            # print(f"df_cine cols \n {df_cine.columns}")            
            # print(f"df_no_cine \n {df_no_cine}")
            # print(f"df_no_cine cols \n {df_no_cine.columns}")
            # print(f"df_retenciones \n {df_retenciones}")
            # print(f"df_retenciones cols \n {df_retenciones.columns}")
        end_tiempo = timer()
        
        _sql.jd.time_informe_revision = str(timedelta(seconds=end_tiempo-start_tiempo))
        _sql.jd.num_retenciones_proce = int(len(df_retenciones.index))
        _sql.jd.num_retenciones_dupli = int(len(df_cine.index))
        _sql.jd.num_retenciones_excel = int(num_elecs + num_fisis)
        _sql.jd.df = ''
        session.modified = True
        print(f"{self.db.uf.MAGENTA} _______________________________________________________ IR en  {self.db.get_fecha_ymd()}  {self.db.uf.RESET} ")
        print(f"""{self.db.uf.BLUE} __________ Acceso {_sql.jd.num_acceso}  Procesado en: {_sql.jd.time_informe_revision} retenciones calculadas    
                    {len(df_retenciones.index)}    duplicados {len(df_cine.index)}  de un listado de {num_elecs+num_fisis}  {self.db.uf.RESET} """)    
        return df_retenciones, df_cine, _sql

    def get_resumen_compras(self, v_usuario):
        '''informe de revision
            # 01-AGO-2023 - Cambio con hilos
            # 14-FEB-20224 - Se agregan variables localles '''
        len_paginado = 0
        len_pagina = 0
        enlace = ''
        enlace_periodos = ''
        df_informe_exp = []
        self.db.uf.pi.usuario = v_usuario
        _jd = self.db.uf.pi

        _sql = RetencionesQ.Terceros(_jd)
        _sql.jd.fecha_hoy = self.db.get_fecha_ymd()
        _sql.jd.procedencia == 'interna'

        _his = self.db.uf.his
        _his.numeros_semestrales_subjetivas = self.db.get_scalar(_sql.numero_declas_semestrales())
        df_declarados = self.db.get_df_from_pg(_sql.get_sql_declaraciones_validas_inf())
        df_out_range = self.db.get_vector(_sql.get_sql_listado_out_range())
        df_retorno_papel, self.df_duplicados_encontrados, _sql = self.buscando_retenciones(df_declarados, _sql)
        enlace_descartes = ''
        df_duplicados = pd.DataFrame()
        df_ingresado_exp = pd.DataFrame()
        df_longitudes_exp = []
        df_paginado = []
        len_todos = 0
        listanovedades = []
        df_pagina = []
        self.tipo_frecuencia = "MENSUAL"
        if not df_retorno_papel.empty:
            df_retorno_papel['valor_retencion'] = df_retorno_papel['valor_retencion'].apply(lambda x: self.db.uf.redondear(x,2))
            df_retorno_papel["anio"] = df_retorno_papel["anio"].astype(int)
            df_retorno_papel["mes"] = df_retorno_papel["mes"].astype(int)     
            df_retorno_papel.sort_values(['anio', 'mes','fecha_emi_retencion'], ascending = [True, True, True], inplace=True)            
            df_informe, df_ingresados, df_longitudes, df_duplicados, df_conteo_dups, _his = self.get_crear_estadistica(df_retorno_papel, df_declarados, _sql, _his)            
            df_informe = df_informe.fillna(0)
            df_informe = df_informe.drop_duplicates()
            if not df_conteo_dups.empty:
                df_retorno_papel = df_retorno_papel.merge(df_conteo_dups, how='left', on=["autorizacion"])
                df_retorno_papel['conteo'] = df_retorno_papel['conteo'].fillna(0)                
            else:
                df_retorno_papel['conteo'] = 0
            df_informe["duplicados"] = df_informe["duplicados"].astype(int) 
            df_longitudes["longitudes"] = df_longitudes["longitudes"].astype(int) 
            df_informe.sort_values(['anio', 'mes'], ascending = [True, True], inplace=True)            
            df_informe_exp, len_informe = self.db.get_lorentz(df_informe)
            df_ingresado_exp, len_ingresado = self.db.get_lorentz(df_ingresados)
            df_longitudes_exp, len_ingresado_longs = self.db.get_lorentz(df_longitudes)
            df_retorno_papel['valor_retencion'] = df_retorno_papel['valor_retencion'].fillna(0)
            df_retorno_papel['valor_retencion'] = df_retorno_papel['valor_retencion'].replace('', 0)
            df_retorno_grabar = df_retorno_papel.copy()
            _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
            _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_INFORME_RETENCION
            _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
            self.db.get_reseto_tabla_estandar_jd(_sql)            
            df_retorno_grabar = self.db.preparar_dataframe(df_retorno_grabar)   
            df_retorno_grabar = df_retorno_grabar.drop(['numero_documento'], axis=1)            
            if "frecuencia" in df_retorno_grabar.columns:
                df_retorno_grabar = df_retorno_grabar.drop('frecuencia', axis=1)    

            df_retorno_grabar['numerado'] = numpy.arange(len(df_retorno_grabar))
            if 'pre_frecuencia' in df_retorno_grabar.columns:
                df_retorno_grabar = df_retorno_grabar.drop('pre_frecuencia', axis=1)       

            if 'cod_impuesto' in df_retorno_grabar.columns:
                df_retorno_grabar = df_retorno_grabar.drop('cod_impuesto', axis=1) 

            _sql.jd.df= df_retorno_grabar
            self.guardar_warp_jd(_sql, True)
            _sql.jd.df= ''
            df_retorno_papel["valor_retencion"] = df_retorno_papel["valor_retencion"].map("${:,.2f}".format)    
            len_todos = len(df_retorno_papel.index)
            _sql.jd.contri_real = _sql.jd.contri
            df_paginado, df_pagina,  tiene_previa, tiene_siguiente =  self.get_paginar_compras(_sql, 1, len_todos)
            df_paginado["paginas"] = df_paginado["paginas"].astype(int)
            df_paginado["inicial"] = df_paginado["inicial"].astype(int)
            df_paginado["final"] = df_paginado["final"].astype(int)
            df_paginado["actual"] = df_paginado["actual"].astype(int)
            df_paginado["num_paginas"] = df_paginado["num_paginas"].astype(int)
            df_pagina["anio"] = df_pagina["anio"].astype(int)
            df_pagina["mes"] = df_pagina["mes"].astype(int)
            df_pagina["secuencial_retencion"] = df_pagina["secuencial_retencion"].astype(int)
            df_pagina["numerado"] = df_pagina["numerado"].astype(int)
            df_pagina["conteo"] = df_pagina["conteo"].astype(int)
            df_paginado =  df_paginado.to_dict("records")
            df_pagina =  df_pagina.to_dict("records")
            len_paginado = tiene_previa
            len_pagina = tiene_siguiente
            fecha = self.db.get_fecha_ymd()
            nombre= f"{_sql.jd.contri}_{fecha}_" 
            fragmentado = self.db.uf.fragmentar()
            placebo = str(int(random.uniform(15, 100000))).zfill(10)            
            seccion =  fragmentado, placebo, nombre
            if str(_sql.jd.tramite).strip() == '':
                _sql.jd.tramite = '19042008'
            
            enlace = f""" <a href="get_informe/{seccion[0]}03{seccion[1]}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="{seccion[2]}_CRUCE.xlsx" 
                            target="_blank" id='dev_a_cr' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Cruce de Retenciones</a> """
            placebo = str(int(random.uniform(15<<2, 100000))).zfill(10)
                        
            enlace_periodos = f""" <a href="get_informe/{seccion[0]}05{seccion[1]}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="{seccion[2]}_PERIODO.xlsx" 
                            target="_blank" id='dev_a_eperiodos' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Periodos</a> """

            placebo = str(int(random.uniform(15<<2, 100000))).zfill(10)
                        
            enlace_descartes = f""" <a href="get_informe/{seccion[0]}17{seccion[1]}/{_sql.jd.tramite}/{_sql.jd.usuario}/{_sql.jd.num_acceso}" download="{seccion[2]}_DESCARTES.xlsx" 
                            target="_blank" id='dev_a_descartados' class="btn btn-soft-dark btn-border a_desca_interna">Descargar Descartados</a> """

            if str(_sql.jd.tramite).strip() == '19042008':
                _sql.jd.tramite = ''
        else:
            listanovedades.append({"Novedad":"no existen resultados para el contribuyente!"})
           
        df_novedades = pd.DataFrame.from_dict(listanovedades)

        
        num_descartes = 0
        if not df_out_range.empty:      
            num_descartes = len(df_out_range.index) 
            if num_descartes>1000:
                df_out_range = df_out_range[0:1000]

        if isinstance(df_novedades, pd.DataFrame):
            df_novedades = df_novedades.to_dict("records")
        num_duplicados= 0
        
        if isinstance(df_duplicados, pd.DataFrame):
            df_duplicados = df_duplicados.to_dict("records")

        if isinstance(self.df_duplicados_encontrados, pd.DataFrame):
            num_duplicados = len(self.df_duplicados_encontrados.index)
        
        if isinstance(df_informe_exp, pd.DataFrame):
            df_informe_exp = df_informe_exp.to_dict("records")
            
        if isinstance(df_ingresado_exp, pd.DataFrame):
            df_ingresado_exp = df_ingresado_exp.to_dict("records")            

        if isinstance(df_paginado, pd.DataFrame):
            df_paginado = df_paginado.to_dict("records")

        if isinstance(df_pagina, pd.DataFrame):
            df_pagina = df_pagina.to_dict("records")

        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd
        compras = {
            #"longitudcompras": len_todos - num_duplicados,
            "longitudcompras": len_todos,
            "novedades": df_novedades,
            "duplicados": df_duplicados,
            "num_duplicados": num_duplicados,
            "df_informe_exp": df_informe_exp,
            "df_ingresado_exp":df_ingresado_exp,
            "df_longitudes_exp":df_longitudes_exp,
            "df_paginado_exp":df_paginado,
            "df_pagina_exp":df_pagina,
            "tiene_previa": len_paginado,
            "tiene_siguiente": len_pagina,
            "enlace_inf_rev": enlace,
            "enlace_periodos": enlace_periodos,
            "enlace_descartes": enlace_descartes,
            "num_cargadas_excel": int(_sql.jd.num_retenciones_excel),                                                
            "out_of_range_fe":df_out_range.to_dict('records'),
            "num_descartes":num_descartes 
        }
        return compras
        
        
    def get_archivo_ir(self, _sql):
        '''archivo ir'''
        if len(_sql.jd.contri)==10:
            _sql.jd.contri = self.db.uf.costelo(_sql.jd.contri)

        df_pagina = self.db.get_vector(_sql.get_sql_informe_retencion(_sql.jd.contri, -1, -1))        
        df_pagina = df_pagina[['ruc_contrib_informan', 'razon_social',
                               'fecha_emi_retencion', 'secuencial_retencion',
                               'autorizacion', 'valor_retenido_listado',
                               'valor_retenido_administracion', 'diferencia',
                               'es_fantasma', 'es_fallecido', 'conteo',
                               'cruza', 'valor_retencion']]
        df_pagina.rename(columns = {'ruc_contrib_informan': 'RUC DEL AGENTE RETENCION'}, inplace = True)
        df_pagina.rename(columns = {'razon_social': 'RAZON SOCIAL'}, inplace = True)
        df_pagina.rename(columns = {'fecha_emi_retencion': 'FECHA DE EMISIÓN'}, inplace = True)
        df_pagina.rename(columns = {'secuencial_retencion': 'SECUENCIA'}, inplace = True)
        
        df_pagina['SECUENCIA'] = df_pagina['SECUENCIA'].astype(str)
        
        df_pagina.rename(columns = {'autorizacion': 'AUTORIZACIÓN'}, inplace = True)
        df_pagina.rename(columns = {'valor_retenido_listado': 'VALOR LISTADO'}, inplace = True)
        df_pagina.rename(columns = {'valor_retenido_administracion': 'VALOR ADMINISTRACION'}, inplace = True)
        df_pagina.rename(columns = {'diferencia': 'DIFERENCIA'}, inplace = True)
        df_pagina.rename(columns = {'es_fantasma': 'FANTASMAS'}, inplace = True)
        df_pagina.rename(columns = {'es_fallecido':'FALLECIDOS'}, inplace = True)
        df_pagina.rename(columns = {'conteo': 'DUPLICADOS'}, inplace = True)
        df_pagina.rename(columns = {'cruza': 'CRUZA'}, inplace = True)
        df_pagina.rename(columns = {'valor_retencion': 'VALOR CADENA'}, inplace = True)
        df_pagina['VALOR CADENA'] = df_pagina['VALOR CADENA'].astype(float)        
        return df_pagina 
    
    
