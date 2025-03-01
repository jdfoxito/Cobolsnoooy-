"""Estadisticas, desde Enero 2023
Funcionalidades:
  - estadisticas generales dle contri.

ESTANDAR PEP8

"""

from datos import InteraccionPG
from config import Config
from datetime import datetime
import pandas as pd


class Analiticas(InteraccionPG.Tabla):
    """
    Para obtener las estadisticas.
    """
    def __init__(self, uf):
        '''constructor inicial'''
        super().__init__(config=Config)
        self.uf = uf

    def preparar_dataframe(self, df):
        '''prepara dataframe'''
        df["contri"] = self.uf.pi.contri
        df["fecha_analisis"] = self.get_fecha_ymd()
        df["fecha_analisis"] = pd.to_datetime(df["fecha_analisis"])
        df["estado"] = 'INA'
        df["periodo_inicial"] = self.uf.pi.periodo_inicial
        df["periodo_final"] = self.uf.pi.periodo_final_org
        df["usuario"] = self.uf.pi.usuario
        df["numero_tramite"] = self.uf.pi.tramite
        return df

    def get_fecha_ymd(self) -> str:
        '''fecha año mes dia'''
        date_time = datetime.fromtimestamp(datetime.now().timestamp())
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_reseto_tabla_estandar(self):
        '''reseteo tabla estandar'''
        numero_veces = self.get_scalar(f"""select count(1)  veces
                                         from {self.uf.pi.tabla_esquema} where
                                        estado = 'INA' and contri
                                        = '{self.uf.pi.contri}' \
                                        and periodo_inicial =
                                        '{self.uf.pi.periodo_inicial}' and
                                        periodo_final =
                                        '{self.uf.pi.periodo_final_org}'; """)
        if numero_veces > 0:
            self.get_actualizar(f"""delete from {self.uf.pi.tabla_esquema}
                                    where contri = '{self.uf.pi.contri}'
                                    and periodo_inicial =
                                    '{self.uf.pi.periodo_inicial}' and
                                    periodo_final =
                                    '{self.uf.pi.periodo_final_org}' and
                                    estado = 'INA'; """)
        return 1

    def get_reseto_tabla_estandar_jd(self, _sql):
        '''reseteo tabla estandar'''
        numero_veces = self.get_scalar(f"""select count(1)  veces
                                             from {_sql.jd.tabla_esquema} where
                                            estado = 'INA' and
                                            contri = '{_sql.jd.contri}' \
                                            and periodo_inicial =
                                            '{_sql.jd.periodo_inicial}' and
                                            periodo_final =
                                            '{_sql.jd.periodo_final_org}' and
                                            usuario = '{_sql.jd.usuario}';""")
        if numero_veces > 0:

            self.get_actualizar(f"""delete from {_sql.jd.tabla_esquema}
                                 where contri = '{_sql.jd.contri}'
                                 and periodo_inicial =
                                 '{_sql.jd.periodo_inicial}' and
                                 periodo_final = '{_sql.jd.periodo_final_org}'
                                 and estado = 'INA' and
                                 usuario = '{_sql.jd.usuario}' ; """)

        return 1

    def get_fecha_ymd_hms(self) -> str:
        '''obtener fecha'''
        date_time = datetime.fromtimestamp(datetime.now().timestamp())
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def numero_procedimientos_contri(self):
        '''numero de procediminetos contri'''
        devuelve = self.get_scalar(f""" select count(1) from
                                     tramites.tra_tramites where
                                   codigo_clase_tramite in (26)  and
                                   codigo_tipo_tramite in (32)  and
                                   codigo_estado    in ('ASI','NUE')
                                    and numero_ruc= '{self.uf.pi.contri}'; """)
        sms = f"""El  contribuyente {self.uf.pi.contri} no tiene
                    tramites nuevos de CADENAS DE IVA  """
        return {'mensaje': sms,
                "category": "archivo",
                "devuelve": devuelve}, devuelve

    def numero_declas_periodo_contri(self):
        '''numero de declaraciones periodo contribuyente'''
        devuelve = self.get_scalar(f""" select count(1) from
                                         owbtar.owb_ods_declaraciones_104 where
                                        numero_identificacion  =
                                        '{self.uf.pi.contri}'
                    and (anio_fiscal || '-'  || mes_fiscal || '-01')::date
                    between  '{self.uf.pi.periodo_inicial}'::date  and
                    '{self.uf.pi.periodo_final}'::date;
                                            """)

        sms = f"""El  RUC {self.uf.pi.contri} no tiene declaraciones en el
                    periodo solicitado  """
        return {'mensaje': sms,
                "category": "archivo",
                "devuelve": devuelve}, devuelve

    def num_declas_mensuales_periodo(self):
        '''numero de declaraciones mensuales periodo'''
        devuelve = self.get_scalar(f""" select count(1) from
                                         owbtar.owb_ods_declaraciones_104 where
                                numero_identificacion = '{self.uf.pi.contri}'
                                and codigo_impuesto = 2011
            and (anio_fiscal || '-'  || mes_fiscal || '-01')::date
            between  '{self.uf.pi.periodo_inicial}'::date
            and '{self.uf.pi.periodo_final}'::date;
                                """)
        return devuelve

    def numero_terceros_periodo_contri(self):
        '''numero de terceros periodo'''
        devuelve = self.get_scalar(f""" select sum(conteo) from (
                                            select count(1) conteo from
                                         terceros.dev_iva_retencion_on_elec
                                        where identificacion_sujeto  =
                                        '{self.uf.pi.contri}' and
                                        fecha_emision between
                                        '{self.uf.pi.periodo_inicial}'
                and  (date_trunc('month', '{self.uf.pi.periodo_final}'::date) +
                          interval '1 month' - interval '1 day')::date
                     union
                    select count(1) from terceros.dev_iva_retencion_on_fi
                    where identificacion_sujeto  = '{self.uf.pi.contri}'
                    and fecha_emision between '{self.uf.pi.periodo_inicial}'
                and (date_trunc('month', '{self.uf.pi.periodo_final}'::date) +
                interval '1 month' - interval '1 day')::date) nupy""")
        sms = f"""El  RUC {self.uf.pi.contri} no tiene retenciones de terceros 
                    en el periodo solicitado   """
        return {'mensaje': sms, "category": "archivo",
                "devuelve": devuelve}, devuelve

    def monto_en_analisis(self):
        '''monto de analisis'''
        return self.get_scalar(f""" select sum(monto_analizar) from (
                                        select contri, periodo_inicial,
                                        periodo_final, sum(monto_analizar)
                                        monto_analizar
                                        from
                                        public.dev_estadistica_base  where
                                        usuario_actual ='{self.uf.pi.usuario}'
                                        group by 1,2,3)px; """)

    def num_contri_analisis(self):
        '''numero de contri cnaliais'''
        return self.get_scalar(f""" select count(distinct contri) from
                                    public.dev_estadistica_base
                                    where usuario_actual =
                                    '{self.uf.pi.usuario}' ; """)
