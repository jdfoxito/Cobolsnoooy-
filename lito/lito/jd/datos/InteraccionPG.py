"""BASE DE DATOS,
Funcionalidades:
Permite conectarse a una base de datos,oracle como postgres trabaja como un ORM

COMPORTAMIENTO:

 - fn(set_particula_live)  controla la informacion de cada analista concurrente
 - fn(get_vector)          devuelve un conjunto de datos sobre una consulta
                            hacia la base de datos proyectada con filtros,
                            como dataframe
 - fn(get_scalar)          devuelve un unico dato de una consulta a la
                            base de datos proyectada con filtros,como dataframe
 - fn(get_actualizar)      actualiza un dato en una tabla

+-------------------+-------------------+---------------------------------+
| Fecha             | Modifier          | Descripcion                     |
+-------------------+-------------------+---------------------------------+
| 12ENE2023         | jagonzaj          |   Se agregan funciones postgres |
| 14FEB2023         | jagonzaj          |   control de los parametros en  |
                                            memoria para cada usuario     |
+-------------------+-------------------+---------------------------------+
ESTANDAR PEP8

"""


from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy import sql
from sqlalchemy import text
import pandas as pd
import traceback
import json
import ast
from pathlib import Path
import numpy as np
from datetime import datetime
from decimal import *
import enum
import datetime


class NpEncoder(json.JSONEncoder):
    """
    sirve para codificar los elementos de un diccionario

    Raises:
        TypeError: por el momento ninguno, los tipos de datos posibles
        han sido cubiertos

    Returns:
        _type_: diccionario json sin novedades
    """

    def default(self, obj):
        '''construcor principal'''
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class DecimalEncoder(json.JSONEncoder):
    '''Encoder decimal'''
    def default(self, obj):
        '''construcntor principal'''        
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class PdEncoder(json.JSONEncoder):
    '''pandas encoder'''
    def default(self, obj):
        '''construcntor principal'''
        if isinstance(obj, pd.Timestamp):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class MultipleJsonEncoders():
    """
    Combine multiple JSON encoders
    """
    def __init__(self, *encoders):
        '''construccion principal'''
        self.encoders = encoders
        self.args = ()
        self.kwargs = {}

    def default(self, obj):
        '''construccion default'''
        for encoder in self.encoders:
            try:
                return encoder(*self.args, **self.kwargs).default(obj)
            except TypeError:
                pass
        raise TypeError(f'''Object of type {obj.__class__.__name__}
                                is not JSON serializable''')

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        enc = json.JSONEncoder(*args, **kwargs)
        enc.default = self.default
        return enc


class JsonDateEncoder(json.JSONEncoder):
    '''json encoder'''
    def default(self, o):
        '''construccion default'''        
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return super().default(o)


class JsonEnumEncoder(json.JSONEncoder):
    '''json enum encoder'''
    def default(self, o):
        '''construccion default'''        
        if isinstance(o, enum.Enum):
            return o.name
        return super().default(o)


class Enumm(enum.Enum):
    '''enumeracion'''
    X = enum.auto()


obj = {'time': datetime.datetime.now(), 'enum': Enumm.X}
encoder_var = MultipleJsonEncoders(JsonDateEncoder, DecimalEncoder)


class Tabla:
    """Caracteristicas Futuras version 1.0.1
    -------------
    - en estos proximos dias se incluye el proxy oracle db 11-MAR2024
    a 20-MAR-2024, en el constructor innicial
    dependiendo si es complementaria o no
    """
    __version__ = "1.0.0"

    def __init__(self, config):
        '''constructor inicial'''
        self.motor = create_engine(f'postgresql+psycopg2://{config.DB_DEV_USER}:{config.DB_DEV_PASS}@{config.DB_DEV_HOST}:5432/{config.DB_DEV_DB}', echo=False,  poolclass=QueuePool, pool_recycle=3600, pool_size=5, max_overflow=5)
        self.config = config

    def allowed_file(self, filename):
        '''extensiones permitidas'''
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in \
            set(self.config.EXTENSIONES_ALLOW)

    def is_valid_upload(self, upload) -> bool:
        ''' es una carga valida'''
        return Path(upload.filename).suffix.lower() in ['.jpg', '.jpeg']

    def get_df_from_pg(self, sql_revisar):
        '''consulta de datos'''
        df = pd.DataFrame()
        try:
            sql_query = sql.text(sql_revisar)
            with self.motor.connect() as conn:
                df = pd.read_sql(sql_query, conn)
        except Exception:
            traceback.print_exc()
        return df.copy()

    def get_actualizar(self, sql_revisar):
        '''actualizar campos'''
        valor = 0
        with self.motor.begin() as conn:
            results = conn.execute(text(sql_revisar))
            conn.commit
            try:
                if results.rowcount > 0:
                    valor = results.first()[0]
                else:
                    valor = 0
            except Exception as ex:
                print(ex)
                valor = 0
        return valor

    def get_scalar(self, sql_revisar):
        '''gest escalar'''
        valor = ''
        with self.motor.begin() as conn:
            results = conn.execute(text(sql_revisar))
            try:
                if results.rowcount > 0:
                    valor = results.first()[0]
                else:
                    valor = ''
            except Exception as ex:
                print(ex)
                valor = ''
        return valor

    def guardar_dataframe_pg(self, df, tabla, esquema) -> int:
        '''guardar informacion en tabla '''
        num_acceso = 0
        if not df.empty:
            num_acceso = df.to_sql(tabla,
                                   con=self.motor,
                                   if_exists='append',
                                   schema=esquema,
                                   index=False,
                                   chunksize=20000)
        return num_acceso

    def guardar_dataframe_jd(self, _sql) -> int:
        '''guardar dataframe'''
        df = _sql.jd.df.copy()
        num_acceso = 0
        if not df.empty:
            num_acceso = df.to_sql(_sql.jd.tabla_relacional,
                                   con=self.motor,
                                   if_exists='append',
                                   schema=_sql.jd.esquema,
                                   index=False,
                                   chunksize=20000)
        return num_acceso

    def get_vector(self, sql_revisar):
        '''conseguir vector'''
        df = pd.DataFrame()
        try:
            df = self.get_df_from_pg(sql_revisar)
        except Exception:
            traceback.print_exc()
        return df

    def get_vector_parse(self, sql_revisar):
        '''get vector parse'''
        argentina = 1
        try:
            df = self.get_vector(sql_revisar)
            result = df.to_json(orient="records")
            parsed = json.loads(result)
            argentina = json.dumps(parsed, indent=4)
        except Exception as ex:
            print(ex)
        return argentina

    def get_transformada(self, df):
        '''transformada'''
        df_bf = []
        longitud = 0
        if not df.empty:
            columnas = []
            for col in df.columns:
                columnas.append(col)
            for index, row in list(df.iterrows()):
                df_bf.append(dict(zip(columnas, row)))
                longitud += 1
                index = index * 1
        return df_bf, longitud

    def get_transformada_simple(self, df):
        '''transformada simple'''
        df_bf = []
        longitud = 0
        if not df.empty:
            columnas = []
            for i in range(len(df.columns)):
                columnas.append('c'+str(i))
            for index, row in list(df.iterrows()):
                df_bf.append(dict(zip(columnas, row)))
                longitud += 1
                index = index * 1
        return df_bf, longitud

    def get_lista_columnas(self, df):
        '''lista columna'''
        lista = []
        for i in range(len(df.columns)):
            lista.append('c'+str(i))
        return lista

    def get_faraday(self, sql_revisar):
        '''get faraday'''
        df = self.get_vector(sql_revisar)
        df.fillna('')
        df, longitud = self.get_transformada(df)
        return df, longitud

    def get_lorentz(self, df):
        '''transformacion'''
        df, longitud = self.get_transformada(df)
        return df, longitud

    def get_planck(self, df):
        '''get planck'''
        df, longitud = self.get_transformada_simple(df)
        return df, longitud

    def get_representante(self, representante):
        ''' representante'''
        if (representante):
            if len(representante) < 13 and len(representante) > 6:
                representante = representante+'001'
            elif len(representante) < 7:
                representante = ''
        else:
            representante = ''
        return representante

    def get_rellenar_cols(self, df_cambiar,  parametro1, fecha_hoy):
        df_cambiar["contri"] = parametro1
        df_cambiar["fecha_analisis"] = fecha_hoy
        df_cambiar["estado"] = 'INA'
        df_cambiar["fila"] = np.arange(len(df_cambiar))
        return df_cambiar

    def camara(self, diccionario):
        '''formateo cadena'''
        return json.dumps(diccionario, cls=encoder_var)

    def get_fecha_ymd_hms(self) -> str:
        '''horario'''
        date_time = datetime.fromtimestamp(datetime.now().timestamp())
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def set_particula_live(self, u, a, j, h, n, m, pivot) -> tuple:
        '''mantenimiento de la sesion'''
        num_acceso = -1
        mensaje = ""
        fecha_air = self.get_fecha_ymd_hms()
        sqla = f"""select * from public.dev_particulas_diarias where
                  usuario = '{u}'  and fecha_air_ini::date = current_date; """
        df_existe = self.get_vector(sqla)
        xdpt = {}
        try:
            per = 'df_periodos_talves'

            if j and isinstance(j["df_periodos_talves"], pd.DataFrame) and \
                    "df_periodos_talves" in j:
                j["df_periodos_talves"]["fecha_ini"] = \
                    j["df_periodos_talves"]["fecha_ini"].astype(str)
                j["df_periodos_talves"]["fecha_fin"] = \
                    j["df_periodos_talves"]["fecha_fin"].astype(str)
                xdpt = j[per][["fecha_ini", "fecha_fin"]].to_dict('records')
                j["df_periodos_talves"] = ''
        except Exception as ex1:
            print(f" IPg 270 ex1 {ex1}")

        if "adhesivos" in j:
            j["adhesivos"] = j["adhesivos"].replace("'", "_")

        if "df" in j:
            if isinstance(j["df"], pd.DataFrame):
                j["df"] = ''
        valep6 = "valores_arrastre_p6"
        if "valores_arrastre_p6" in j:
            if isinstance(j["valores_arrastre_p6"], list):
                for x in j["valores_arrastre_p6"]:
                    j[valep6][x] = j[valep6][x].replace("'", "_")

            if isinstance(j["valores_arrastre_p6"], str):
                j[valep6] = j[valep6].replace("'", "_")

        valep7 = "valores_analizados_p7"
        if "valores_analizados_p7" in j:
            if isinstance(j["valores_analizados_p7"], list):
                for x in j["valores_analizados_p7"]:
                    j[valep7][x] = j[valep7][x].replace("'", "_")

            if isinstance(j["valores_analizados_p7"], str):
                j[valep7] = j[valep7].replace("'", "_")

        val_a67 = "valores_analizados_6_7_am"
        if "valores_analizados_6_7_am" in j:
            if isinstance(j["valores_analizados_6_7_am"], list):
                for x in j["valores_analizados_6_7_am"]:
                    j[val_a67][x] = j[val_a67][x].replace("'", "_")

            if isinstance(j[val_a67], str):
                j[val_a67] = j[val_a67].replace("'", "_")
        condicion_nav = ""

        if len(n) > 0:
            condicion_nav = f", nav = '{json.dumps(n)}'"

        if df_existe.empty:
            if pivot == "ingreso":
                sqla = f"""delete from public.dev_particulas_diarias where
                            usuario = '{u}'  and
                            fecha_air_ini::date < current_date; """
                self.get_actualizar(sqla)
                ldf = {"usuario": [u],
                       "acceso": [int(a)],
                       "fecha_air_ini": [fecha_air],
                       "jd": [self.camara(j)],
                       "his": [self.camara(h)],
                       "nav": [self.camara(n)],
                       "dpt": [self.camara(xdpt)],
                       "reingreso": [0], "agente": [str(m)]}
                df = pd.DataFrame.from_dict(ldf)
                if not df.empty:
                    num_acceso = df.to_sql("dev_particulas_diarias",
                                           con=self.motor,
                                           if_exists='append',
                                           schema="public",
                                           index=False,
                                           chunksize=10)
        else:
            match pivot:
                case "ingreso":
                    num_acceso_comp = int(df_existe['acceso'].values[0])
                    agente = str(df_existe['agente'].values[0])
                    if num_acceso_comp < int(a):
                        mensaje = f"""Su sesión en su otra ventana/navegador
                                        {agente} se cerrará!"""
                    sqla = f"""update public.dev_particulas_diarias set
                               acceso = {a}, fecha_air_live= '{fecha_air}',
                               jd = '{self.camara(j)}',
                               his = '{self.camara(h)}' {condicion_nav},
                                dpt='{self.camara(xdpt)}',
                                reingreso=  reingreso + 1, agente = '{m}'
                                where usuario = '{u}';"""
                    if int(a) > 0:
                        self.get_actualizar(sqla)

                case "actualizar":
                    sqla = f""" update public.dev_particulas_diarias
                                set  fecha_air_live = '{fecha_air}',
                                jd = '{self.camara(j)}',
                                his = '{self.camara(h)}'  {condicion_nav},
                                dpt='{self.camara(xdpt)}',  agente = '{m}'
                                where usuario = '{u}' and acceso = {a}; """

                case "recargar":
                    try:
                        peri = "df_periodos_talves" 
                        j = df_existe['jd'].values[0]
                        if peri in j:
                            j[peri] = df_existe['dpt'].values[0]
                            j[peri] = pd.json_normalize(j[peri])

                        if "adhesivos" in j:
                            j["adhesivos"] = j["adhesivos"].replace("_", "'")

                        valp6 = "valores_arrastre_p6"
                        if "valores_arrastre_p6" in j:
                            if isinstance(j["valores_arrastre_p6"], list):
                                for x in j["valores_arrastre_p6"]:
                                    j[valp6][x] = j[valp6][x].replace("_", "'")

                        valp7 = "valores_arrastre_p7"
                        if "valores_analizados_p7" in j:
                            if isinstance(j["valores_analizados_p7"], list):
                                for x in j["valores_analizados_p7"]:
                                    j[valp7][x] = j[valp7][x].replace("_", "'")

                        val67 = "valores_analizados_6_7_am"
                        if "valores_analizados_6_7_am" in j:
                            if isinstance(j[val67], list):
                                for x in j[val67]:
                                    j[val67][x] = j[val67][x].replace("_", "'")

                        h = df_existe['his'].values[0]
                        n = df_existe['nav'].values[0]
                        num_acceso = int(df_existe['acceso'].values[0])

                        if num_acceso > a:
                            num_acceso = -3
                            a = -3
                        else:
                            a = num_acceso
                    except Exception as ex:
                        print(f"******* 186 ex {ex}")
                        num_acceso = -2

        if int(a) > 0:
            try:
                self.get_actualizar(sqla)
            except Exception as ex:
                print(f"IPG  383 ex {ex}")
            num_acceso = a
        else:
            num_acceso = -1
        return num_acceso, j, h, n, mensaje
