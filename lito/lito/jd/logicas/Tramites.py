"""Tramites, desde Enero 2023
Funcionalidades:
  - Sirve para el historial de tramites.

El analista ingresa,, un caso:
    +-------------------+-------------------+-------------------+
    | 179083231323001   | 2022-01-01        |     2022-12-31    |
    +-------------------+-------------------+-------------------+

COMPORTAMIENTO:

 - fn(get_previas_sql)                   tramites Previos del contri
                                         en cadenas de iva
 - fn(get_canadian)                      tramites Similares
                                        del contri en cadenas de iva

    +-------------------+-------------------+--------------------------+
    | Fecha             | Modifier          | Descripcion               |
    +-------------------+-------------------+--------------------------+
    | 20ENE2023         | jagonzaj          |   tramites previos        |
                                                y similares             |
    +-------------------+-------------------+---------------------------+

ESTANDAR PEP8
REVISADO CON SONARLINT 4.3.0
"""

from datos import Consultas


class Diarios:
    '''Generacion de tramites diarios'''
    def __init__(self, db):
        self.db = db
        self.cn = Consultas.Papel(db)

    def get_previas_sql(self):
        '''  tramites que son previos'''
        df_tramites = []
        longitud_tramites = 0
        df_tramites = self.db.get_vector(self.cn.get_sql_previas())
        df_tramites.fillna(value='', inplace=True)
        longitud_tramites = len(df_tramites.index)
        resultado = {
            "tramites": df_tramites.to_dict("records"),
            "longitud_tramites": longitud_tramites

        }
        return resultado

    def get_canadian(self):
        '''tramites similares que son asignados y nuevos,
        por pruebas se coloca : ASI NUE'''
        df_tramites = []
        consulta = self.cn.get_sql_similares()
        df_tramites = self.db.get_vector(consulta)
        df_tramites.fillna(value='', inplace=True)
        numero_tramites = len(df_tramites.index)
        resultado = {
            "tramites": df_tramites.to_dict("records"),
            "numero_tramites": numero_tramites
        }
        return resultado
