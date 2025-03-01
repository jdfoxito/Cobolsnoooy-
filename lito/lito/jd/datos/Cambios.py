"""Consultas, desde Enero 2023
Funcionalidades:
  - Consuultas a la base para postgres.

ESTANDAR PEP8

"""
from jd.ayudante.Celebridades import Navegante


class Afectacion:
    '''consultas varias'''
    nav: Navegante = Navegante({})

    def __init__(self, jd):
        '''constructor principal'''
        self.jd = jd

    def upd_sql_memoria_salvada(self):
        '''pantalla principal'''
        return f""" update {self.jd.tabla_esquema} set estado = 'SAV',
                    idmemoria =  {self.jd.memoria}
                    where estado = 'INA' and contri = '{self.jd.contri}' and
                    periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_final}'  """

    def get_sql_ultima_memoria_ingresado(self):
        '''ultima memoria ingresada'''
        return f""" select max(idmemoria) from public.dev_memoria_casos where
                        contri = '{self.jd.contri}' and
                        periodo_inicial = '{self.jd.periodo_inicial}' and
                        periodo_final = '{self.jd.periodo_final}'
                """

    def upd_sql_diez_once(self):
        '''Actualizaciones'''
        if str(self.jd.el_diez) == '':
            self.jd.el_diez = 0

        if str(self.jd.el_once) == '':
            self.jd.el_once = 0

        return f""" update temporal.dev_cuadro_liquidacion
                    set valor = {self.jd.el_diez}
                        where contri = '{self.jd.contri}' and
                        periodo_inicial = '{self.jd.periodo_inicial}' and
                        periodo_final = '{self.jd.periodo_finalisima}' and
                        fila = 10 and estado = 'INA'  and
                        usuario = '{self.jd.usuario}';

                    update temporal.dev_cuadro_liquidacion set
                        valor = {self.jd.el_once}
                        where contri = '{self.jd.contri}' and
                        periodo_inicial = '{self.jd.periodo_inicial}' and
                        periodo_final = '{self.jd.periodo_finalisima}' and
                        fila = 11 and estado = 'INA'  and
                        usuario = '{self.jd.usuario}';
                """

    def upd_sql_estadisticas_pre_informe(self):
        '''estadistica pre informe'''
        return f""" update temporal.dev_resumen_cadena set
                    mayores = {self.jd.mayoriza_ajuste},
                    nocruzan = {self.jd.no_sustentado}
                        where contri = '{self.jd.contri}'
                        and periodo_inicial = '{self.jd.periodo_inicial}' and
                        periodo_final = '{self.jd.periodo_finalisima}' and
                        numero_adhesivo = '{self.jd.adhesivo}'  and
                        usuario = '{self.jd.usuario}'
                        and estado = 'INA';
                """

    def upd_sql_tramite_aprobado(self):
        '''pantalla tramites'''
        consulta = ''
        match (self.nav.perfil):
            case 'Analista': consulta = f"""update public.dev_memoria_casos
                                            set estado = 'FIN',
                                            time_actualiza_memoria =
                                            current_timestamp,
                                            supervisor_marca =
                                            '{self.jd.usuario}'
                                            where idmemoria
                                            = {self.jd.memoria}    """
            case 'Supervisor': consulta = f"""update public.dev_memoria_casos
                                              set estado = 'APR' ,
                                              time_actualiza_memoria =
                                              current_timestamp,
                                              supervisor_marca =
                                              '{self.jd.usuario}' where
                                              idmemoria = {self.jd.memoria} """
        return consulta

    def upd_sql_tramite_aprobado_3ra(self):
        '''aprobado primera instancia'''
        consulta = ''
        match (self.nav.perfil):
            case 'Analista': consulta = f""" update public.dev_memoria_casos
                                                set estado = 'BOR',
                                                time_actualiza_memoria =
                                                current_timestamp,
                                                supervisor_marca =
                                                '{self.jd.usuario}' where
                                                idmemoria= {self.jd.memoria}"""
            case 'Supervisor': consulta = f"""update public.dev_memoria_casos
                                              set estado = 'SAV',
                                              time_actualiza_memoria =
                                              current_timestamp,
                                              supervisor_marca =
                                              '{self.jd.usuario}' where
                                              idmemoria = {self.jd.memoria} """

        return consulta

    def upd_sql_tramite_devolver(self):
        '''tramite a devolver'''
        consulta = ''
        match (self.nav.perfil):
            case 'Analista': consulta = f"""update public.dev_memoria_casos
                                            set estado = 'SAV',
                                            time_actualiza_memoria =
                                            current_timestamp,
                                            supervisor_marca =
                                            '{self.jd.usuario}' where
                                            idmemoria = {self.jd.memoria}  """
            case 'Supervisor': consulta = f"""update public.dev_memoria_casos
                                              set estado = 'BOR',
                                              time_actualiza_memoria =
                                              current_timestamp,
                                              supervisor_marca =
                                              '{self.jd.usuario}' where
                                              idmemoria = {self.jd.memoria} """
        return consulta
