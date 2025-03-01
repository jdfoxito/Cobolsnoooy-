"""Tableros, desde Enero 2023
Funcionalidades:
  - Tableros.

ESTANDAR PEP8

"""


class MasConsultas:
    '''consultas particlaers'''
    def __init__(self, db):
        '''constructor principal'''
        self.db = db

    def get_sql_actividad_reciente(self):
        '''activiadad reciente'''
        return """ with thead as (
                        select *  from (
                            select usuario, max(num_acceso) num_acceso from
                            public.dev_accesos_portal where
                            fecha_ingreso::date = current_date group by 1
                        ) a1 inner join public.dev_accesos_portal b
                        using(usuario, num_acceso)
                    ) select *from thead a inner join
                    public.dev_usuario_cad_iva b
                    on lower(a.usuario) = lower(b.username)
                    order by fecha_ingreso desc limit 3 """

    def get_sql_top_ten_devs(self):
        '''top 10'''
        return """ select razon_social,
                    sum(distinct monto_a_devolver_calculado) devuelto from
                    dev_memoria_casos a
                    inner join rucsri.dev_iva_contris_llegan b
                    on a.contri = b.contri
                    group by 1 order by 2 desc limit 20; """

    def get_sql_cuadros(self):
        '''cuadro particulares'''
        return """ select
                    (select count (distinct contri) numero_contri
                        from dev_estadistica_base) numero_contri,
                    (select sum(distinct monto_a_devolver_calculado)
                        monto_a_devolver_calculado
                        from dev_memoria_casos)monto_a_devolver_calculado,
                    (select count (distinct numero_tramite) nuevos
                    from tramites.tra_tramites where codigo_estado
                    in ('ASI','NUE')  ) nuevos,
                    (select sum(distinct monto_analizar ) monto_analizar
                    from dev_estadistica_base) monto_analizar; """


