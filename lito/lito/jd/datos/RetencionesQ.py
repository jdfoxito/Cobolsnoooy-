"""Consultas, desde Enero 2023
Funcionalidades:

  - Consuultas a la base para postgres.


ESTANDAR PEP8

"""


from datetime import datetime, timedelta


class Terceros:
    '''consultas de los terceros que reportan al contri'''

    def __init__(self, jd):
        self.jd = jd
        self.estado = 'INA'

    def get_sql_posible_ffpv(self):
        '''posible ffpv'''
        return f""" select codigo_autorizacion autorizacion,
                    numero_ruc::varchar agente_retencion,
                    '{self.jd.secuencia_tercero}'::int comprobante,
                    '{self.jd.fecha_tercero}' fecha_emision, '' es_ffpv
                    from inter.dev_iva_autoriza_emision
                    where id_tipo_documento = 7
                    and codigo_autorizacion = '{self.jd.autorizacion_tercero}'
                    and numero_ruc = '{self.jd.tercero}'
                    and '{self.jd.secuencia_tercero}'::int between
                    numero_inicial_ia and numero_final_ia
                    and '{self.jd.fecha_tercero}'::date  between
                    fecha_inicio_detalle and fecha_fin_detalle
                """

    def get_sql_informe_retencion_ing_sumarizado(self, z):
        '''    #para obtener ingresados sumarizados'''
        return f""" select extract(year from fecha_emision) anio,
                    extract(month from fecha_emision) mes,
                    sum(valor_retenido) ingresados
                     from temporal.dev_cargas_archivos where contri = '{z}'
                        and periodo_inicial = '{self.jd.periodo_inicial}' and
                        periodo_final = '{self.jd.periodo_final}' and
                        usuario = '{self.jd.usuario}'
                        and estado = '{self.estado}'
                        group by 1,2; """

    def get_sql_informe_retencion_num_filas(self, z):
        '''# para obtener numero de filas'''
        return f"""select count(1) from
                     temporal.dev_informe_retencion where contri = '{z}'
                    and estado='INA'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_final}' and
                    usuario = '{self.jd.usuario}'; """

    def get_lista_indices(self, auto, valr):
        '''lista indices'''
        return f"""  select  count(distinct numero_documento_sustento) from
                    terceros.dev_iva_retencion_on_elec
                    where numero_autorizacion = '{auto}' and
                    val_retenido = {valr} and
                    identificacion_sujeto = '{self.jd.contri}'
                    union
                    select  count(distinct numero_serie_sec_compr) from
                    terceros.dev_iva_retencion_on_fi
                    where numero_autorizacion = '{auto}' and 
                    val_retenido = {valr} and
                    identificacion_sujeto = '{self.jd.contri}'
                        """

    def get_sql_listado_explora_parcial(self) -> str:
        '''listado exploracion parcial'''
        condicion = ' and length(autorizacion) > 20 ' if self.jd.and_errante == 'E' else ' and length(autorizacion) < 20 '
        return f""" select extract(year from fecha_emision)::varchar anio,
                    extract(month from fecha_emision)::varchar mes,
                        count(1) conteo
                         from temporal.dev_cargas_archivos where
                        fecha_emision::date between '{self.jd.periodo_inicial}'
                        and '{self.jd.periodo_final}'
                        and periodo_inicial = '{self.jd.periodo_inicial_org}'
                        and periodo_final = '{self.jd.periodo_final_org}'
                        and contri = '{self.jd.contri}' and estado = 'INA' and
                        usuario = '{self.jd.usuario}'
                        {condicion}
                        group by  1,2 having count(1) > 0;
                    """

    def get_sql_declaraciones_validas_inf(self):
        '''declaraciones validas'''
        return f""" select anio_fiscal anio, mes_fiscal mes,
                    retenciones_fuente_iva, numero_adhesivo, codigo_impuesto
                      from temporal.dev_declaraciones_validas where
                    contri = '{self.jd.contri}' and estado = 'INA'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_finalisima}'
                    and usuario = '{self.jd.usuario}'
                """

    def get_sql_listado_out_range(self):
        '''descartados'''
        return f"""
                    select agente_retencion, fecha_emision, serie, comprobante,
                    autorizacion, porcentaje_iva, porcentaje_retencion_iva,
                    valor_retenido, fecha_carga::varchar fecha_carga,
                    razon --, string_agg(distinct razon,',') razon
                      from temporal.dev_cargas_archivos_nv
                    where contri = '{self.jd.contri}' and
                    periodo_inicial = '{self.jd.periodo_inicial}'
                    and periodo_final = '{self.jd.periodo_final}'
                    and estado='INA'  and usuario = '{self.jd.usuario}';
                    --group by 1,2,3,4,5,6,7,8,9
                    ;
                """

    def get_sql_adhesivos_parciales(self):
        '''adhesivos parciales'''
        return f""" select  codigo_impuesto, anio_fiscal, mes_fiscal
                         from  owbtar.owb_ods_declaraciones_104 where
                        numero_adhesivo in  ({self.jd.adhesivos}) and
                        numero_identificacion = '{self.jd.contri}';
                """

    def numero_declas_semestrales(self):
        '''numero de declaraciones semestarles'''
        return f"""select count(1) from owbtar.owb_ods_declaraciones_104
                    where  codigo_impuesto = 2021
                      and numero_identificacion  = '{self.jd.contri}'
                      and (anio_fiscal || '-'  || mes_fiscal || '-01')::date
                      between  '{self.jd.periodo_inicial}'::date
                      and '{self.jd.periodo_final}'::date;

                                """

    def get_filtros_parciales_clase(self):
        '''filtros parciales clase'''
        estado = "" if self.jd.procedencia == 'externa' else "INA"
        condicion_periodos = ''
        condicion_estado = ''
        condicion_memoria = f' and idmemoria = {self.jd.memoria}'
        if estado == 'INA':
            condicion_estado = " and estado = 'INA'"
            condicion_memoria = ''
            condicion_periodos = f" and periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}' "
        return condicion_estado, condicion_memoria, condicion_periodos

    def get_sql_informe_retencion(self, z, a, b):
        '''informe de retencion
         # 1 para obtener una pagina del informe de retencion
                # 22 estado =   self.get_estados()
                # if self.jd.procedencia == 'externa' else "INA"
        '''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        condicio_numerado = f""" and numerado between {a} and {b} """
        if a == -1 and b == -1:
            condicio_numerado = ""
        return f""" select anio, mes, to_char(fecha_emi_retencion,'yyyy-mm-dd')
                    fecha_emi_retencion,
                    to_char(fecha_emi_ret,'yyyy-mm-dd hh:mm:ss') fecha_emi_ret,
                    secuencial_retencion, autorizacion,
                    valor_retencion, diferencia, valor_retenido_administracion,
                    valor_retenido_listado, es_fantasma, es_fallecido, es_ffpv,
                    cruza, conclusion, no_reporta,
                    ruc_contrib_informan, razon_social, conteo, contri,usuario,
                    periodo_inicial, periodo_final, fecha_analisis, estado,
                    numero_tramite, numerado
                      from temporal.dev_informe_retencion where contri = '{z}'
                    and usuario = '{self.jd.usuario}'
                        {condicion_estado}   {condicion_memoria}
                        {condicion_periodos}
                        {condicio_numerado}; """

    def get_sql_listado_parcial(self):
        '''listado parcial'''
        condicion = ' and length(autorizacion) > 20 ' if self.jd.and_errante == 'E' else ' and length(autorizacion) < 20 '
        return f""" with thead as (
                    select  agente_retencion::varchar agente_retencion,
                    fecha_emision::date fecha_emision,
                    comprobante::varchar comprobante,
                    autorizacion::varchar autorizacion,
                    indice, round(valor_retenido, 2) valor_retenido,
                    contri::varchar contri
                     from  temporal.dev_cargas_archivos
                     where contri = '{self.jd.contri}'  and fecha_emision::date
                    between  '{self.jd.periodo_inicial}'
                    and  '{self.jd.periodo_final}'
                    and periodo_inicial = '{self.jd.periodo_inicial_org}'
                    and periodo_final = '{self.jd.periodo_final_org}'
                    and estado = 'INA' and usuario = '{self.jd.usuario}'
                    {condicion}
                )select a.*,case when b.fecha_baja_fantasma is null
                    then '' else 'si' end es_fantasma,
                    case when c.fecha is null then '' else 'si' end
                      es_fallecido from thead  a left join
                    inter.dev_fantasmas b
                        on a.agente_retencion = b.identificacion
                        -- and a.fecha_emision between
                        -- fecha_alta_fantasma and fecha_baja_fantasma
                    and agente_retencion is not null
                    and length(agente_retencion)>0
                    left join inter.dev_fallecidos_diferencial c
                    on a.agente_retencion = c.numero_ruc
                    and a.fecha_emision >= c.fecha
                """

    def get_sql_administracion_parcial(self):
        '''administracion parcial'''
        consulta = f""" select  distinct numero_ruc_emisor::varchar
                        agente_retencion,identificacion_sujeto::varchar contri,
                        fecha_emision::date fecha_emision,
                        secuencial::varchar comprobante,
                        numero_autorizacion::varchar  autorizacion,
        round(val_retenido, 2) valor_retenido,
        COALESCE(numero_documento_sustento::varchar, '')
        numero_documento_sustento ,
        string_agg(  distinct upper(razon_social),',') razon_social
        from  terceros.dev_iva_retencion_on_elec
        where identificacion_sujeto = '{self.jd.contri}'
        and fecha_emision::date
        between  '{self.jd.periodo_inicial}'  and  '{self.jd.periodo_final}'
        and length(numero_autorizacion) >20
        group by  1,2,3,4,5,6,7
        order by  contri, agente_retencion, autorizacion, comprobante asc
        """
        if self.jd.and_errante == 'F':
            consulta = f"""select  distinct numero_ruc_emisor::varchar
                            agente_retencion,
                            identificacion_sujeto::varchar contri,
                            fecha_emision::date fecha_emision,
                            secuencial::varchar comprobante,
                            numero_autorizacion  autorizacion,
                            round(val_retenido, 2) valor_retenido,
                            COALESCE(numero_serie_sec_compr::varchar, '')
                            numero_documento_sustento,
                            string_agg(  distinct upper(razon_social),',')
                            razon_social
                        from  terceros.dev_iva_retencion_on_fi
                              where identificacion_sujeto ='{self.jd.contri}'
                              and fecha_emision::date
                              between '{self.jd.periodo_inicial}'
                              and  '{self.jd.periodo_final}'
                        and length(numero_autorizacion) between  1 and 20
                        group by  1,2,3,4,5,6,7
                        order by  contri, agente_retencion, autorizacion,
                        comprobante asc

            """
        return consulta


class Chain:
    '''para cadenas'''

    def __init__(self, jd):
        '''cadena construcotr inicial'''
        self.jd = jd

    def get_sql_cadena_iva_existe(self) -> str:
        '''cadena iva existe'''
        return f""" select count(1)
                        from temporal.dev_cad_iva_procesa where contri = '{self.jd.contri}' and estado = 'INA'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and  periodo_final = '{self.jd.periodo_final}' and usuario = '{self.jd.usuario}' """

    def get_sql_cadena_iva(self) -> str:
        '''cadena de iva'''
        return f""" select distinct camino, a.anio_fiscal anio, a.mes_fiscal mes, a.impuesto_causado, a.ct_mes_actual, a.sct_adquisicion_mesanterior,
                        a.sct_retenciones_mesanterior,b.valor_retencion valor_retencion_valida, 
                        0 ct_adq_proximo_mes, 0 ct_ret_proximo_mes, 0 total_impuesto_a_pagar, 0 retenciones_a_devolver, tot_impuesto_pagar_x_percepcion
                        ,0 calculo_ct_adq, 0 calculo_ct_ret, diferencia_arr_ct,	diferencia_x_ct,  diferencia_adquisiciones, diferencia_retenciones, ajuste_x_adquisiciones
                        ,sct_x_adquisiciones,	sct_x_retenciones
                        from  temporal.dev_declaraciones_validas a
                            inner join  temporal.dev_resultado_analisis_retencion b using(contri, estado,periodo_inicial, periodo_final, usuario)
                            where contri = '{self.jd.contri}' and a.anio_fiscal::int = b.anio and a.mes_fiscal::int = b.mes
                            and  a.estado = 'INA'  and numero_adhesivo in ({self.jd.adhesivos})  and b.estado = 'INA'
                            and periodo_inicial = '{self.jd.periodo_inicial}' and  periodo_final = '{self.jd.periodo_finalisima}' and usuario = '{self.jd.usuario}'
                            order by 2 asc, 3 asc;
                """

    def get_sql_cadena_iva_procesado(self) -> str:
        '''cadena iva procesada'''
        return f""" select camino, anio, mes, impuesto_causado, ct_mes_actual,
                    sct_adquisicion_mesanterior, sct_retenciones_mesanterior,
                    valor_retencion_valida, ct_adq_proximo_mes,
                    ct_ret_proximo_mes, total_impuesto_a_pagar,
                    retenciones_a_devolver, tot_impuesto_pagar_x_percepcion,
                    calculo_ct_adq, calculo_ct_ret, diferencia_arr_ct,
                    diferencia_x_ct, diferencia_adquisiciones,
                    diferencia_retenciones, ajuste_x_adquisiciones,
                    sct_x_adquisiciones, sct_x_retenciones from
                    temporal.dev_cad_iva_procesa
                    where contri = '{self.jd.contri}' and estado = 'INA'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_finalisima}'
                    and usuario = '{self.jd.usuario}';
                """

    def get_sql_razon_social_(self):
        '''razon social'''
        if len(self.jd.contri) == 10:
            self.jd.contri = self.db.uf.costelo(self.jd.contri)
        return f"""   select razon_social from rucsri.dev_iva_contri where numero_ruc = '{self.jd.contri}'; """

    def get_sql_supervisores_(self):
        '''supervisores'''
        return f"""
                    select distinct supervisor nombre from public.dev_usuario_cad_iva where username = '{self.jd.usuario}'
                """

    def get_sql_periodos_analizados(self):
        return f"""select distinct a.anio, a.mes
                          from temporal.dev_resultado_analisis_retencion a inner join  temporal.dev_declaraciones_validas b using(contri,estado, periodo_inicial, periodo_final, usuario )
                        where contri = '{self.jd.contri}' and estado='INA'
                        and periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}' and usuario = '{self.jd.usuario}'
                        and a.anio = b.anio_fiscal::int and a.mes = b.mes_fiscal::int
                        order by 1 asc, 2 asc;
                """

    def get_sql_dividir_adq_ret(self):
        return f"""select sct_adquisicion_mesanterior || ',' ||	sct_retenciones_mesanterior dividir from (
                                                select anio, mes, sct_adquisicion_mesanterior ,	sct_retenciones_mesanterior  from temporal.dev_pre_cadena_iva
                                                where contri = '{self.jd.contri}' and estado='INA'
                                                and periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}'  and usuario = '{self.jd.usuario}'
                                                order by 2 asc, 2 asc limit 1) as1;
                                                """

    def get_sql_snt_datos_cadena(self):
        return f""" select fecha_ingreso, coalesce(monto_a_devolver::float,0) monto_a_devolver, sum(coalesce(monto_solicitado::float,0)) monto_solicitado
                        from tramites.tra_tramites a inner join tramites.tra_detalles_tramite b on a.id_tramite = b.id_tramite
                            where numero_ruc ='{self.jd.contri}' and numero_tramite = '{self.jd.tramite}'
                            group by 1,2;
                """

    def get_sql_num_veces_pre_cad_iva(self):
        return f"""select count(1)  veces from temporal.dev_pre_cadena_iva where estado = 'INA' and contri = '{self.jd.contri}'
                        and periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}' and usuario = '{self.jd.usuario}'  """

    def get_sql_borrar_pre_cad_iva(self):
        return f""" delete from temporal.dev_pre_cadena_iva  where contri = '{self.jd.contri}' and estado = 'INA'  
                        and periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}' and usuario = '{self.jd.usuario}'  """


class Excel(Terceros):
    '''clase excel de terceros'''
    autorizacion = ''
    tipo = ''

    def __init__(self, jd):
        '''consttructor princiapl'''
        self.jd = jd

    def get_sql_cadena_iva_proc_reset(self) -> str:
        return f""" delete from temporal.dev_cad_iva_procesa where contri = '{self.jd.contri}' and estado = 'INA'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and  periodo_final = '{self.jd.periodo_finalisima}'  and usuario = '{self.jd.usuario}' """

    def get_sql_caso_parecido(self):
        return f"""
                        select distinct usuario, fecha_analisis::date::varchar fecha_analisis, b.nombre, b.cargo, b.email, b.departamento, a.numero_tramite
                            from public.dev_memoria_casos a inner join public.dev_usuario_cad_iva b on a.usuario = b.username
                                where estado in ('SAV','APR','FIN') and contri = '{self.jd.contri}' and b.id not in (155,154,153,147)
                                and periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}' limit 1;
                """

    def get_posible_autorizacion(self):
        sql = f"select  count(1) existe  from terceros.dev_iva_retencion_on_fi where numero_autorizacion = '{self.autorizacion.strip()}'; "
        if self.tipo == "ELEC":
            sql = f"select  count(1) existe  from terceros.dev_iva_retencion_on_elec where numero_autorizacion = '{self.autorizacion.strip()}'; "
        return sql

    def get_sql_retenciones_propias_subjetivas(self):
        return f""" select distinct numero_autorizacion autorizacion from terceros.dev_iva_retencion_on_elec where identificacion_sujeto = '{self.jd.contri}'
                        and fecha_emision between '{self.jd.periodo_inicial}' and '{self.jd.periodo_final}'
                    union
                    select distinct  numero_autorizacion autorizacion from terceros.dev_iva_retencion_on_fi where identificacion_sujeto = '{self.jd.contri}'
                        and fecha_emision between '{self.jd.periodo_inicial}' and '{self.jd.periodo_final}'

                """

    def get_limite_cara(self):
        '''limite de carga'''
        return """select coalesce(max(indice),0)+1  limite
                from temporal.dev_cargas_archivos"""


class Contri:
    '''informacion del contri en general'''
    representante = ''
    tipo = ''

    def __init__(self, jd):
        '''constructor principal'''
        self.jd = jd

    def es_tramite_tipo_inconsistent(self):
        '''tipo inconsistente'''
        return f"""select distinct a.codigo_clase_tramite, a.codigo_tipo_tramite t1,c.nombre_tipo_tramite tipo1,  b.codigo_tipo_tramite t2, d.nombre_tipo_tramite tipo2
                    from tramites.tra_tramites a inner join tramites.tra_detalles_tramite b using(id_tramite, codigo_clase_tramite)
                            left join tramites.tra_tipos_tramite c on c.codigo_tipo_tramite = a.codigo_tipo_tramite and c.codigo_clase_tramite = a.codigo_clase_tramite
                            left join tramites.tra_tipos_tramite d on d.codigo_tipo_tramite = b.codigo_tipo_tramite and d.codigo_clase_tramite = a.codigo_clase_tramite
                            where numero_ruc = '{self.jd.contri}' and    a.codigo_clase_tramite in (26) and a.codigo_tipo_tramite <> b.codigo_tipo_tramite
                                and codigo_estado in ('ASI','NUE') limit 1;
                   """

    def es_fantasma(self):
        '''es fantasma'''
        return f""" 	select count(1) numero from inter.dev_fantasmas
                               where identificacion = '{self.jd.usuario}'
                                    and fecha_alta_fantasma = '{self.jd.periodo_inicial}' and fecha_baja_fantasma = '{self.jd.periodo_final}'; """

    def get_info_representante(self):
        '''informacion representante'''
        return f"""select coalesce(razon_social,'') razon_social from rucsri.dev_iva_contri where numero_ruc = '{self.representante}';"""

    def get_contri_his(self):
        '''contri historico'''
        return f"""select numero_identificacion, fecha_inicio::varchar fecha_inicio, coalesce(fecha_fin::varchar,', la actualidad')::varchar fecha_fin
                            from  rucsri.dev_iva_contri_hist where numero_identificacion = '{self.jd.contri}' limit 1;"""

    def get_sql_contribuyente(self):
        '''informacion del contri'''
        return f"""   with thead as (
                        select numero_ruc, razon_social, representante_legal,  ubicacion_geografica, obligado,
                                            clase_contribuyente, substr(ubicacion_geografica,1,3)::int provinciacod,
                                            descripcion provincia, estructura_organizacional,
                                            substr(estructura_organizacional,1,1) letra
                        from  rucsri.dev_iva_contri a left join adm.adm_ubicaciones_geograficas aa
                                        on aa.codigo = substr(a.ubicacion_geografica,1,3)
                                        where numero_ruc =  '{self.jd.contri}'
                    )select *,
                                case  when  letra = 'Q' then 'ZONA 9'
                                    when  letra = 'I' then 'ZONA 1'
                                    when  letra = 'T' then 'ZONA 3'
                                    when  letra = 'R' then 'ZONA 5'
                                    when  letra = 'L' then 'ZONA 7'
                                    when  letra = 'M' then 'ZONA 4'
                                    when  letra = 'N' then 'ZONA 2'
                                    when  letra = 'S' then 'DIRECCION NACIONAL'
                                    when  letra = 'A' then 'ZONA 6'
                                    when  letra = 'G' then 'ZONA 8'
                                    when  letra =  '' THEN 'NO DEFINIDO'
                                end jurisdiccion from thead;
                    """

    def get_sql_tramites_nuevos_periodo(self):
        '''tramites nuevos periodo'''
        return f"""with ta as (

                        select  distinct b.anio_fiscal, b.mes_fiscal, count(distinct numero_tramite) similares
                                from tramites.tra_tramites a inner join tramites.tra_detalles_tramite b using(id_tramite, codigo_clase_tramite, codigo_tipo_tramite)
                                inner join  tramites.tra_clases_tramite c on c.codigo_clase_tramite = a.codigo_clase_tramite
                                inner join  tramites.tra_tipos_tramite d on d.codigo_clase_tramite = a.codigo_clase_tramite and d.codigo_tipo_tramite = a.codigo_tipo_tramite
                                inner join  tramites.tra_subtipos_tramite e on e.codigo_clase_tramite = a.codigo_clase_tramite and e.codigo_tipo_tramite = a.codigo_tipo_tramite
                                    and e.codigo_sub_tipo_tramite = b.codigo_sub_tipo_tramite
                                where
                                    a.codigo_clase_tramite in (26)  and b.codigo_tipo_tramite in (32) and b.codigo_sub_tipo_tramite in (1,2)
                                    and numero_ruc = '{self.jd.contri}' and codigo_estado   not in ('ASI','NUE')
                                    and (b.anio_fiscal || '-' || b.mes_fiscal || '-01')::date between  ('{self.jd.periodo_inicial}' )::date 
                                    and  (date_trunc('month', '{self.jd.periodo_final_org}'::date) +     interval '1 month' - interval '1 day')::date
                                group by 1,2
                    ),
                    tb as (
                            select  distinct a.codigo_clase_tramite, b.codigo_tipo_tramite, count(distinct numero_tramite) previos
                                    from tramites.tra_tramites a inner join tramites.tra_detalles_tramite b using(id_tramite, codigo_clase_tramite, codigo_tipo_tramite)
                                    inner join  tramites.tra_clases_tramite c on c.codigo_clase_tramite = a.codigo_clase_tramite
                                    inner join  tramites.tra_tipos_tramite d on d.codigo_clase_tramite = a.codigo_clase_tramite and d.codigo_tipo_tramite = a.codigo_tipo_tramite
                                    inner join  tramites.tra_subtipos_tramite e on e.codigo_clase_tramite = a.codigo_clase_tramite and e.codigo_tipo_tramite = a.codigo_tipo_tramite
                                        and e.codigo_sub_tipo_tramite = b.codigo_sub_tipo_tramite
                                    where
                                        a.codigo_clase_tramite in (26)  and e.codigo_tipo_tramite in (32) and e.codigo_sub_tipo_tramite in (1,2)
                                        and numero_ruc = '{self.jd.contri}' and codigo_estado  not in ('ASI','NUE')
                                    group by 1,2
                        ), t_declas as (
                            select distinct numero_identificacion, a.anio_fiscal, a.mes_fiscal, fecha_recepcion from ta a inner join OWBTAR.OWB_ODS_DECLARACIONES_104  b
                                    on a.anio_fiscal = b.anio_fiscal::int and a.mes_fiscal = b.mes_fiscal::int
                                    and b.numero_identificacion = '{self.jd.contri}' and b.sustitutiva_original = 'ORIGINAL'
                            )
                            select  distinct to_char(fecha_ingreso,'yyyy-mm-dd hh:mm:ss') fecha_ingreso, to_char(fecha_recepcion,'yyyy-mm-dd hh:mm:ss') fecha_recepcion,
                            numero_tramite, codigo_estado estado, d.codigo_tipo_tramite, d.nombre_tipo_tramite, e.codigo_sub_tipo_tramite, e.nombre_sub_tipo_tramite,
                            b.anio_fiscal, b.mes_fiscal,   case when fecha_ingreso <=  (fecha_recepcion::Date   - '5 years' :: interval)::date then 'SI' else 'NO' end prescrito,
                            monto_solicitado, a.codigo_clase_tramite, c.nombre_clase_tramite,  descripcion_tramite,
                            coalesce(similares::varchar,'no tiene') similares ,  coalesce(previos::varchar,'no tiene') previos, coalesce(bb.descripcion,'') se_resuelve_con
                            from tramites.tra_tramites a inner join tramites.tra_detalles_tramite b using(id_tramite, codigo_clase_tramite, codigo_tipo_tramite)
                            inner join  tramites.tra_clases_tramite c on c.codigo_clase_tramite = a.codigo_clase_tramite
                            inner join  tramites.tra_tipos_tramite d on d.codigo_clase_tramite = a.codigo_clase_tramite and d.codigo_tipo_tramite = a.codigo_tipo_tramite
                            inner join  tramites.tra_subtipos_tramite e on e.codigo_clase_tramite = a.codigo_clase_tramite and e.codigo_tipo_tramite = a.codigo_tipo_tramite
                                and e.codigo_sub_tipo_tramite = b.codigo_sub_tipo_tramite
                            left join  t_declas f on a.numero_ruc = f.numero_identificacion and f.anio_fiscal::int = b.anio_fiscal
                            and f.mes_fiscal::int = b.mes_fiscal
                            left join ta z on z.mes_fiscal = b.mes_fiscal and z.anio_fiscal = b.anio_fiscal
                            left join tb z1 on z1.codigo_tipo_tramite = a.codigo_tipo_tramite and z1.codigo_clase_tramite = a.codigo_clase_tramite
                            inner join adm.adm_estructura_organizacional aa on aa.codigo = a.codigo_es_resuelto_por
                            inner join adm.adm_ubicaciones_geograficas bb on substr(aa.ubicacion_geografica,1,5) = bb.codigo and aa.fecha_final is  null
                            where
                                numero_ruc = '{self.jd.contri}' and a.codigo_clase_tramite in (26)  and e.codigo_tipo_tramite in (32) and e.codigo_sub_tipo_tramite in (1,2)
                                and codigo_estado    in ('ASI','NUE')
                                order by nombre_tipo_tramite desc;

                   """


class Declaraciones:
    '''delcaraciones del contri'''
    representante = ''
    tipo = ''

    def __init__(self, jd):
        '''constructor principal'''
        self.jd = jd

    def get_sql_declaracion_cumplen_nocumplen(self):
        '''declaraciones no cumplen'''
        return f"""  select distinct numero_identificacion, anio_fiscal,
                    mes_fiscal,to_char(fecha_recepcion,'yyyy-mm-dd HH24:MI:SS')
                    fecha_recepcion,ultima_declaracion,
                    (fecha_recepcion::Date   + '1 years'::interval)::date prescrito2,
                    case when  fecha_recepcion <= (fecha_recepcion::Date + '1 years' :: interval)::date then 'SI' else 'NO' end estadentro_del_year,
                    sustitutiva_original, numero_adhesivo, declaracion_cero,
                    saldo_crt_cle_man_2160 + comp_iva_medio_elec_2890
                    sct_adquisicion_mesanterior,
                    saldo_crt_rfu_man_2170 sct_retenciones_mesanterior,
                    ajust_iva_dev_adq_med_ele_2910 + aju_idr_pc_ipt_crt_mac_2210
                     ajuste_x_adquisiciones,
                    aju_idr_pc_ipt_crt_mac_rf_2212 ajuste_x_retenciones,
                    saldo_crt_cle_man_2160 + comp_iva_medio_elec_2890 -
                    ajust_iva_dev_adq_med_ele_2910 + aju_idr_pc_ipt_crt_mac_2210 sct_mes_anterior,
                    saldo_crt_rfu_man_2170 - aju_idr_pc_ipt_crt_mac_rf_2212
                     sct_mesanterior_retenciones,
                    tot_imp_vnl_mac_iaf_1260 total_impuestos_mes_actual,
                    crt_acu_fap_2130 ct_factor_proporcionalidad,
                    impuesto_causado_2140  impuesto_causado,
                    credito_tributario_mac_2150  ct_mes_actual,
                    rfu_mes_actual_2200 retenciones_fuente_iva,
                    saldo_crt_clo_ipr_msi_2220+ com_iva_vent_med_elec_2930 sct_x_adquisiciones,
                    saldo_crt_rfu_msi_2230 sct_x_retenciones,
                    tot_imp_apa_percepcion_2270 tot_impuesto_pagar_x_percepcion,
                    saldo_crt_clo_ipr_msi_2220,  total_pagado,total_impuesto_a_pagar_2610 ,
                    case when codigo_impuesto = 2011 then 'MENSUAL' else 'SEMESTRAL' end codigo_impuesto
                from owbtar.owb_ods_declaraciones_104 where numero_identificacion = '{self.jd.contri}' and
                (anio_fiscal || '-' || mes_fiscal || '-01')::date between  ('{self.jd.periodo_inicial}' )::date
                    and  (date_trunc('month', '{self.jd.periodo_final}'::date) +     interval '1 month' - interval '1 day')::date
                    --and codigo_impuesto = 2011                                                       
                order by numero_adhesivo desc, fecha_recepcion desc;
            """

    def get_sql_declaracion_transpuesta(self):
        '''    # 2 primera pesttania de cadena de iva '''
        return f""" select distinct anio_fiscal, mes_fiscal , '' camino,
                    to_char(fecha_recepcion,'yyyy-mm-dd HH24:MI:SS')
                     fecha_recepcion,
                    upper(sustitutiva_original) sustitutiva_original,
                    numero_adhesivo,
                    saldo_crt_cle_man_2160 + comp_iva_medio_elec_2890
                     sct_adquisicion_mesanterior,
                    saldo_crt_rfu_man_2170 sct_retenciones_mesanterior,
                    ajust_iva_dev_adq_med_ele_2910 +
                    aju_idr_pc_ipt_crt_mac_2210 ajuste_x_adquisiciones,
                    aju_idr_pc_ipt_crt_mac_rf_2212 ajuste_x_retenciones,
                    saldo_crt_cle_man_2160 + comp_iva_medio_elec_2890 -
                    ajust_iva_dev_adq_med_ele_2910 -
                    aju_idr_pc_ipt_crt_mac_2210 sct_mes_anterior,
                    saldo_crt_rfu_man_2170 - aju_idr_pc_ipt_crt_mac_rf_2212
                     sct_mesanterior_retenciones,
                    tot_imp_vnl_mac_iaf_1260 total_impuestos_mes_actual,
                    crt_acu_fap_2130 ct_factor_proporcionalidad,
                    impuesto_causado_2140  impuesto_causado,
                    credito_tributario_mac_2150  ct_mes_actual,
                    rfu_mes_actual_2200 retenciones_fuente_iva,
                    saldo_crt_clo_ipr_msi_2220+ com_iva_vent_med_elec_2930
                     sct_x_adquisiciones,
                    saldo_crt_rfu_msi_2230 sct_x_retenciones,
                    tot_imp_apa_percepcion_2270
                     tot_impuesto_pagar_x_percepcion,
                    saldo_crt_clo_ipr_msi_2220,  total_pagado,
                    total_impuesto_a_pagar_2610,
                    '' diferencia_arr_ct, '' diferencia_x_ct,
                    '' diferencia_adquisiciones,
                    '' diferencia_retenciones, 0 totales, codigo_impuesto
                from owbtar.owb_ods_declaraciones_104 where
                 numero_identificacion = '{self.jd.contri}' and
                 numero_adhesivo in ({self.jd.adhesivos})
                 order by numero_adhesivo desc, fecha_recepcion asc;
        """

    def we_have_semestrales(self):
        '''si se tienen semestrales'''
        return f""" select  count(1) total from
                     owbtar.owb_ods_declaraciones_104
                     where numero_adhesivo in  (
                    {self.jd.adhesivos}
                    ) and codigo_impuesto = 2021;
        """

    def num_declas_validas(self):
        '''declaraciones validas'''
        return f""" select count(1) from temporal.dev_declaraciones_validas
                    where contri = '{self.jd.contri}'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_finalisima}'  and
                     usuario = '{self.jd.usuario}'  """

    def reset_declas_validas(self):
        '''declaraciones validas'''
        return f""" delete from temporal.dev_declaraciones_validas
                     where contri = '{self.jd.contri}'
                     and periodo_inicial = '{self.jd.periodo_inicial}' and
                      periodo_final = '{self.jd.periodo_finalisima}'
                       and  usuario = '{self.jd.usuario}'  """


class NoCruzan:
    '''consultas para las retenciones que no cruzan'''

    def __init__(self, jd):
        '''constructor principal'''
        self.jd = jd
        self.estado = 'INA'

    def get_sql_providenciadas(self):
        '''# 2. estado =   self.get_estados() 
        if self.jd.procedencia == 'externa' else "INA"'''
        estado = "" if self.jd.procedencia == 'externa' else "INA"
        condicion_estado = ''
        condicion_memoria = f' and idmemoria = {self.jd.memoria}'
        if estado == 'INA':
            condicion_estado = " and a.estado = 'INA'"
            condicion_memoria = ''

        if len(self.jd.contri) == 10:
            self.jd.contri = self.jd.uf.costelo(self.jd.contri)

        return f"""select distinct *from (
                select distinct * from (
                    with thead as (
                        select '{self.jd.contri}' contri, 'INA' estado, '{self.jd.periodo_inicial}'::date periodo_inicial, (date_trunc('month',
                        '{self.jd.periodo_final}'::date) + interval '1 month' - interval '1 day')::date periodo_final, '{self.jd.usuario}' usuario
                    ), provi as (
                        select  distinct b.contri, b.periodo_inicial, b.periodo_final,  a.ruc_contrib_informan, a.fecha_emi_retencion, a.autorizacion, a.secuencial_retencion
                            ,a.frecuencia, a.cod_impuesto,  a.valor_retenido_listado
                            from temporal.dev_providencias_vals a inner join  thead b using(contri) where length(autorizacion) > 20
                            and a.periodo_inicial = '{self.jd.periodo_inicial_org}' and a.periodo_final = '{self.jd.periodo_final_org}' and a.usuario = '{self.jd.usuario}'
                            {condicion_estado}  {condicion_memoria}
                    ), cursor_compras as (
                        select  distinct numero_ruc_emisor agente_retencion, identificacion_sujeto contri, razon_social,
                            fecha_emision::date fecha_emision,  secuencial::numeric comprobante,
                            numero_autorizacion  autorizacion
                        from  terceros.dev_iva_retencion_on_elec a inner join thead b on a.identificacion_sujeto = b.contri
                        and fecha_emision between  (select periodo_inicial from thead) and (select thead.periodo_final from thead)  order by autorizacion asc
                    ), autorizaciones as (
                        select distinct  a.contri, a.ruc_contrib_informan, a.autorizacion, b.autorizacion numero_autorizacion_pintar  from provi a left join
                                cursor_compras b on  a.contri = b.contri and  a.autorizacion  = b.autorizacion
                    ),carpinteria as (
                        select distinct *from provi a
                                inner join autorizaciones d using(autorizacion, contri, ruc_contrib_informan)
                    )select distinct  contri ,  ruc_contrib_informan, ruc_contrib_informan::varchar numero_ruc_emisor_pintar,  fecha_emi_retencion::varchar fecha_emi_retencion , fecha_emi_retencion::varchar fecha_emision_pintar,  autorizacion,
                            numero_autorizacion_pintar, secuencial_retencion, secuencial_retencion::varchar secuencial_pintar, b.valor_retenido_listado valor_retencion, extract(year from fecha_emi_retencion) anio,
                            extract(month from fecha_emi_retencion) mes,  '' ffpv, b.frecuencia, b.cod_impuesto, '' documento
                            from carpinteria a inner join provi b
                                using( fecha_emi_retencion, autorizacion, contri, ruc_contrib_informan, secuencial_retencion )
                                
                            where length(b.autorizacion)>20  and  b.periodo_inicial = '{self.jd.periodo_inicial_org}' and b.periodo_final = '{self.jd.periodo_final_org}'
                                )pa
                    union
                    select distinct * from (
                        with thead as (
                            select '{self.jd.contri}' contri, 'INA' estado, '{self.jd.periodo_inicial}'::date periodo_inicial, (date_trunc('month', '{self.jd.periodo_final}'::date) + interval '1 month' - interval '1 day')::date periodo_final
                        ), provi as (
                            select  distinct b.contri, b.periodo_inicial, b.periodo_final,  a.ruc_contrib_informan, a.fecha_emi_retencion, a.autorizacion, a.secuencial_retencion
                                ,a.frecuencia, a.cod_impuesto,  a.valor_retenido_listado, a.es_ffpv
                                    from temporal.dev_providencias_vals a inner join  thead b using(contri) where length(autorizacion) < 20
                                {condicion_estado}  {condicion_memoria}
                                and a.periodo_inicial = '{self.jd.periodo_inicial_org}' and a.periodo_final = '{self.jd.periodo_final_org}' and a.usuario = '{self.jd.usuario}'
                                and a.estado = 'INA'
                        ),cursor_compras_fi as (
                        select  distinct numero_ruc_emisor agente_retencion, identificacion_sujeto contri, razon_social,
                                fecha_emision::date fecha_emision,  secuencial::numeric comprobante, numero_autorizacion  autorizacion
                            from  terceros.dev_iva_retencion_on_fi a inner join thead b on a.identificacion_sujeto = b.contri
                            and fecha_emision between  (select periodo_inicial from thead) and (select thead.periodo_final from thead)
                            and numero_autorizacion is not null and length(numero_autorizacion)>0  order by autorizacion asc
                    ), emisores as (
                            select distinct  a.contri, a.ruc_contrib_informan,  b.agente_retencion numero_ruc_emisor_pintar   from provi a left join
                                    cursor_compras_fi b on  a.contri = b.contri and  a.ruc_contrib_informan = b.agente_retencion
                    ),fechaemisiones as (
                            select distinct   a.contri, a.ruc_contrib_informan, to_char(a.fecha_emi_retencion,'yyyy-mm-dd')::date fecha_emi_retencion,  b.fecha_emision::varchar fecha_emision_pintar   from provi a left join
                                cursor_compras_fi  b on a.contri = b.contri and a.fecha_emi_retencion  = b.fecha_emision and a.ruc_contrib_informan = b.agente_retencion and  a.secuencial_retencion  = b.comprobante
                    ),autorizaciones as (
                            select distinct  a.contri, a.ruc_contrib_informan, a.autorizacion, b.autorizacion numero_autorizacion_pintar  from provi a left join
                                cursor_compras_fi b on  a.contri = b.contri and  a.autorizacion  = b.autorizacion and  a.secuencial_retencion  = b.comprobante
                    ),secuenciales as (
                            select distinct  a.contri, a.ruc_contrib_informan, a.secuencial_retencion,  b.comprobante::varchar secuencial_pintar   from provi a left join
                                    cursor_compras_fi b on a.contri = b.contri and  a.secuencial_retencion  = b.comprobante::int and a.ruc_contrib_informan = b.agente_retencion and a.autorizacion = b.autorizacion
                    ),carpinteria as (
                        select distinct *from provi a inner join emisores b using(contri, ruc_contrib_informan  )
                                inner join fechaemisiones c using(fecha_emi_retencion, contri, ruc_contrib_informan)
                                inner join autorizaciones d using(autorizacion, contri, ruc_contrib_informan)
                                inner join secuenciales e using(secuencial_retencion, contri, ruc_contrib_informan)
                    ), prebloque as (
                        select distinct  contri ,  ruc_contrib_informan, numero_ruc_emisor_pintar,    fecha_emi_retencion::varchar fecha_emi_retencion , fecha_emision_pintar,  autorizacion,
                            numero_autorizacion_pintar, a.secuencial_retencion, secuencial_pintar, b.valor_retenido_listado valor_retencion,
                            extract(year from fecha_emi_retencion) anio, extract(month from fecha_emi_retencion) mes,
                            case when b.es_ffpv is null then '' else b.es_ffpv end ffpv, 
                            b.frecuencia, b.cod_impuesto, 
                            string_agg(distinct  coalesce(d.tipocomprobante, ''), ',') documento
                            from carpinteria a inner join provi b
                                using( fecha_emi_retencion, autorizacion, contri, ruc_contrib_informan, secuencial_retencion)
                                left join inter.dev_iva_autoriza_emision c on c.numero_ruc = b.ruc_contrib_informan and c.codigo_autorizacion = b.autorizacion and c.id_tipo_documento = 7
                                left join public.dev_tipos_documentos d on d.codigo = c.id_tipo_documento
                            where length(b.autorizacion)<20 and  b.periodo_inicial = '{self.jd.periodo_inicial_org}' and b.periodo_final = '{self.jd.periodo_final_org}'
                            group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
                        ) select *from prebloque
                            )pb )xa order by anio asc, mes asc;
                """

    def get_sql_informe_filtros(self, filtro):
        '''#para obtener las providencias - metodo definitivo'''
        return f"""     select ruc_contrib_informan, razon_social, to_char(fecha_emi_retencion,'yyyy-mm-dd')::varchar  fecha_emision, secuencial_retencion,
                        autorizacion, valor_retenido_listado valor_retencion from temporal.dev_informe_retencion
                        where contri = '{self.jd.contri}' and estado ='INA' and usuario = '{self.jd.usuario}'
                        and   periodo_inicial = '{self.jd.periodo_inicial}' and periodo_final = '{self.jd.periodo_final}' and {filtro};
                """


class MuyFuturas:
    '''compensacion a futuro'''

    def __init__(self, jd):
        '''constructor principal'''
        self.jd = jd

    def get_sql_ultima_memoria_ingresado(self):
        '''ultiumo ingresado'''
        return f""" select max(idmemoria) from public.dev_memoria_casos
                      where contri = '{self.jd.contri}' and
                      periodo_inicial = '{self.jd.periodo_inicial}'
                      and periodo_final = '{self.jd.periodo_final}'
                """

    def get_sql_futuros_conteo(self):
        '''futuros conteo'''
        return f""" select count(1)  veces from temporal.dev_compensa_futuro
                    where  contri = '{self.jd.contri}'   and estado='INA'
                     and periodo_inicial = '{self.jd.periodo_inicial}' and
                      periodo_final = '{self.jd.periodo_final}' and
                       usuario = '{self.jd.usuario}'
                """

    def get_sql_declaracion_transpuesta_futura(self):
        '''declaracion transpuesta futura'''
        mes_siguiente = str((datetime.strptime(self.jd.periodo_final, '%Y-%m-%d').date() + timedelta(days=15)).strftime('%Y-%m'))
        mesactual = str((datetime.now()).strftime('%Y-%m'))
        l3 = mes_siguiente + '-01'
        l4 = mesactual + '-28'
        return f""" with tmaximas as (
                        select numero_identificacion, anio_fiscal, mes_fiscal,
                        max(numero_adhesivo) numero_adhesivo
                        from owbtar.owb_ods_declaraciones_104 where
                        numero_identificacion = '{self.jd.contri}' and
                            (anio_fiscal || '-' || mes_fiscal || '-01')::date
                            between  ('{l3}' )::date
                            and  (date_trunc('month', '{l4}'::date) +
                            interval '1 month' - interval '1 day')::date
                            group by  1,2,3
                    ), tseleccionadas as (
                        select distinct numero_adhesivo from tmaximas
                    ),
                    tcreditos as (
                        select sum(valor) valor  from
                        temporal.dev_cuadro_liquidacion
                         where contri = '{self.jd.contri}' 
                         and estado = 'INA' and fila in (3,4)
                         and periodo_inicial = '{self.jd.periodo_inicial}' and
                          periodo_final = '{self.jd.periodo_finalisima}' and
                         usuario = '{self.jd.usuario}'
                    )
                    select distinct anio_fiscal, mes_fiscal , '' camino,
                    to_char(fecha_recepcion,'yyyy-mm-dd HH24:MI:SS')
                    fecha_recepcion,
                    upper(sustitutiva_original) sustitutiva_original,
                    numero_adhesivo,
                    (select *from tcreditos) 
                    sct_credito_mes_anterior_rca_adq_ret,
                    ajust_iva_dev_adq_med_ele_2910 +
                    aju_idr_pc_ipt_crt_mac_2210 ajuste_x_adquisiciones,
                    (select *from tcreditos) - (ajust_iva_dev_adq_med_ele_2910
                    + aju_idr_pc_ipt_crt_mac_2210) saldo_de_ct_mes_anterior,
                    impuesto_causado_2140  impuesto_causado,
                        credito_tributario_mac_2150  ct_mes_actual,
                        rfu_mes_actual_2200 retenciones_fuente_iva,
                        tot_imp_apa_percepcion_2270 
                        tot_impuesto_pagar_x_percepcion,
                        '0' compensa_futuro_reco_sol_atendida,
                        '0' saldo_cred_resulta_next_mes,
                        '0' impuesto_pagar_resulta_mes
                from owbtar.owb_ods_declaraciones_104
                    where numero_identificacion = '{self.jd.contri}' and
                    numero_adhesivo in (select *from tseleccionadas)  order by 
                     anio_fiscal asc, mes_fiscal asc, fecha_recepcion asc;

            """

    def get_sql_declaracion_transpuesta_futura_diaria(self):
        '''transpuesta diaria'''
        return f"""select anio_fiscal,mes_fiscal,camino,fecha_recepcion,
                    sustitutiva_original,numero_adhesivo,
                    sct_credito_mes_anterior_rca_adq_ret,
                    ajuste_x_adquisiciones,
                    saldo_de_ct_mes_anterior,impuesto_causado,ct_mes_actual,
                    retenciones_fuente_iva,tot_impuesto_pagar_x_percepcion,
                    compensa_futuro_reco_sol_atendida,
                    saldo_cred_resulta_next_mes,
                    impuesto_pagar_resulta_mes from
                     temporal.dev_compensa_futuro
                     where contri = '{self.jd.contri}' and estado = 'INA'
                     and periodo_inicial = '{self.jd.periodo_inicial}' and
                     periodo_final = '{self.jd.periodo_finalisima}'
                     and usuario = '{self.jd.usuario}'
                    order by anio_fiscal asc, mes_fiscal asc,
                    fecha_recepcion asc
                """

    def get_ultimo_diez(self):
        '''ultimo valor en la decima posicion'''
        return f""" with thead as (
                        select anio_fiscal, mes_fiscal,
                            max(numero_adhesivo)numero_adhesivo
                            from owbtar.owb_ods_declaraciones_104
                            where numero_identificacion = '{self.jd.contri}'
                            group by 1,2 order by 1 desc,2 desc limit 1
                        )
                        select saldo_crt_rfu_msi_2230 from
                        owbtar.owb_ods_declaraciones_104 where
                        numero_adhesivo = (select numero_adhesivo from thead);
                        """
