"""Listado de EXCEL, desde Diciembre 2022

Funcionalidades:
  - Sirve para recibir el archivo de excel ingresado por el analista de cada
    zonal.

    El contri  110XXXXXXXXXX001 solicita devoluciones de retenciones de IVA
    para el periodo
                2022-01-01              2022-12-31


    Y carga el listado de excel en 8 columnas:
    'agente_retencion', 'fecha_emision',  'serie', 'comprobante',
    'autorizacion',  'porcentaje_iva', 'porcentaje_retencion_iva',
    'valor_retenido','fecha_carga', 'contri'

    agente_retencion : Debe tener 13 caracteres solo numeros
    fecha_emision    : Formato aaaa-mm-dd de preferencia, puede usarse otros
                            formatos como dd/mm/yyyy
    serie            : Es un campo que indica la serie del documento,
                        no se usa en el aplicativo de forma relevante
                        solo esun recuerdo
    comprobante      : es un secuencial, si este esta en formato 001-001-232323
                        se sivide en tres partes y se toma la ultima parte
                        los ultimos 8 caracteres
    autorizacion     : de 50 caracteres si es electronico o deunas 10
                        caracteres sies fisico
    base_imponible   : es un valor numerico que representa  la base de la
                        retencion, es solo un recuerdo que se guarda
                        en el aplicativo
    porcentaje_iva   : es un valor numerico que representa el porcentaje de la
                        retencion, es solo un recuerdo que se guarda en
                        el aplicativo
    valor_retenido   : es un valor numerico que representa un valor en dolares,
                        debe estar con dos decimales en la entrada si se pasa
                        se recorta a 2

 - fn(decidir_formato)  Encausa el formato correcto de la fecha
                          segun como podria venir
 - fn(depurar_listado)             Guarda la tabla d resultados en pantalla
 - fn(set_reproceso_descartados)   Se incluye un reproceso de descartados,
                                    aplica solo para fisicos, si el CF existe
                                    en las autorizaciones entonces se lo saca
                                    de descartados
 - fn(fx_calamina)                 Se cambia el metodo de lectura de los
                                    archivos de excel
 - fn(tratar_listado)              La recolecion de variables que va
                                    arrojando el excel

+-------------------+-------------------+-------------------------------------+
| Fecha             | Modifier          | Descripcion                         |
+-------------------+-------------------+-------------------------------------+
| 2022-10-25        | jagonzaj          | Carga de archivo via pandas, se     |
|                                       |  revis existan las 8 columnas       |
| 2022-11-18        | jagonzaj          | Carga de archivo via pandas, para   |
|                                       |  columnas especificas primeras      |
|                                       |  depuraciones                       |
| 2023-01-20        | jagonzaj          | Cambio en la forma de carga de      |
|                                       |  archivo , seutiliza una            |
|                                       |  nomenclatura para poder ubicar que |
|                                       |  usuario esta cargando archivos     |
|                                       |  redundantes                        |
| 2023-03-20        | jagonzaj          | Se incluyen mas depuraciones en el  |
|                                       |  listado, para incrementar el numero|
|                                       |  de archivos validos,               |
| 2023-03-20        | jagonzaj          | Se toma la fecha de la autorizacion |
|                                       |   07012022070992262427001200100100*,|
|                                       |   pero se inactiva                  |
| 2024-01-15        | jagonzaj          | Se incluye calamina para la         |
|                                       |     lectura de excel                |
+-------------------+-------------------+-------------------------------------+
"""

import os, math, traceback, unicodedata, re
import pandas as tired
import numpy as numerico
from datetime import datetime
from datos import Consultas, RetencionesQ
from timeit import default_timer as timer
from datetime import timedelta
from logicas import Materiales
from joblib import Parallel, delayed, parallel_backend
from pandarallel import pandarallel
from python_calamine import CalamineWorkbook
from python_calamine.pandas import pandas_monkeypatch
pandas_monkeypatch()


class ArchivoExcel (Materiales.Universales):
    """Caracteristicas Futuras version 1.0.9
    -------------
    - La funcion para tmar la fecha de la autorizacion queda inactiva hasta
    retomarla posiblemente Enero 2025
    """
    __version__ = "1.0.8"

    def __init__(self, db):
        '''constructor principal'''
        self.db = db
        self.cn = Consultas.Papel(db)        
        tired.options.mode.copy_on_write = True

    def filtrarnumero(self, texto):
        '''filtrar numero'''
        return "".join(c for c in texto if c.isdigit())

    def detectar_numero(self, texto):
        '''detectar numero'''
        posible_numero = ''
        for caracter in texto:
            if caracter.isnumeric():
                posible_numero += caracter
        return posible_numero

    def fix_float_error(self, x):
        '''arrglar formato float'''
        return float('{:n}'.format(x))

    def tratar_porcentaje(self, texto):
        '''tratar porcentaje'''
        texto = texto.replace("%", "")
        texto = texto.replace(",", ".")
        if texto.isnumeric():
            if int(texto.strip())>1:
                texto = str(float(texto)/100)
        else:
            texto = '0'
        return texto

    def decidir_formato(self, fecha):
        '''buscar formato de fecha'''
        formato = '%Y-%m-%d'
        descubierto = ''
        simbolos = ['-', '/']
        fecha_nueva = '          '
        rearmado = fecha
        res = [i for i in fecha if i in simbolos]
        simb_usado = ['*']
        simbolo = '?'
        if len(res) > 0:
            simb_usado = list(set(res))
            simbolo = simb_usado[0]

        if fecha.count(simbolo) == 2 and len(descubierto) != 8 and simbolo in simbolos:
            partes = fecha.split(simbolo)
            for i in range(len(partes)):
                if len(partes[i]) < 2 and len(partes[i]) > 0:
                    partes[i] = partes[i].zfill(2)

            if len(partes[0]) == 2 and len(partes[1]) == 2 and len(partes[2]) == 2 and int('20'+partes[2]) > 2015 and int('20'+partes[2]) < 2099:
                partes[2] = '20'+partes[2]

            if simbolo == simb_usado[0]:
                rearmado = f"{partes[0]}{simbolo}{partes[1]}{simbolo}{partes[2]}"

            if len(partes[0]) == 2 and (int(partes[0]) > 0 and int(partes[0]) < 32):
                descubierto = f'%d{simbolo}'

                if len(partes[1]) == 2 and (int(partes[1]) > 0 and int(partes[1]) < 13):
                    descubierto += f'%m{simbolo}'
                    if len(partes[2]) == 4 and (int(partes[2]) > 0 and int(partes[2]) < 9999):
                        descubierto += f'%Y'

            if len(partes[0]) == 2 and (int(partes[0]) > 0 and int(partes[0]) < 13) and len(descubierto) != 8:
                descubierto = f'%m{simbolo}'
                if len(partes[1]) == 2 and (int(partes[1]) > 0 and int(partes[1]) < 32):
                    descubierto += f'%d{simbolo}'
                    if len(partes[2]) == 4 and (int(partes[2]) > 0 and int(partes[2]) < 9999):
                        descubierto += '%Y'

            if len(partes[0]) == 4 and (int(partes[0]) > 0 and int(partes[0]) < 9999) and len(descubierto) != 8:
                descubierto = f'%Y{simbolo}'
                if len(partes[1]) == 2 and (int(partes[1]) > 0 and int(partes[1]) < 13):
                    descubierto += f'%m{simbolo}'
                    if len(partes[2]) == 2 and (int(partes[2]) > 0 and int(partes[2]) < 32):
                        descubierto += '%d'

                if len(partes[1]) == 2 and (int(partes[1]) > 0 and int(partes[1]) < 32) and len(descubierto) != 8:
                    descubierto += f'%d{simbolo}'
                    if len(partes[2]) == 2 and (int(partes[2]) > 0 and int(partes[2]) < 13):
                        descubierto += '%m'

        if len(descubierto) == 8:
            fecha_nueva = rearmado

        formato = '' if fecha_nueva == '' else descubierto
        fecha_nueva = '' if fecha_nueva == '' else fecha_nueva
        return formato, fecha_nueva

    def convertir_fecha(self, a, b):
        '''conversion de fecha'''
        return datetime.strptime(a, b)

    def set_fecha_from_aut(self, aut, fi):
        '''fecha desde la autorizacion'''
        dia = 'N'
        mes = 'N'
        anio = 'N'
        fecha_aut = 'N'
        fecha_final = fi
        if len(aut) > 30 and len(aut) < 60:
            posible_fecha = aut[0:9]
            posible_dia = int(posible_fecha[0:2])
            posible_mes = int(posible_fecha[2:4])
            posible_anio = int(posible_fecha[4:8])
            if posible_dia > 0 and posible_dia < 32:
                dia = str(posible_dia).zfill(2)

            if posible_mes > 0 and posible_mes < 32:
                mes = str(posible_mes).zfill(2)

            if posible_anio > 2010 and posible_anio < 2050:
                anio = str(posible_anio).zfill(2)

            if dia != 'N' and mes != 'N' and anio != 'N':
                fecha_aut = f"{anio}-{mes}-{dia}"

            if fecha_aut != 'N':
                fecha_final = fecha_aut
        return fecha_final

    def truncate(self, f, n):
        '''truncate'''
        return math.floor(f * 10 ** n) / 10 ** n

    def truncate_float(self, n, places):
        '''truncar float'''
        if len(str(n).split(".")[1]) == places:
            return n
        else:
            return int(n * (10 ** places)) / 10 ** places             

    def fx_clean_celda_vacia(self, x):
        '''limiar celda vacia'''
        x = x.strip()
        if len(x) == 0:
            x = '0'
        else:
            x
        return x

    def fx_emisor(self, tercero):
        '''emisor'''
        tercero = tercero.strip()
        tercero = tercero.replace(".0", '')
        tercero = tercero.replace(".", '')
        tercero = tercero.replace("'", '')
        tercero = tercero.replace(' ', '')
        tercero = tercero.lstrip()
        tercero = tercero[:13]
        if len(tercero) == 12 and tercero.endswith("001"):
            tercero = '0' + str(tercero)
        tercero = tercero.zfill(13) if len(tercero) <= 12 else tercero
        return tercero

    def depurar_listado(self, df_contri_file):
        '''se soliciona algunos temas en el listado'''
        tired.options.mode.copy_on_write = True

        df_contri_file.fecha_emision = df_contri_file.fecha_emision.replace(r'\s+', '', regex=True)
        df_contri_file['valor_retenido'] = df_contri_file['valor_retenido'].astype(str)        
        df_contri_file['valor_retenido'] = df_contri_file['valor_retenido'].apply(lambda x: self.fx_clean_celda_vacia(x))
        df_contri_file['valor_retenido'] = df_contri_file['valor_retenido'].astype(float)
        df_contri_file['valor_retenido'] = df_contri_file['valor_retenido'].apply(lambda x: self.db.uf.redondear(x,3))
        df_contri_file['valor_retenido'] = df_contri_file['valor_retenido'].apply(lambda x: self.db.uf.redondear(x,2))
        df_contri_file['porcentaje_iva'] = df_contri_file['porcentaje_iva'].str.replace(",",".")
        df_contri_file['porcentaje_retencion_iva'] = df_contri_file['porcentaje_retencion_iva'].apply(lambda x: self.tratar_porcentaje(x))
        df_contri_file['autorizacion'] = df_contri_file['autorizacion'].str.replace("'","")
        df_contri_file['autorizacion'] = df_contri_file['autorizacion'].str.replace(".0","")
        df_contri_file['autorizacion'] = df_contri_file['autorizacion'].apply(lambda x: self.detectar_numero(x))
        df_contri_file['autorizacion'] = df_contri_file['autorizacion'].str.slice(0, 60)
        df_contri_file['comprobante'] = df_contri_file['comprobante'].str.replace("'","")
        df_contri_file['comprobante'] = df_contri_file['comprobante'].apply(lambda nupy: self.get_comprobante(nupy))
        df_contri_file["comprobante"] = df_contri_file["comprobante"].replace(["^\\s*$"], '0', regex=True)
        df_contri_file["comprobante"] = df_contri_file["comprobante"].astype(int) 
        df_contri_file['fecha_carga'] =  tired.to_datetime(df_contri_file['fecha_carga'])
        df_contri_file['fecha_emision'] = df_contri_file['fecha_emision'].astype(str) 
        df_contri_file['fecha_emision'] = df_contri_file['fecha_emision'].str[:10]
        df_contri_file['agente_retencion'] = df_contri_file['agente_retencion'].astype(str)
        df_contri_file['agente_retencion'] = df_contri_file['agente_retencion'].map(str.strip)
        df_contri_file['agente_retencion'] = df_contri_file['agente_retencion'].apply(lambda x: self.fx_emisor(x))
        df_contri_file[['formato', 'fecha_emision']] = df_contri_file['fecha_emision'].apply(lambda x: self.decidir_formato(x)).to_list()
        df_contri_file_nv = df_contri_file[df_contri_file["formato"] == '']
        df_contri_file_aux = df_contri_file.copy()

        df_contri_file = df_contri_file[(df_contri_file["formato"].str.len() == 8) & (df_contri_file["comprobante"] > 0)]
        if not df_contri_file.empty:
            df_contri_file.loc[:, 'fecha_emision'] = df_contri_file.apply( lambda row: self.convertir_fecha(str(row["fecha_emision"]),  row["formato"]), axis=1)
            df_contri_file.loc[:, 'fecha_emision'] = tired.to_datetime(df_contri_file['fecha_emision'], format='mixed', errors='coerce').dt.date

        df_contri_file_comp_nv = df_contri_file_aux.query("comprobante < 1")
        df_contri_file_nv = tired.concat([df_contri_file_nv, df_contri_file_comp_nv])
        return df_contri_file, df_contri_file_nv

    def get_comprobante_va(self, posible_comprobante):
        '''obtiene el comprobante '''
        posible_comprobante = str(posible_comprobante).strip()
        posible_comprobante = str(posible_comprobante).lstrip("\n\r")
        posible_comprobante = re.sub(r'\n$', ' ', posible_comprobante)
        posible_comprobante = ' '.join(set(posible_comprobante.split()))
        posible_comprobante = str(posible_comprobante).strip()
        posible_comprobante = posible_comprobante.replace('\n', ' ')
        posible_comprobante = str(posible_comprobante).replace(".0", "")
        comprobante = posible_comprobante
        secciones = str(posible_comprobante).split('-')
        if len(secciones) > 0:
            comprobante = secciones[-1]

        comprobante = str(comprobante).lstrip("0")
        lcomp = re.findall(r"(\d+)", comprobante)
        if lcomp and len(lcomp) > 0:
            comprobante = int(lcomp[0])
        else:
            comprobante = -1
        if len(str(comprobante)) > 8:
            comprobante = str(comprobante)[0:8]

        return comprobante

    def get_comprobante(self, comprobante):
        '''conseguir comprobante'''
        comprobante = str(comprobante)
        if comprobante.endswith(".0"):
            comprobante = comprobante.replace(".0", "")

        if comprobante.endswith(",0"):
            comprobante = comprobante.replace(",0", "")

        comprobante_limpio = re.sub(r'[^0-9]', '-', comprobante)
        partes = re.split(r'[^0-9]+', comprobante_limpio)
        partes_numericas = [parte for parte in partes if parte]
        if partes_numericas:
            return partes_numericas[-1]
        else:
            return -1

    def set_reproceso_descartados(self, _sql):
        '''reprocesamiento descartados'''
        df_para_nocruzan = tired.DataFrame()
        df_respuesta = _sql.jd.df.copy()
        df_descartados = _sql.jd.df.copy()

        if not df_descartados.empty:
            df_fisicas = df_descartados[df_descartados["autorizacion"].str.len() == 10]
            if not df_fisicas.empty:
                df_fisicas = df_fisicas[df_fisicas["contri"] == _sql.jd.contri]
                df_fisicas[['formato', 'fecha_emision']] = df_fisicas['fecha_emision'].apply(lambda x: self.decidir_formato(x)).to_list()
                df_fisicas = df_fisicas[(df_fisicas["formato"].str.len() == 8) & (df_fisicas["comprobante"] > 0)  & (df_fisicas["agente_retencion"].str.len() == 13)]
                df_fisicas.loc[:, 'fecha_emision'] = df_fisicas.apply( lambda row: self.convertir_fecha(str(row["fecha_emision"]),  row["formato"]), axis=1)
                df_fisicas.loc[:, 'fecha_emision'] = tired.to_datetime(df_fisicas['fecha_emision'], format='mixed', errors='coerce').dt.date
                fecha_inicio = datetime.strptime(_sql.jd.periodo_inicial_org, '%Y-%m-%d').date()
                fecha_final = datetime.strptime(_sql.jd.periodo_final_org, '%Y-%m-%d').date()
                df_fisicas = df_fisicas[(df_fisicas.fecha_emision.between(fecha_inicio, fecha_final))]
                df_fisicas.fillna(value='0', inplace=True)
                df_fisicas["comprobante"] = df_fisicas["comprobante"].astype(int)
                df_fisicas["autorizacion"] = df_fisicas["autorizacion"].astype(str)
                df_fisicas["agente_retencion"] = df_fisicas["agente_retencion"].astype(str)
                df_fisicas["fecha_emision"] = df_fisicas["fecha_emision"].astype(str)
                df_fisicas_before = df_fisicas.copy()
                df_fisicas = df_fisicas.reset_index()
                df_ffpv = tired.DataFrame()
                with parallel_backend(backend="threading"):
                    parallel = Parallel(verbose=0)
                    resultados = parallel([delayed(self.get_posible_ffpv)(_sql, fila) for ix, fila in df_fisicas.iterrows()])
                if len(resultados) > 0:
                    df_ffpv = tired.concat(resultados).reset_index()
                    df_ffpv["comprobante"] = df_ffpv["comprobante"].astype(int)
                    df_ffpv["autorizacion"] = df_ffpv["autorizacion"].astype(str)
                    df_ffpv["agente_retencion"] = df_ffpv["agente_retencion"].astype(str)
                    df_ffpv["fecha_emision"] = df_ffpv["fecha_emision"].astype(str)

                if "index" in df_ffpv:
                    df_ffpv.drop({'index'}, axis=1, inplace=True)

                indices = tired.unique(df_fisicas_before.index).tolist()
                if len(indices) > 0:
                    df_para_nocruzan = df_descartados.loc[df_descartados.index.isin(indices)]
                    if "razon" in df_para_nocruzan:
                        df_para_nocruzan.drop({'razon'}, axis=1, inplace=True)

                    df_respuesta = df_descartados.loc[~df_descartados.index.isin(indices)]

                if not df_respuesta.empty:
                    df_respuesta.loc[:, "estado"] = 'INA'
        return df_para_nocruzan, df_respuesta

    def get_posible_ffpv(self, _sql, fila):
        '''posible ffpv'''
        _sql.jd.tercero = fila["agente_retencion"]
        _sql.jd.autorizacion_tercero = fila["autorizacion"]
        _sql.jd.fecha_tercero = fila["fecha_emision"]
        _sql.jd.secuencia_tercero = fila["comprobante"]
        df = self.db.get_vector(_sql.get_sql_posible_ffpv())
        df["indice"] = fila["index"]
        return df

    def strip_accents(self, s):
        '''eliminar acentos'''
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    def fx_separar(self, columna):
        '''separar'''
        columna = columna.strip().lower()
        columna = columna.replace("fecharet", "fecha ret")
        columna = columna.replace("valorretenido", "valor retenido")
        columna = columna.replace("numeroautorizacion", "numero autorizacion")
        columna = columna.replace("RetenerIVA", "retener iva")
        columna = columna.replace("baseImponibleIVA", "base imponible iva")
        palabras_pre = columna.split(' ')
        palabras_pre_a = []
        try:
            palabras_res = []
            if len(palabras_pre) > 0:
                for pal in palabras_pre:
                    pal = self.strip_accents(pal)
                    pal = ''.join(letter for letter in pal if letter.isalnum())
                    if len(pal) > 4:
                        palabras_res.append(pal)
            else:
                palabras_res.append(columna)

        except Exception as ex1:
            print(f"ex1 {ex1}")
        return palabras_pre_a

    def fx_columnas_reales(self, fila):
        '''columnas reales'''
        l_columnas = []
        for col in fila:
            if len(str(col).strip()) > 0:
                l_columnas.append(col)

        if len(l_columnas) > 2:
            l_columnas = []
            for col in fila:
                l_columnas.append(col)
        return len(l_columnas)

    def fx_n_primera(self, filas):
        '''buqueda inciial'''
        constancia = False
        num_filas_f = 0
        siguiente = 0
        f = 0
        limite = 9
        if len(filas) <= 10:
            limite = len(filas)
        while not constancia and f < limite:
            num_filas_f = self.fx_columnas_reales(filas[f])
            anterior = num_filas_f
            if (anterior == siguiente-1 or anterior == siguiente + 1 or anterior == siguiente) and siguiente > 2:
                constancia = True

            if f > limite:
                constancia = True
            siguiente = anterior
            f = f+1

        if f < 0:
            f = 0

        if f < 3:
            f = 0
        else:
            f = f-2

        return int(f)

    def fx_calamina(self, archivox):
        '''carga de execl como calamina'''
        des = ''
        num_hojas = 0
        df = tired.DataFrame()
        err = 0
        try:
            with tired.ExcelFile(archivox) as xls_libro:
                try:
                    hojas = xls_libro.sheet_names
                    num_hojas = len(hojas) 
                    for hojanombre in hojas:
                        df = CalamineWorkbook.from_path(archivox).get_sheet_by_name(hojanombre).to_python(skip_empty_area=True)
                        i_a = len(df)
                        if i_a > 0:
                            banda_limite_analisis = 10
                            if i_a < 10:
                                banda_limite_analisis = i_a
                            if len(df)>2:
                                numero_iniciador = self.fx_n_primera(df[0:banda_limite_analisis])
                            else:
                                numero_iniciador = 0
                            columnas_reales = df[numero_iniciador]
                            dfa = tired.DataFrame(df, dtype="string")
                            df = dfa.copy()
                            dfz = df.copy() 
                            dfz = dfz.set_axis(columnas_reales, axis=1)
                            if i_a == 1:
                                dfz = dfz[0:0]
                            inicio = int(numero_iniciador+1)
                            if i_a > 0:
                                dfz = dfz.iloc[inicio:]
                            dfz = dfz.loc[:, ~dfz.columns.str.contains('^Unnamed')]
                            dfz = dfz.loc[:,~dfz.columns.duplicated()]
                            if '' in dfz.columns:
                                df = dfz.drop(columns=[''])
                            else:
                                df = dfz

                            df_f = tired.DataFrame()
                            if len(df.columns) > 20:
                                columnas = df.columns.to_list()
                                for ix, col in enumerate(columnas, start=0):
                                    if ix < 10:
                                        df_f[col] = df[col]
                            else:
                                df_f = df.copy()

                            duplicadas = []
                            descartar = False
                            if len(df_f.columns) > 7 and len(df_f.columns) < 20:
                                columnas = df_f.columns.to_list()
                                try:
                                    for col_a in columnas:
                                        for col_b in columnas:
                                            if col_a != col_b and df[col_a].equals(df[col_b]) and col_a not in duplicadas and (col_a.lower().find("valor") < 0) \
                                                and (col_a.lower().find("porcentaje") < 0) and (col_a.lower().find("base") < 0):
                                                duplicadas.append(col_b)

                                except Exception as ex4:
                                    print(f"ex4 {ex4}")
                                df = tired.DataFrame()
                                try:
                                    if len(duplicadas) > 0 and len(columnas) != 8:
                                        for colum in columnas:
                                            if colum not in duplicadas:
                                                df[colum] = df_f[colum]
                                    else:
                                        for colum in columnas:
                                            df[colum] = df_f[colum]
                                except Exception as ex2:
                                    print(f"ex2 {ex2}")
                            else:
                                descartar = True
                            suma = 0
                            hoja_elegida = False
                            if num_hojas > 0 and not descartar:
                                criterios = ["fecha", "emision", "agente", "retencion", "contri", "autorizacion", "secuencia", "base", "valor", "retenido", "retencion"]
                                columnas_df = df.columns.to_list() 
                                for col in columnas_df:
                                    for cri in criterios:
                                        descomp = self.fx_separar(col)
                                        for pal in descomp:
                                            if pal == cri:
                                                criterios.remove(cri)
                                                suma += 1
                                                break
                                if suma > 5:
                                    hoja_elegida = True
                            if hoja_elegida:
                                break

                            if not df.empty:
                                if len(df.columns) < 8:
                                    err = 1
                                    des = f"Insuficientes Columnas,  {len(df.columns)}   en un archivo con {num_hojas} hojas "
                                if len(df.columns) > 8:         
                                    err = 2
                                    des = f"Demasiadas Columnas,  {len(df.columns)}   en un archivo con {num_hojas} hojas"
                        else:
                            err = 5
                            des = f"Hoja e blanco   en un archivo con {num_hojas} hojas"
                except Exception as ex:
                    err = 4
                    if str(ex).find("Zip error: invalid Zip archive:") >= 0:
                        err = 15

                    des = str(ex) + f"*** {len(df.columns)}   en un archivo con {num_hojas} hojas,  err {err}  "
                    print(f"Lectura de Archivo  {des}")
        except Exception as ex:
            err = 3
            des = f"*** err {err} archivo {archivox}  err {str(ex)} "
            print(f"Lectura de Archivo  {des}")
        if type(df) == list:
            df = tired.DataFrame(df)
        return df, int(err), des

    def tratar_listado(self, archivo_in, fn, params):
        '''recepcion de archivo de excel'''
        tired.options.mode.copy_on_write = True
        _jd = self.db.uf.pi
        _sql = RetencionesQ.Excel(_jd)
        _his = self.db.uf.his
        _inf = self.db.uf.informante
        estadisticas = {"guardado": 0}
        df_contri_file = tired.DataFrame()
        df_contri_file_nv_x = tired.DataFrame()
        _sql.jd.fecha_hoy = self.db.get_fecha_ymd()
        self.db.get_actualizar(_sql.get_sql_cadena_iva_proc_reset())
        try:
            archivo_in.save(os.path.join(self.db.config.UPLOAD_FOLDER,  fn))
            print(f"{self.db.uf.CYAN} _Cargando {str(fn)} Comienza en  {self.db.get_fecha_ymd()}  {self.db.uf.RESET} ")
            df_contri_file, err, des = self.fx_calamina(os.path.join(self.db.config.UPLOAD_FOLDER,  fn))
            if err == 15:
                err = 0
                des = ''
                try:
                    if fn.endswith(".xlsx"):
                        fn_temp = fn.replace(".xlsx",".xls")
                        os.rename(os.path.join(self.db.config.UPLOAD_FOLDER,  fn), os.path.join(self.db.config.UPLOAD_FOLDER,  fn_temp))
                        fn = fn.replace(".xlsx",".xls")
                        df_contri_file, err, des = self.fx_calamina(os.path.join(self.db.config.UPLOAD_FOLDER,  fn))
                    elif fn.endswith(".xls"):
                        fn_temp = fn.replace(".xls",".xlsx")
                        os.rename(os.path.join(self.db.config.UPLOAD_FOLDER,  fn), os.path.join(self.db.config.UPLOAD_FOLDER,  fn_temp))
                        fn = fn.replace(".xls",".xlsx")
                        df_contri_file, err, des = self.fx_calamina(os.path.join(self.db.config.UPLOAD_FOLDER,  fn))
                except Exception as ex:
                    err = 4
                    des = f"Archivo {fn}  tiene un formato incorrecto {ex}"

            print(f"{self.db.uf.BLUE} ______________XLSX    {str(fn)} {self.db.uf.RESET}")
            print(f"{self.db.uf.CYAN}  545 Termina de cargar en  {self.db.get_fecha_ymd()} filas load {len(df_contri_file.index)}  err{err}  des {des}  {self.db.uf.RESET} ")
            print(f"{self.db.uf.BLUE} __________________________________________________ {self.db.uf.RESET}")

            if int(err) > 0:
                _inf.detener = True
                if des.lower().find("unable to read workbook") >= 0:
                    des = "Grabe el excel en un archivo excel (Excel WorBook xlsx) reciente, sin marcar como Strict Open XML EXCEL"
                _inf.agregar_razones({'mensaje': des, "category": "archivo", "detener": True})

            df_contri_file.dropna(how='all', axis=1, inplace=True)
            df_contri_file = df_contri_file.fillna('0')
            numero_filas = len(df_contri_file.index)
            _his.num_excel_filas = int(numero_filas)
            estadisticas["numero_filas"] = numero_filas
            if numero_filas == 0:
                _inf.detener = True
                _inf.agregar_razones({'mensaje': f"El  archivo  {_jd.contri} esta vacio   ", "category": "archivo", "detener": True})

            df_parecido = self.db.get_vector(_sql.get_sql_caso_parecido())
            num_parecidos = len(df_parecido.index)
            if num_parecidos > 0:
                # 1 detener = 0
                nombre = df_parecido['nombre'].iloc[0]
                email = df_parecido['email'].iloc[0]
                numero_tramite = df_parecido['numero_tramite'].iloc[0]
                _inf.agregar_razones({'mensaje': f"Existe un tramite del contribuyente en el mismo periodo, de {nombre} ,@ {email} ,TRAMITE: {numero_tramite}  ","category" : "archivo","detener": False })

            if not _inf.detener:
                estadisticas["num_columnas"] = len(df_contri_file.columns)
                if len(df_contri_file.columns) > self.db.config.NUM_COLUMNAS_ARCHIVO_RETENCION:
                    diferencia_columnas = self.db.config.NUM_COLUMNAS_ARCHIVO_RETENCION - len(df_contri_file.columns)
                    if diferencia_columnas < 0:
                        restar = len(df_contri_file.columns) - (diferencia_columnas*-1)
                        df_contri_file = df_contri_file.iloc[:, :restar]
                if len(df_contri_file.columns) == self.db.config.NUM_COLUMNAS_ARCHIVO_RETENCION:
                    df_contri_file['fecha_carga'] = self.db.get_fecha_ymd_hms()
                    estadisticas["fecha_ejecucion"] = self.db.get_fecha_ymd_hms()
                    df_contri_file['fecha_carga'] = df_contri_file['fecha_carga'].astype(str)
                    df_contri_file['contri'] = _jd.contri            
                    df_contri_file.columns = self.db.config.ARCHIVO_RETENCION_COLS
                    # 1. vacios en valor retenido
                    self.db.uf.his.num_excel_val_ret_blanks = int(len(df_contri_file[df_contri_file['valor_retenido'] == '']))
                    estadisticas["num_vacios_vr"] = self.db.uf.his.num_excel_val_ret_blanks/numero_filas*100
                    if "num_vacios_vr" in estadisticas:
                        if len(str(estadisticas["num_vacios_vr"])) == 0:
                            estadisticas["num_vacios_vr"] = 0
                        elif int(estadisticas["num_vacios_vr"])/numero_filas * 100 >= 50:
                            self.db.uf.informante.detener = True
                            self.db.uf.informante.agregar_razones({'mensaje': f"El  archivo  {self.db.uf.pi.contri} la columna valor retenido tiene mas de la mitad de valores en blanco por favor rellenar ","category" : "archivo","detener": True })

                    # 1 valores incorrectos en el valor de retencion
                    if not _inf.detener:
                        df_contri_file['valor_retenido'] = df_contri_file['valor_retenido'].str.replace(",", ".")
                        df_val_retenido_x = tired.DataFrame()
                        df_selecciones = df_contri_file.apply(lambda row: self.db.uf.es_fx(row['valor_retenido']), axis=1)
                        if not df_selecciones.empty:
                            indices = tired.unique(df_selecciones.index).tolist()
                            df_val_retenido_x = df_contri_file.loc[~df_contri_file.index.isin(indices)]
                            df_contri_file = df_contri_file.loc[df_contri_file.index.isin(indices)]

                        estadisticas["num_vr_no_numericos"] = len(df_val_retenido_x.index)
                        _his.num_excel_col_val_ret_invalid = int(estadisticas["num_vr_no_numericos"])
                        df_contri_file, df_contri_file_nv_fechas = self.depurar_listado(df_contri_file)
                        if not df_contri_file.empty:
                            df_contri_file_nv = df_contri_file[df_contri_file["fecha_emision"].isnull()]
                            if not df_contri_file_nv.empty:
                                df_contri_file_nv["razon"] = "Fechas de emision no declarada"
                            if not df_contri_file_nv_fechas.empty:
                                df_contri_file_nv_fechas["razon"] = "Fechas de emision formato incorrecto"
                            if not df_val_retenido_x.empty:
                                df_val_retenido_x["razon"] = "Valores de Retencion incorrectas"

                            if not df_contri_file_nv.empty or not df_contri_file_nv_fechas.empty or not df_val_retenido_x.empty:
                                df_contri_file_nv_x = tired.concat([df_contri_file_nv, df_contri_file_nv_fechas, df_val_retenido_x])
                            _his.num_excel_fec_emi_invalid = int(len(df_contri_file_nv_fechas.index))
                            df_contri_file = df_contri_file[df_contri_file["fecha_emision"].notnull()]
                            df_contri_file['estado'] = 'INA'
                            df_contri_file_test = df_contri_file.copy()
                            df_contri_file_test["fecha_emision"] = tired.to_datetime(df_contri_file_test.fecha_emision)
                            df_contri_file_fuera_rango = df_contri_file_test[~(df_contri_file_test.fecha_emision.between(_jd.periodo_inicial_org, _jd.periodo_final_org))]                                  
                            df_contri_file = df_contri_file_test[(df_contri_file_test.fecha_emision.between(_jd.periodo_inicial_org, _jd.periodo_final_org))]
                            if not df_contri_file_fuera_rango.empty:
                                df_contri_file_fuera_rango["razon"] = "Retenciones fuera de rango de fecha"

                            if not df_contri_file_nv_x.empty:
                                df_contri_file_nv_x = tired.concat([df_contri_file_nv_x, df_contri_file_fuera_rango])

                            if df_contri_file_nv_x.empty:
                                df_contri_file_nv_x = df_contri_file_fuera_rango

                            df_contri_file_propias = df_contri_file.copy()
                            df_contri_file_propias["fecha_emision_pivot"] = tired.to_datetime(df_contri_file_propias.fecha_emision)
                            df_contri_file_propias = df_contri_file_propias[(df_contri_file_propias.fecha_emision_pivot.between(_jd.periodo_inicial_org, _jd.periodo_final_org))]
                            df_contri_file_propias_ret = df_contri_file_propias["autorizacion"]
                            df_retenciones_subjetivas = self.db.get_vector(_sql.get_sql_retenciones_propias_subjetivas())
                            df_objetivas = tired.merge(df_contri_file_propias_ret, df_retenciones_subjetivas, how="inner", indicator=True, on=["autorizacion"], suffixes=('_x', '_y')).reset_index()
                            df_objetivas["autorizacion"] = df_objetivas["autorizacion"].astype(str)
                            df_contri_file["autorizacion"] = df_contri_file["autorizacion"].astype(str)
                            lista_elegibles = tired.unique(df_objetivas["autorizacion"]).tolist()
                            lista_son = tired.unique(df_contri_file["autorizacion"]).tolist()
                            lista_no_elegibles = list(set(lista_son) - set(lista_elegibles))
                            lista_remover = []
                            for autorizacion in lista_no_elegibles:
                                existe = -1904
                                _sql.autorizacion = autorizacion.strip()
                                match(len(autorizacion.strip())):
                                    case 10:
                                        _sql.tipo = 'FIS'
                                        existe = self.db.get_scalar(_sql.get_posible_autorizacion())

                                    case 40 | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 | 50 | 51 | 52 | 53:
                                        _sql.tipo = 'ELEC'
                                        existe = self.db.get_scalar(_sql.get_posible_autorizacion())
                                    case _:
                                        existe = -1

                                if existe == 0:
                                    lista_remover.append(autorizacion)

                            if len(lista_remover) > 0:
                                lista_no_elegibles = list(set(lista_no_elegibles) - set(lista_remover))

                            if len(df_objetivas) == 0:
                                _inf.agregar_razones({'mensaje': f"En el archivo {fn} para el contribuyente {_sql.jd.contri} no tiene retenciones que le pertenecen, en el periodo solicitado! ", "category": "archivo", "detener": True})
                                _inf.detener = True

                            if not _inf.detener:
                                df_contri_file_nv_no_elegibles = df_contri_file[df_contri_file['autorizacion'].isin(lista_no_elegibles)]
                                df_contri_file = df_contri_file[~df_contri_file['autorizacion'].isin(lista_no_elegibles)]
                                if not df_contri_file_nv_no_elegibles.empty:
                                    df_contri_file_nv_no_elegibles["razon"] = "Son de otro Contribuyente o cero o nulas"

                                if not df_contri_file_nv_x.empty:
                                    df_contri_file_nv_x = tired.concat([df_contri_file_nv_x, df_contri_file_nv_no_elegibles])

                                if df_contri_file_nv_x.empty:
                                    df_contri_file_nv_x = df_contri_file_nv_no_elegibles

                                df_contri_file_nv_x.fecha_emision = df_contri_file_nv_x.fecha_emision.astype(str)
                                df_contri_file_nv_x.fecha_emision = df_contri_file_nv_x.fecha_emision.str[:10]

                                _sql.jd.esquema = self.db.config.TB_PG_ESQUEMA_TEMPORAL
                                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_CARGAS_ARCHIVOS
                                _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                                self.db.get_reseto_tabla_estandar_jd(_sql)
                                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_DECLARACIONES_VALIDAS
                                _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                                self.db.get_reseto_tabla_estandar_jd(_sql)
                                df_contri_file_nv_x = df_contri_file_nv_x.drop(['formato'], axis=1)
                                start = timer()
                                _sql.jd.df = df_contri_file_nv_x
                                df_entran_para_nocruzan, df_contri_file_nv_x = self.set_reproceso_descartados(_sql)
                                if not df_entran_para_nocruzan.empty:
                                    df_contri_file = tired.concat([df_contri_file,df_entran_para_nocruzan])
                                _sql.jd.df = ''
                                limiteactual = self.db.get_scalar(_sql.get_limite_cara())
                                df_contri_file['indice'] = range(int(limiteactual), int(limiteactual)+len(df_contri_file))
                                df_contri_file['indice'] = df_contri_file['indice'].astype('Int64')
                                estadisticas["num_con_errores"] = int(len(df_contri_file_nv_x.index))
                                _his.num_excel_num_fails = int(estadisticas["num_con_errores"])
                                estadisticas["monto_analizar"] = df_contri_file['valor_retenido'].sum()
                                _his.monto_excel_identificado = estadisticas["monto_analizar"]
                                df_contri_file["usuario"] = _sql.jd.usuario
                                df_contri_file["numero_tramite"] = _sql.jd.tramite
                                df_contri_file["periodo_inicial"] = _sql.jd.periodo_inicial_org
                                df_contri_file["periodo_final"] = _sql.jd.periodo_final_org
                                df_contri_file = df_contri_file.drop(['formato'], axis=1)

                                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_CARGAS_ARCHIVOS
                                _sql.jd.df = df_contri_file
                                self.db.guardar_dataframe_jd(_sql)
                                _sql.jd.df = ''
                                # 1 guardando fallidos
                                _his.num_descartados = int(len(df_contri_file_nv_x.index))
                                if not df_contri_file_nv_x.empty:
                                    print(f" FILAS CON DIFICULTADES {self.db.uf.RED}  {len(df_contri_file_nv_x.index)}  en {str(fn)} {self.db.uf.RESET} ")

                                _sql.jd.tabla_relacional = self.db.config.TB_PG_DEV_CARGAS_ARCHIVOS_NV
                                _sql.jd.tabla_esquema = f"{_sql.jd.esquema}.{_sql.jd.tabla_relacional}"
                                _sql.jd.df = df_contri_file_nv_x
                                self.guardar_warp_jd(_sql, True)
                                _sql.jd.df = ''
                                end = timer()
                                _his.time_excel_a_db = str(timedelta(seconds=end-start))
                                estadisticas["guardado"] = 1
                                _inf.detener = False
                        else:
                            mensaje = "El archivo contiene fechas de emision incorrectas/valores de retencion no validos, por favor carga un listado actualizado!    "
                            _inf.agregar_razones({'mensaje': mensaje, "category": "archivo", "detener": True})
                            _inf.detener = True
                else:
                    mensaje = f"el archivo no contiene el numero de columnas esperado, es {self.db.config.NUM_COLUMNAS_ARCHIVO_RETENCION} -> {len(df_contri_file.columns)},  \n incluir las columnas {self.db.config.ARCHIVO_RETENCION_COLS}    "
                    _inf.agregar_razones({'mensaje': mensaje, "category": "archivo" , "detener": True})
                    _inf.detener = True
            else:
                _inf.agregar_razones({'mensaje': f"En el periodo solicitado el contribuyente {_sql.jd.contri} no dispone declaraciones mensuales ", "category": "archivo", "detener": True})
                _inf.detener = True
        except Exception as ex:
            traceback.print_stack()
            print(f"CARGA LISTADO {self.db.uf.RED}  ERR {ex}   {self.db.uf.RESET}")
            _inf.agregar_razones({'mensaje': f" {ex} ", "category": "archivo", "detener": True})
            _inf.detener = True
        _sql.jd.df = ''
        self.db.uf.his = _his
        self.db.uf.pi = _sql.jd
        self.db.uf.informante = _inf

        return estadisticas
