"""Consultas, desde Enero 2023
Funcionalidades:
  - Consuultas a la base para postgres.

ESTANDAR PEP8

"""


class Papel:
    '''consultas varias'''
    def __init__(self, db):
        self.db = db

    def get_estados(self):
        '''conseguir los estados'''
        estado = 'INA'

        match(int(self.db.uf.pi.cuerda)):
            case 6:
                match(self.db.uf.navegante.perfil):
                    case 'Analista':
                        estado = 'APR'
                    case 'Supervisor':
                        estado = 'SAV'

            case 7:
                match(self.db.uf.navegante.perfil):
                    case 'Analista':
                        estado = 'FIN'
                    case 'Supervisor':
                        estado = 'APR'

            case 8:
                match(self.db.uf.navegante.perfil):
                    case 'Analista':
                        estado = 'ERR'
                    case 'Supervisor':
                        estado = 'SAV'
            case _:
                estado = 'INA'
        return estado

    def get_sql_tramites_contri(self):
        '''tramites del contribuyentes'''
        return f"""with tdeclas as (
                        select anio_fiscal, mes_fiscal, max(fecha_recepcion)
                        fecha_recepcion from
                        OWBTAR.OWB_ODS_DECLARACIONES_104 f where
                        f.numero_identificacion = '{self.db.uf.pi.contri}' and
                        sustitutiva_original = 'ORIGINAL' group by 1,2
                    )
                    select  distinct numero_ruc,
                    to_char(fecha_ingreso,'yyyy-mm-dd hh:mm:ss')
                    fecha_ingreso,
                    to_char(fecha_recepcion, 'yyyy-mm-dd hh:mm:ss')
                    fecha_recepcion,
                    numero_tramite, codigo_estado estado,
                    d.codigo_tipo_tramite, d.nombre_tipo_tramite,
                    e.codigo_sub_tipo_tramite, e.nombre_sub_tipo_tramite,
                    a.codigo_clase_tramite, c.nombre_clase_tramite,
                    descripcion_tramite, coalesce(bb.descripcion,'')
                    se_resuelve_con, b.anio_fiscal, b.mes_fiscal,
                    monto_solicitado, coalesce(monto_a_devolver::float, 0 )
                    monto_a_devolver,  b.anio_fiscal::varchar || '-' ||
                    lpad(b.mes_fiscal::varchar,2,'0') || '-01'  periodo_fiscal
                    from tramites.tra_tramites a inner join
                    tramites.tra_detalles_tramite b
                    using(id_tramite, codigo_clase_tramite,
                    codigo_tipo_tramite)
                    inner join  tramites.tra_clases_tramite c on
                    c.codigo_clase_tramite = a.codigo_clase_tramite
                    inner join  tramites.tra_tipos_tramite d on
                    d.codigo_clase_tramite = a.codigo_clase_tramite
                    and d.codigo_tipo_tramite = a.codigo_tipo_tramite
                    inner join  tramites.tra_subtipos_tramite e on
                    e.codigo_clase_tramite = a.codigo_clase_tramite and
                    e.codigo_tipo_tramite = a.codigo_tipo_tramite
                        and e.codigo_sub_tipo_tramite =
                        b.codigo_sub_tipo_tramite
                    inner join adm.adm_estructura_organizacional
                        aa on aa.codigo = a.codigo_es_resuelto_por
                    inner join adm.adm_ubicaciones_geograficas bb
                        on substr(aa.ubicacion_geografica,1,5) =
                        bb.codigo and aa.fecha_final is  null
                    left join  tdeclas f on  f.anio_fiscal::int =
                        b.anio_fiscal and f.mes_fiscal::int = b.mes_fiscal
                    where
                        a.codigo_clase_tramite in (26)  and
                        b.codigo_tipo_tramite in (32) and
                        b.codigo_sub_tipo_tramite in (1,2)
                        and numero_ruc = '{self.db.uf.pi.contri}'
                    order by anio_fiscal asc, mes_fiscal asc
                    """

    def get_sql_declaraciones_validas_inf_sem(self):
        '''declaraciones validas informes semanales'''
        return f""" select anio_fiscal anio, mes_fiscal mes,
                    retenciones_fuente_iva, numero_adhesivo, codigo_impuesto
                     from temporal.dev_declaraciones_validas
                    where contri = '{self.db.uf.pi.contri}' and estado = 'INA'
                    and periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                    and periodo_final = '{self.db.uf.pi.periodo_finalisima}'
                    and usuario = '{self.db.uf.pi.usuario}'
                    and codigo_impuesto = '2021'
                """

    def get_sql_cadena_iva(self, _jd) -> str:
        '''cadenas de iva'''
        return f""" select distinct camino, a.anio_fiscal anio,
                    a.mes_fiscal mes, a.impuesto_causado, a.ct_mes_actual,
                    a.sct_adquisicion_mesanterior,
                    a.sct_retenciones_mesanterior,
                    b.valor_retencion valor_retencion_valida,
                    0 ct_adq_proximo_mes, 0 ct_ret_proximo_mes,
                    0 total_impuesto_a_pagar, 0 retenciones_a_devolver,
                    tot_impuesto_pagar_x_percepcion
                    ,0 calculo_ct_adq, 0 calculo_ct_ret, diferencia_arr_ct,
                    diferencia_x_ct,  diferencia_adquisiciones,
                    diferencia_retenciones, ajuste_x_adquisiciones
                    ,sct_x_adquisiciones,	sct_x_retenciones
                    from  temporal.dev_declaraciones_validas a
                        inner join
                        temporal.dev_resultado_analisis_retencion b
                        using(contri, estado, periodo_inicial,
                        periodo_final, usuario)
                        where contri = '{_jd["contri"]}' and
                        a.anio_fiscal::int = b.anio and
                        a.mes_fiscal::int = b.mes
                        and  a.estado = 'INA'  and numero_adhesivo in
                        ({_jd["adhesivos"]})  and b.estado = 'INA'
                        and periodo_inicial = '{_jd["periodo_inicial"]}' and
                        periodo_final = '{_jd["periodo_finalisima"]}' and
                        usuario = '{_jd["usuario"]}'
                        order by 2 asc, 3 asc;
                """

    def get_sql_cadena_iva_existe(self, _jd) -> str:
        '''chequeo de la cadena de iva existe'''
        return f""" select count(1)
                         from temporal.dev_cad_iva_procesa
                        where contri = '{_jd["contri"]}' and estado = 'INA'
                        and periodo_inicial = '{_jd["periodo_inicial"]}'
                        and  periodo_final = '{_jd["periodo_final"]}'
                        and usuario = '{_jd["usuario"]}'
                """

    def get_sql_cadena_iva_proc_reset(self) -> str:
        '''cadea iva procedimiento reset'''
        return f""" delete from temporal.dev_cad_iva_procesa
                    where contri = '{self.db.uf.pi.contri}' and estado = 'INA'
                    and periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                    and  periodo_final = '{self.db.uf.pi.periodo_finalisima}'
                    and usuario = '{self.db.uf.pi.usuario}' """

    def get_sql_cadena_iva_procesado(self, _jd) -> str:
        '''cadena iva procesado'''
        return f""" select camino, anio, mes, impuesto_causado, ct_mes_actual,
                    sct_adquisicion_mesanterior, sct_retenciones_mesanterior,
                    valor_retencion_valida, ct_adq_proximo_mes,
                    ct_ret_proximo_mes, total_impuesto_a_pagar,
                    retenciones_a_devolver, tot_impuesto_pagar_x_percepcion,
                    calculo_ct_adq, calculo_ct_ret, diferencia_arr_ct,
                    diferencia_x_ct, diferencia_adquisiciones,
                    diferencia_retenciones, ajuste_x_adquisiciones,
                    sct_x_adquisiciones,
                    sct_x_retenciones from temporal.dev_cad_iva_procesa
                    where contri = '{_jd["contri"]}' and estado = 'INA'
                    and periodo_inicial = '{_jd["periodo_inicial"]}'
                    and  periodo_final = '{_jd["periodo_finalisima"]}'
                    and usuario = '{_jd["usuario"]}';
                """

    def get_pasado_cadena_iva_adq_ma(self) -> str:
        '''adquisiciones mes anterior'''
        return f"""select sct_adquisicion_mesanterior from
                    temporal.dev_declaraciones_validas where
                    contri = '{self.db.uf.pi.contri}' and estado = 'INA'
                     and periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                     and  periodo_final = '{self.db.uf.pi.periodo_finalisima}'
                     and usuario = '{self.db.uf.pi.usuario}'
                     order by anio_fiscal asc, mes_fiscal asc limit 1 ;
                """

    def get_sql_providenciadas_ina(self):
        '''para obtener providencias'''
        return f""" select anio, mes, ruc_contrib_informan, contri,
                       razon_social,
                       to_char(fecha_emi_retencion,'yyyy-mm-dd hh:mm:ss')
                       fecha_emi_retencion,
                        autorizacion, valor_retencion, secuencial_retencion,
                        es_fantasma, es_fallecido, es_ffpv, cruza, conclusion,
                        valor_retencion_aceptado, estado, fecha_analisis,
                        tramite from temporal.dev_providencias_vals where
                            contri = '{self.db.uf.pi.contri}'
                            and estado = 'INA' and
                            periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                            and periodo_final = '{self.db.uf.pi.periodo_final}'
                            and usuario = '{self.db.uf.pi.usuario}'
                    ;
                """

    def get_filtros_parciales_clase(self):
        '''filtros parcilaes de clase'''
        estado = "" if self.db.uf.pi.procedencia == 'externa' else "INA"
        condicion_periodos = ''
        condicion_estado = ''
        condicion_memoria = f' and idmemoria = {self.db.uf.pi.memoria}'
        if estado == 'INA':
            condicion_estado = " and estado = 'INA'"
            condicion_memoria = ''
            condicion_periodos = f""" and periodo_inicial =
                                    '{self.db.uf.pi.periodo_inicial}'
                                    and periodo_final =
                                    '{self.db.uf.pi.periodo_final}' """

        return condicion_estado, condicion_memoria, condicion_periodos

    def get_sql_rs(self, z):
        '''razon social '''
        return f"""   select razon_social from rucsri.dev_iva_contri
                        where numero_ruc = '{z}'; """

    def get_sql_razon_social_his(self, z):
        '''razon social hisotira '''
        return f"""   select razon_social from
                        rucsri.dev_iva_contris_llegan where contri = '{z}'; """

    # 1 para obtener numero de filas
    def get_sql_razon_social(self):
        '''razon social de otra manera'''
        if len(self.db.uf.pi.contri) == 10:
            self.db.uf.pi.contri = self.db.uf.costelo(self.db.uf.pi.contri)
        return f"""   select razon_social from rucsri.dev_iva_contri
                        where numero_ruc = '{ self.db.uf.pi.contri}'; """

    def get_sql_razon_social_(self, _jd):
        '''razon social codificada'''
        if len(_jd["contri"]) == 10:
            _jd["contri"] = self.db.uf.costelo(_jd["contri"])
        return f"""   select razon_social from rucsri.dev_iva_contri
                        where numero_ruc = '{_jd["contri"]}'; """

    def get_sql_previas(self):
        '''sel previas '''
        return f"""  select distinct to_char(fecha_ingreso,
                        'yyyy-mm-dd hh:mm:ss') fecha_ingreso,  numero_tramite,
                        a.codigo_estado estado, d.codigo_tipo_tramite,
                        d.nombre_tipo_tramite,
                        e.codigo_sub_tipo_tramite, e.nombre_sub_tipo_tramite,
                        b.anio_fiscal, b.mes_fiscal,
                        monto_solicitado, a.codigo_clase_tramite,
                        c.nombre_clase_tramite,  descripcion_tramite,
                        numero_contestacion, archivo_contestacion
                        from tramites.tra_tramites a inner join
                            tramites.tra_detalles_tramite b using(id_tramite,
                            codigo_clase_tramite, codigo_tipo_tramite)
                        inner join  tramites.tra_clases_tramite c
                            on c.codigo_clase_tramite = a.codigo_clase_tramite
                        inner join  tramites.tra_tipos_tramite d
                            on d.codigo_clase_tramite = a.codigo_clase_tramite
                            and d.codigo_tipo_tramite = a.codigo_tipo_tramite
                        inner join  tramites.tra_subtipos_tramite e
                            on e.codigo_clase_tramite = a.codigo_clase_tramite
                            and e.codigo_tipo_tramite = a.codigo_tipo_tramite
                            and e.codigo_sub_tipo_tramite =
                            b.codigo_sub_tipo_tramite
                            left join tramites.tra_contestaciones_tramite h on
                            h.id_tramite = a.id_tramite and tipo_contestacion
                            in ('RES','OFI')
                            and archivo_contestacion is not null
                        where
                            a.codigo_clase_tramite in (26)  and
                            e.codigo_tipo_tramite in (19, 32)
                            and numero_ruc = '{self.db.uf.pi.contri}'
                            and a.codigo_estado  not in ('ASI','NUE')
                        order by nombre_tipo_tramite desc;
            """

    def get_sql_similares(self):
        '''similares'''
        return f"""select distinct to_char(fecha_ingreso,'yyyy-mm-dd')
                    fecha_ingreso,
                    to_char(fecha_recepcion,'yyyy-mm-dd hh:mm:ss')
                    fecha_recepcion, numero_tramite,
                    a.codigo_estado estado,
                    d.codigo_tipo_tramite, d.nombre_tipo_tramite,
                    e.codigo_sub_tipo_tramite, e.nombre_sub_tipo_tramite,
                    b.anio_fiscal, b.mes_fiscal,
                    case when fecha_ingreso <=
                    (fecha_recepcion::Date   - '5 years' :: interval)::date
                    then 'SI' else 'NO' end prescrito,
                    monto_solicitado, a.codigo_clase_tramite,
                    c.nombre_clase_tramite,  descripcion_tramite,
                    numero_contestacion, archivo_contestacion
                    from tramites.tra_tramites a inner join
                    tramites.tra_detalles_tramite b using(id_tramite,
                    codigo_clase_tramite, codigo_tipo_tramite)
                    inner join  tramites.tra_clases_tramite c on
                    c.codigo_clase_tramite = a.codigo_clase_tramite
                    inner join  tramites.tra_tipos_tramite d on
                    d.codigo_clase_tramite = a.codigo_clase_tramite and
                    d.codigo_tipo_tramite = a.codigo_tipo_tramite
                    inner join  tramites.tra_subtipos_tramite e on
                        e.codigo_clase_tramite = a.codigo_clase_tramite and
                        e.codigo_tipo_tramite = a.codigo_tipo_tramite
                        and e.codigo_sub_tipo_tramite =
                        b.codigo_sub_tipo_tramite
                    inner join  OWBTAR.OWB_ODS_DECLARACIONES_104 f
                        on a.numero_ruc = f.numero_identificacion and
                        f.anio_fiscal::int = b.anio_fiscal and
                        f.mes_fiscal::int = b.mes_fiscal
                    left join tramites.tra_contestaciones_tramite h
                        on h.id_tramite = a.id_tramite and tipo_contestacion
                        in ('RES', 'OFI') and archivo_contestacion is not null
                    where
                        a.codigo_clase_tramite in (26)  and
                        e.codigo_tipo_tramite in (19, 32)
                        and numero_ruc = '{self.db.uf.pi.contri}' and
                            a.codigo_estado  not in ('ASI','NUE')
                        and b.anio_fiscal = {self.db.uf.pi.anio} and
                            b.mes_fiscal = {self.db.uf.pi.mes} and
                            f.sustitutiva_original = 'ORIGINAL'
                        order by nombre_tipo_tramite desc; """

    def get_sql_acceso_numero(self):
        '''acceso numero'''
        return f""" select max(num_acceso) num_acceso from
                        public.dev_accesos_portal
                        where usuario = '{self.db.uf.pi.usuario}' and
                        ipv4='{self.db.uf.pi.ipv4}' and
                        fecha_ingreso::date = '{self.db.get_fecha_ymd()}' and
                        estado = 1; """

    def get_sql_listado_exploratorio(self) -> str:
        '''informe de retencion'''
        return f""" select extract(year from fecha_emision)::varchar anio,
                    extract(month from fecha_emision)::varchar mes,
                    count(1) conteo
                     from temporal.dev_cargas_archivos
                     where fecha_emision::date
                    between   '{self.db.uf.pi.periodo_inicial_org}' and
                    '{self.db.uf.pi.periodo_final_org}'
                    and periodo_inicial = '{self.db.uf.pi.periodo_inicial_org}'
                    and periodo_final = '{self.db.uf.pi.periodo_final_org}'
                    and contri = '{self.db.uf.pi.contri}'
                    and estado = 'INA' and usuario = '{self.db.uf.pi.usuario}'
                    group by  1,2 having count(1) > 0;
                    """

    def get_sql_compras_exploratorio(self) -> str:
        '''compras explorataorio'''
        return f"""select anio::varchar anio, mes::varchar mes, sum(conteo)
                    from(
                    select extract(year from fecha_emision) anio,
                        extract (month from fecha_emision) mes,
                        count(1) conteo from
                        terceros.dev_iva_retencion_on_elec where fecha_emision
                        between  '{self.db.uf.pi.periodo_inicial}'
                        and '{self.db.uf.pi.periodo_finalisima}' and
                        identificacion_sujeto = '{self.db.uf.pi.contri}'
                        group by 1,2 having count(1)>0
                    union
                    select extract(year from fecha_emision) anio,
                        extract (month from fecha_emision) mes,
                        count(1) conteo from
                        terceros.dev_iva_retencion_on_fi where fecha_emision
                        between  '{self.db.uf.pi.periodo_inicial}' and
                        '{self.db.uf.pi.periodo_finalisima}' and
                        identificacion_sujeto = '{self.db.uf.pi.contri}'
                        group by 1,2 having count(1)>0
                    )nupy group by 1,2"""

    def get_sql_listado_explora_parcial(self) -> str:
        '''listado explora parcial'''
        condicion = ' and length(autorizacion) > 20 ' if  self.db.uf.pi.and_errante == 'E' else ' and length(autorizacion) < 20 '
        return f""" select extract(year from fecha_emision)::varchar anio,
                    extract(month from fecha_emision)::varchar mes,
                    count(1) conteo
                      from temporal.dev_cargas_archivos where
                    fecha_emision::date
                    between '{self.db.uf.pi.periodo_inicial}' and
                    '{self.db.uf.pi.periodo_final}'
                    and periodo_inicial = '{self.db.uf.pi.periodo_inicial_org}'
                    and periodo_final = '{self.db.uf.pi.periodo_final_org}'
                    and contri = '{self.db.uf.pi.contri}' and estado = 'INA'
                    and usuario = '{self.db.uf.pi.usuario}'
                    {condicion}
                    group by  1,2 having count(1) > 0;
                    """

    def get_sql_listado_parcial(self):
        '''listado parcial '''
        condicion = ' and length(autorizacion) > 20 ' if  self.db.uf.pi.and_errante == 'E' else ' and length(autorizacion) < 20 '
        return f""" with thead as (
                    select  agente_retencion::varchar agente_retencion,
                    fecha_emision::date fecha_emision,
                    comprobante::varchar comprobante,
                    autorizacion::varchar autorizacion,
                    indice, round(valor_retenido, 2) valor_retenido,
                    contri::varchar contri
                     from  temporal.dev_cargas_archivos
                    where contri = '{self.db.uf.pi.contri}'  and
                    fecha_emision::date between
                    '{self.db.uf.pi.periodo_inicial}'  and
                    '{self.db.uf.pi.periodo_final}'
                    and periodo_inicial =
                    '{self.db.uf.pi.periodo_inicial_org}'
                    and periodo_final = '{self.db.uf.pi.periodo_final_org}'
                    and estado = 'INA' and usuario = '{self.db.uf.pi.usuario}'
                    {condicion}
                )select a.*,case when b.fecha_baja_fantasma is null
                    then '' else 'si' end es_fantasma,
                    case when c.fecha is null then '' else 'si' end
                        es_fallecido from thead  a left join
                        inter.dev_fantasmas b on
                        a.agente_retencion = b.identificacion
                        --and a.fecha_emision between
                        --fecha_alta_fantasma and fecha_baja_fantasma
                        and agente_retencion is not null
                        and length(agente_retencion)>0
                        left join inter.dev_fallecidos_diferencial
                        c on a.agente_retencion = c.numero_ruc
                        and a.fecha_emision >= c.fecha
                """

    def get_sql_administracion_parcial(self):
        '''sql administracion parcial'''
        consulta = f""" select  distinct numero_ruc_emisor::varchar
                           agente_retencion,
                           identificacion_sujeto::varchar contri,
                           fecha_emision::date fecha_emision,
                           secuencial::varchar comprobante,
                           numero_autorizacion::varchar  autorizacion,
                           round(val_retenido, 2) valor_retenido,
                           COALESCE(numero_documento_sustento::varchar, '')
                           numero_documento_sustento ,
                           string_agg(  distinct upper(razon_social),',')
                           razon_social
                        from  terceros.dev_iva_retencion_on_elec
                        where identificacion_sujeto = '{self.db.uf.pi.contri}'
                        and fecha_emision::date
                        between  '{self.db.uf.pi.periodo_inicial}'  and
                            '{self.db.uf.pi.periodo_final}'
                        and length(numero_autorizacion) >20
                        group by  1,2,3,4,5,6,7
                        order by  contri, agente_retencion,
                        autorizacion, comprobante asc
                """
        if self.db.uf.pi.and_errante == 'F':
            consulta = f""" select  distinct numero_ruc_emisor::varchar
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
                              where identificacion_sujeto =
                              '{self.db.uf.pi.contri}'  and
                              fecha_emision::date between
                              '{self.db.uf.pi.periodo_inicial}'  and
                              '{self.db.uf.pi.periodo_final}'
                        and length(numero_autorizacion) between  1 and 20
                        group by  1,2,3,4,5,6,7
                        order by  contri, agente_retencion,
                        autorizacion, comprobante asc
            """
        return consulta

    def get_sql_snt_datos_cadena(self, _jd):
        '''snd datos cadena'''
        return f"""select fecha_ingreso, coalesce(monto_a_devolver::float,0)
                    monto_a_devolver, sum(coalesce(monto_solicitado::float,0))
                    monto_solicitado
                    from tramites.tra_tramites a inner join
                        tramites.tra_detalles_tramite b
                        on a.id_tramite = b.id_tramite
                        where numero_ruc ='{_jd["contri"]}'
                        and numero_tramite = '{_jd["tramite"]}'
                        group by 1,2;
                """

    def get_sql_caso_parecido(self):
        '''caso parecido'''
        return f"""select distinct usuario, fecha_analisis::date::varchar
                    fecha_analisis, b.nombre, b.cargo, b.email, b.departamento,
                    a.numero_tramite
                    from public.dev_memoria_casos a inner join
                    public.dev_usuario_cad_iva b on a.usuario = b.username
                        where estado in ('SAV','APR','FIN') and
                        contri = '{self.db.uf.pi.contri}' and b.id not in
                        (155,154,153,147)
                        and periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                        and periodo_final = '{self.db.uf.pi.periodo_final}'
                        limit 1;
                """

    def get_sql_retenciones_propias_subjetivas(self):
        '''retenciones propias subjetivas'''
        return f""" select distinct numero_autorizacion autorizacion from
                    terceros.dev_iva_retencion_on_elec
                    where identificacion_sujeto = '{self.db.uf.pi.contri}'
                        and fecha_emision
                        between '{self.db.uf.pi.periodo_inicial}' and
                        '{self.db.uf.pi.periodo_final}'
                    union
                    select distinct  numero_autorizacion autorizacion from
                    terceros.dev_iva_retencion_on_fi
                    where identificacion_sujeto = '{self.db.uf.pi.contri}'
                        and fecha_emision
                        between '{self.db.uf.pi.periodo_inicial}' and
                        '{self.db.uf.pi.periodo_final}'
                """

    def get_sql_dividir_adq_ret(self, _jd):
        '''adquisiciones retenciones division'''
        return f"""select sct_adquisicion_mesanterior || ',' ||
                    sct_retenciones_mesanterior dividir from (
                    select anio, mes, sct_adquisicion_mesanterior,
                    sct_retenciones_mesanterior  from
                    temporal.dev_pre_cadena_iva
                    where contri = '{_jd["contri"]}' and estado='INA'
                    and periodo_inicial = '{_jd["periodo_inicial"]}' and
                    periodo_final = '{_jd["periodo_final"]}'  and
                    usuario = '{_jd["usuario"]}'
                    order by 2 asc, 2 asc limit 1) as1;
                    """

    def get_sql_futuras(self):
        '''comprensacio a futuro'''
        return f"""select anio_fiscal, mes_fiscal, camino, fecha_recepcion,
                     sustitutiva_original, numero_adhesivo,
                     sct_credito_mes_anterior_rca_adq_ret,
                     ajuste_x_adquisiciones, saldo_de_ct_mes_anterior,
                     impuesto_causado, ct_mes_actual, retenciones_fuente_iva,
                     tot_impuesto_pagar_x_percepcion,
                     compensa_futuro_reco_sol_atendida,
                     saldo_cred_resulta_next_mes, impuesto_pagar_resulta_mes
                      from temporal.dev_compensa_futuro
                        where contri = '{self.db.uf.pi.contri}'
                        and estado='INA'
                        and periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                        and periodo_final = '{self.db.uf.pi.periodo_final}'
                        and usuario = '{self.db.uf.pi.usuario}'
                    order by 1 asc, 2 asc;
                            """

    def get_sql_periodos_validos(self):
        '''periodos validos'''
        return f"""select distinct anio_fiscal anio, mes_fiscal mes from
                    temporal.dev_declaraciones_validas
                    where contri = '{self.db.uf.pi.contri}' and estado='INA'
                    and periodo_inicial = '{self.db.uf.pi.periodo_inicial}'
                    and periodo_final = '{self.db.uf.pi.periodo_final}'
                    and usuario = '{self.db.uf.pi.usuario}'
                        order by 1 asc, 2 asc;
                """

    def get_sql_duplicados(self, a, b, c, d, e, f):
        '''sql duplicados'''
        return f"""
                      select   distinct identificacion_sujeto::varchar contri,
                        numero_ruc_emisor::varchar agente_retencion,
                        numero_autorizacion::varchar autorizacion,
                        secuencial comprobante,
                        to_char(fecha_emision,'yyyy-mm-dd')::varchar
                        fecha_emision,  numero_documento_sustento::varchar
                        numero_documento_sustento,
                        round(val_retenido,2) valor_retenido
                      from terceros.dev_iva_retencion_on_elec
                      where
                      identificacion_sujeto = '{a}' and
                      numero_ruc_emisor = '{b}' and
                      numero_autorizacion = '{c}' and
                      secuencial = {d} and
                      extract(year from fecha_emision::date) = extract(year from '{e}'::date) and
                      extract(month from fecha_emision::date) = extract(month from '{e}'::date) and
                      round(val_retenido,2) = {f}
                """
        # fecha_emision::date = '{e}' and


    def get_sql_periodos_analizados(self, _jd):
        '''periodos analizados'''
        return f"""
                    select distinct a.anio, a.mes
                        from temporal.dev_resultado_analisis_retencion a
                        inner join  temporal.dev_declaraciones_validas b
                        using(contri, estado, periodo_inicial,
                        periodo_final, usuario )
                        where contri = '{_jd["contri"]}' and estado='INA'
                        and periodo_inicial = '{_jd["periodo_inicial"]}'
                        and periodo_final = '{_jd["periodo_final"]}'
                        and usuario = '{_jd["usuario"]}'
                        and a.anio = b.anio_fiscal::int
                        and a.mes = b.mes_fiscal::int
                        order by 1 asc, 2 asc;
                         """

    def get_upd_divisores_futuros(self, divisor_l4, adhesivo, contri):
        '''divisores'''
        return f"""update temporal.dev_compensa_futuro
                 set compensa_futuro_reco_sol_atendida = {float(divisor_l4)}
                 where numero_adhesivo =  '{adhesivo}'
                 and   contri = '{contri}'  """
