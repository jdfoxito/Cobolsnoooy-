"""Consultas, desde Enero 2023
Funcionalidades:
  - Consuultas a la base para postgres.
ESTANDAR PEP8
"""

from ayudante import Interacciones


class Globales:
    '''para consultas globales'''

    nav = ''

    def __init__(self, jd):
        '''constructor principal'''
        self.jd = jd

    def costelo(self, num):
        '''codificacion texto'''
        vector = [0, 1]
        longitud = len(num)
        lista = []
        for i in range(longitud):
            x = vector[0] + vector[1]
            vector[0] = vector[1]
            vector[1] = x
            coeficiente = int(num[i]) - int(str(x)[-1])
            lista.append(str(coeficiente + 10 if coeficiente < 0 else coeficiente))
        return (''.join(lista))+'001'

    def get_filtros_parciales_clase(self):
        '''filtros parciales clase'''
        estado = "" if self.jd.procedencia == 'externa' else "INA"
        condicion_periodos = ''
        condicion_estado = ''
        condicion_memoria = f' and idmemoria = {self.jd.memoria}'
        if estado == 'INA':
            condicion_estado = " and estado = 'INA'"
            condicion_memoria = ''
            condicion_periodos = f""" and periodo_inicial =
                                    '{self.jd.periodo_inicial}' and
                                    periodo_final='{self.jd.periodo_final}' """

        return condicion_estado, condicion_memoria, condicion_periodos

    def get_sql_resumen_tramites_id(self):
        '''resumen de tramites'''
        return f""" select a.idmemoria id, a.contri,
                    a.fecha_analisis::date::varchar fecha_analisis,a.usuario,
                    a.numero_tramite, a.supervisor_marca,
                    c.nombre nombre_analista, d.nombre nombre_supervisor,
                    a.estado, a.periodo_inicial::varchar periodo_inicial,
                    a.periodo_final::varchar periodo_final,
                    snt_monto_solicitado, monto_a_devolver_calculado,
                    b.razon_social,
                    (time_graba_memoria - time_inicia)::time::varchar
                    resuelto_en
                    from public.dev_memoria_casos a inner join
                    rucsri.dev_iva_contris_llegan b on a.contri = b.contri
                        inner join public.dev_usuario_cad_iva c
                            on c.username = a.usuario
                        left join public.dev_usuario_cad_iva d
                            on d.username = a.supervisor_marca
                        where  a.idmemoria   =  {self.jd.memoria};
                ; """

    def get_sql_resumen_periodos_est(self):
        '''resumen periodos'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f"""select anio, mes, retenciones_fuente_iva, numero_adhesivo,
                    ingresados, aceptados, negados_x_any, fantasmas,fallecidos,
                    esffpv, nocruzan, duplicados, no_cruzaron_sin_obs,
                    cruzan_fe_fi,  valor_no_reporta, negados_dups, mayores,
                    no_listado, v_ncf, diferencia_actualizar, no_consta_base,
                    aceptados_cadena
                      from temporal.dev_resumen_cadena
                        where contri = '{self.jd.contri}' and
                        usuario = '{self.jd.usuario}' {condicion_estado}
                        {condicion_memoria} {condicion_periodos}
                        order by anio asc, mes asc;
                    """

    def get_sql_iva_procesado(self):
        '''iva procesado'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()

        if len(self.jd.contri) == 10:
            self.jd.contri = self.costelo(self.jd.contri)
        return f"""select camino, anio, mes, impuesto_causado, ct_mes_actual,
                    sct_adquisicion_mesanterior,  sct_retenciones_mesanterior,
                    valor_retencion_valida, ct_adq_proximo_mes,
                    ct_ret_proximo_mes, total_impuesto_a_pagar,
                    retenciones_a_devolver
                      from temporal.dev_cad_iva_procesa where
                    contri = '{self.jd.contri}'  and
                    usuario = '{self.jd.usuario}'
                    {condicion_estado}  {condicion_memoria} 
                    {condicion_periodos} order by anio asc, mes asc;
                """

    def get_sql_resumen_periodos(self):
        '''resumen periodos'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f""" select anio, mes, total_impuesto_a_pagar,
                    retenciones_a_devolver, saldos, fila
                      from temporal.dev_resumen_periodo
                    where contri = '{self.jd.contri}' and
                    usuario = '{self.jd.usuario}'  {condicion_estado}
                    {condicion_memoria} {condicion_periodos}
                    order by anio asc, mes asc; """

    def get_sql_resumen_liquidacion(self):
        '''resumen liquidacion'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f""" select distinct valor, fila from
                        temporal.dev_cuadro_liquidacion
                        where contri = '{self.jd.contri}' and
                        usuario = '{self.jd.usuario}' {condicion_estado}
                        {condicion_memoria} {condicion_periodos}
                        order by fila asc
                ; """

    def get_sql_resumen_analizados(self):
        '''resumen analizados'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f""" select distinct  valor, fila from
                    temporal.dev_resumen_analizados
                    where contri = '{self.jd.contri}' and
                    usuario = '{self.jd.usuario}'  {condicion_estado}
                    {condicion_memoria} {condicion_periodos}
                    order by fila asc
                ; """

    def get_sql_resumen_verifica(self):
        '''resumen verifica'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f""" select distinct  valor1, valor2, fila from
                        temporal.dev_resumen_verifica
                        where contri = '{self.jd.contri}' and
                        usuario = '{self.jd.usuario}'  {condicion_estado}
                        {condicion_memoria} {condicion_periodos}
                        order by fila asc; """

    def get_sql_resumen_resultados(self):
        '''resumen resultados'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f""" select valor1, valor2, fila from
                    temporal.dev_resumen_resultados
                    where contri = '{self.jd.contri}' and
                    usuario = '{self.jd.usuario}' {condicion_estado}
                    {condicion_memoria} {condicion_periodos}
                    order by fila asc
                ; """

    def get_sql_resumen_resultados_obs(self):
        '''resumen observaciones'''
        condicion_estado, condicion_memoria, condicion_periodos = self.get_filtros_parciales_clase()
        return f""" select observaciones from temporal.dev_observaciones
                    where contri = '{self.jd.contri}' and
                    usuario = '{self.jd.usuario}'  {condicion_estado}
                    {condicion_memoria} {condicion_periodos}
                    order by fila asc; """

    # 1 guardado memoria
    def get_sql_resumen_tramites(self):
        '''resumen tramites'''

        consulta = f"""select a.idmemoria id, a.contri,
                        a.fecha_analisis::date::varchar fecha_analisis,
                        a.usuario, a.numero_tramite,
                        a.estado, a.periodo_inicial::varchar periodo_inicial,
                        a.periodo_final::varchar periodo_final,
                        snt_monto_solicitado, monto_a_devolver_calculado,
                        b.razon_social,
                        (time_graba_memoria - time_inicia)::time::varchar
                        resuelto_en,  '{self.nav.perfil}' perfil_observador
                            from public.dev_memoria_casos a inner join
                            rucsri.dev_iva_contris_llegan b
                            on a.contri = b.contri
                            where   estado = 'DEFAULT';"""

        match (self.nav.perfil):
            # Administrador
            case 'Administrador':
                match int(self.jd.huesped):
                    case 1:
                        consulta = f"""select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                        fecha_analisis,a.usuario,
                                        a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial,
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                        '{self.nav.perfil}' perfil_observador
                                        from public.dev_memoria_casos a inner
                                         join rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where estado = 'SAV' ;
                                        """
                    case 2:
                        consulta = f""" select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                         fecha_analisis,a.usuario, 
                                         a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial, 
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                        '{self.nav.perfil}' perfil_observador
                                        from public.dev_memoria_casos a inner
                                         join rucsri.dev_iva_contris_llegan b
                                        on a.contri = b.contri
                                        where estado = 'APR';
                                    """

                    case 3:
                        consulta = f"""select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                        fecha_analisis,a.usuario,
                                        a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial,
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                        '{self.nav.perfil}' perfil_observador
                                        from public.dev_memoria_casos a
                                        inner join
                                        rucsri.dev_iva_contris_llegan b
                                        on a.contri = b.contri
                                        where  estado in ('ERR','BOR');
                                    """

                    case 4: consulta = f""" with tramites as (
                                            select distinct numero_tramite
                                            from public.dev_memoria_casos a
                                            inner join
                                            rucsri.dev_iva_contris_llegan b
                                                on a.contri = b.contri
                                            ), losdups as (
                                            select numero_tramite from
                                                public.dev_memoria_casos
                                                where numero_tramite in
                                                (select *from tramites)
                                                group by 1 having
                                                count(numero_tramite) > 1 and
                                                count(distinct usuario) >1
                                            )  select a.idmemoria id, a.contri,
                                            a.fecha_analisis::date::varchar
                                            fecha_analisis,a.usuario,
                                            a.numero_tramite, a.estado,
                                            a.periodo_inicial::varchar
                                            periodo_inicial,
                                            a.periodo_final::varchar
                                             periodo_final,
                                            snt_monto_solicitado,
                                            monto_a_devolver_calculado,
                                            b.razon_social,
                                            (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                            '{self.nav.perfil}' perfil_observador
                                            from public.dev_memoria_casos a
                                            inner join rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where 
                                            numero_tramite in
                                              ( select *from losdups)"""



            # end Aministrador
            case 'Supervisor':
                match int(self.jd.huesped):
                    case 1:
                        consulta = f"""with thead as (select distinct username
                                        from public.dev_usuario_cad_iva
                                        where lower(supervisor_usuario) =
                                         lower('{self.nav.username}')
                                            and perfil = 'Analista'
                                        )
                                        select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                        fecha_analisis,a.usuario,
                                        a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial,
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                        '{self.nav.perfil}' perfil_observador
                                        from public.dev_memoria_casos a inner
                                         join rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where estado = 'SAV' and usuario in
                                            (select *from thead) ;
                                        """
                    case 2:
                        consulta = f""" select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                         fecha_analisis,a.usuario, 
                                         a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial, 
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                        '{self.nav.perfil}' perfil_observador
                                        from public.dev_memoria_casos a inner
                                         join rucsri.dev_iva_contris_llegan b
                                        on a.contri = b.contri
                                        where supervisor_marca =
                                        '{self.nav.username}'
                                        and estado = 'APR';
                                    """

                    case 3:
                        consulta = f"""select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                        fecha_analisis,a.usuario,
                                        a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial,
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                        '{self.nav.perfil}' perfil_observador
                                        from public.dev_memoria_casos a
                                        inner join
                                        rucsri.dev_iva_contris_llegan b
                                        on a.contri = b.contri
                                        where supervisor_marca =
                                        '{self.nav.username}' and
                                        estado in ('ERR','BOR');
                                    """

                    case 4: consulta = f""" with tramites as (
                                            select distinct numero_tramite
                                            from public.dev_memoria_casos a
                                            inner join
                                            rucsri.dev_iva_contris_llegan b
                                                on a.contri = b.contri
                                                where
                                                supervisor_marca =
                                                '{self.nav.username}'
                                            ), losdups as (
                                            select numero_tramite from
                                                public.dev_memoria_casos
                                                where numero_tramite in
                                                (select *from tramites)
                                                group by 1 having
                                                count(numero_tramite) > 1 and
                                                count(distinct usuario) >1
                                            )  select a.idmemoria id, a.contri,
                                            a.fecha_analisis::date::varchar
                                            fecha_analisis,a.usuario,
                                            a.numero_tramite, a.estado,
                                            a.periodo_inicial::varchar
                                            periodo_inicial,
                                            a.periodo_final::varchar
                                             periodo_final,
                                            snt_monto_solicitado,
                                            monto_a_devolver_calculado,
                                            b.razon_social,
                                            (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                            '{self.nav.perfil}' perfil_observador
                                            from public.dev_memoria_casos a
                                            inner join rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where 
                                            numero_tramite in
                                              ( select *from losdups)"""
            case 'Analista':
                match int(self.jd.huesped):
                    case 1:
                        consulta = f"""select a.idmemoria id, a.contri,
                                        a.fecha_analisis::date::varchar
                                        fecha_analisis,a.usuario,
                                        a.numero_tramite,
                                        a.estado, a.periodo_inicial::varchar
                                        periodo_inicial,
                                        a.periodo_final::varchar periodo_final,
                                        snt_monto_solicitado,
                                        monto_a_devolver_calculado,
                                        b.razon_social,
                                        (time_graba_memoria - time_inicia)::time::varchar
                                        resuelto_en,  '{self.nav.perfil}'
                                        perfil_observador
                                        from public.dev_memoria_casos a
                                        inner join
                                        rucsri.dev_iva_contris_llegan b
                                        on a.contri = b.contri
                                        where
                                        usuario = '{self.nav.username}'
                                        and estado = 'APR';
                                        """
                    case 2: consulta = f""" select a.idmemoria id, a.contri,
                                            a.fecha_analisis::date::varchar
                                            fecha_analisis,a.usuario,
                                            a.numero_tramite,
                                            a.estado,
                                            a.periodo_inicial::varchar
                                            periodo_inicial, 
                                            a.periodo_final::varchar
                                            periodo_final,
                                            snt_monto_solicitado,
                                            monto_a_devolver_calculado,
                                            b.razon_social,
                                            (time_graba_memoria - time_inicia)::time::varchar
                                            resuelto_en,
                                            '{self.nav.perfil}'
                                            perfil_observador
                                            from public.dev_memoria_casos a
                                            inner join
                                            rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where
                                            usuario = '{self.nav.username}' and
                                            estado = 'FIN'; """

                    case 3: consulta = f""" select a.idmemoria id, a.contri,
                                            a.fecha_analisis::date::varchar
                                            fecha_analisis, a.usuario,
                                            a.numero_tramite,
                                            a.estado,
                                            a.periodo_inicial::varchar
                                            periodo_inicial,
                                            a.periodo_final::varchar
                                            periodo_final,
                                            snt_monto_solicitado,
                                            monto_a_devolver_calculado,
                                            b.razon_social,
                                            (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                            '{self.nav.perfil}'
                                            perfil_observador
                                            from public.dev_memoria_casos a
                                            inner join
                                            rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where
                                            usuario = '{self.nav.username}' and
                                             estado = 'SAV'; """
                    case 4: consulta = f""" select a.idmemoria id, a.contri,
                                            a.fecha_analisis::date::varchar
                                            fecha_analisis,a.usuario,
                                            a.numero_tramite,
                                            a.estado,
                                            a.periodo_inicial::varchar
                                            periodo_inicial,
                                            a.periodo_final::varchar
                                            periodo_final,
                                            snt_monto_solicitado,
                                            monto_a_devolver_calculado,
                                            b.razon_social,
                                            (time_graba_memoria - time_inicia)::time::varchar resuelto_en,
                                            '{self.nav.perfil}' perfil_observador
                                            from public.dev_memoria_casos a
                                            inner join rucsri.dev_iva_contris_llegan b
                                            on a.contri = b.contri
                                            where
                                            usuario = '{self.nav.username}' and
                                            estado = 'BOR'; """
        return consulta

    def get_sql_supervisores(self):
        '''supervisores'''
        perfil = self.nav.perfil
        if perfil == 'Analista':
            perfil = 'Supervisor'
        return f""" select supervisor nombre from public.dev_usuario_cad_iva
                    where username = '{self.jd.usuario}'
                """

    def get_sql_resumen_tramites_grupo(self):
        '''resumen de tramites grupo'''
        consulta = f"""select a.idmemoria id, a.contri, b.razon_social,
                        a.periodo_inicial::varchar periodo_inicial,
                        a.periodo_final::varchar periodo_final,
                        a.numero_tramite,
                        snt_fecha_ingreso::date::varchar snt_fecha_ingreso,
                        a.usuario, c.nombre nombre_analista,
                        a.supervisor_marca, d.nombre nombre_supervisor,
                        a.fecha_analisis::date::varchar fecha_analisis,
                        time_graba_memoria::varchar time_graba_memoria,
                        time_inicia::varchar time_inicia,
                        time_actualiza_memoria::varchar time_actualiza_memoria,
                        (time_graba_memoria - time_inicia)::time::varchar
                        resuelto_en, num_excel_filas,
                        monto_excel_identificado, num_providencias,
                        num_descartados,
                        snt_monto_solicitado, monto_a_devolver_calculado,
                            a.estado, 'Analista' perfil_observador
                        from public.dev_memoria_casos a
                            inner join rucsri.dev_iva_contris_llegan b
                            on a.contri = b.contri
                            inner join public.dev_usuario_cad_iva c
                            on lower(c.username) = lower(a.usuario)
                            left join public.dev_usuario_cad_iva d
                            on lower(d.username) = lower(a.supervisor_marca)
                            where idmemoria = {self.jd.memoria};
                    """
        return consulta

    def get_sql_informe_retencion_num_filas(self, z):
        '''   para obtener numero de filas'''
        return f""" select count(1) from temporal.dev_informe_retencion
                    where contri = '{z}'  and estado='INA'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_final}'
                    and usuario = '{self.jd.usuario}'; """

    # para obtener ingresados sumarizados
    def get_sql_informe_retencion_ing_sumarizado(self, z):
        '''informe retencion sumarizado'''
        return f""" select extract(year from fecha_emision) anio,
                    extract(month from fecha_emision) mes,
                        sum(valor_retenido) ingresados
                     from temporal.dev_cargas_archivos where contri = '{z}'
                    and periodo_inicial = '{self.jd.periodo_inicial}' and
                    periodo_final = '{self.jd.periodo_final}' and
                    usuario = '{self.jd.usuario}'
                    and estado = 'INA'
                    group by 1,2; """

    def get_sql_cadena_iva_reporte(self) -> str:
        '''cadena iva reporte'''
        return f""" select distinct  a.anio_fiscal anio, a.mes_fiscal mes,
                    camino, a.impuesto_causado, a.ct_mes_actual,
                    a.sct_adquisicion_mesanterior,
                    a.sct_retenciones_mesanterior,b.valor_retencion
                    valor_retencion_valida, a.numero_adhesivo,
                    a.fecha_recepcion,
                    tot_impuesto_pagar_x_percepcion,  diferencia_arr_ct,
                    diferencia_x_ct,  diferencia_adquisiciones,
                    diferencia_retenciones, ajuste_x_adquisiciones
                    ,sct_x_adquisiciones,	sct_x_retenciones
                    from  temporal.dev_declaraciones_validas a
                        inner join temporal.dev_resultado_analisis_retencion b
                        using(contri, estado,periodo_inicial,
                        periodo_final, usuario)
                        where contri = '{self.jd.contri}' and
                        a.anio_fiscal::int = b.anio and
                        a.mes_fiscal::int = b.mes
                        and b.estado = 'INA' and
                        periodo_inicial = '{self.jd.periodo_inicial}' and
                        periodo_final = '{self.jd.periodo_finalisima}' and
                        usuario = '{self.jd.usuario}'
                        order by 1 asc, 2 asc;
                """

    def get_sql_cadena_iva_reporte_eq(self) -> str:
        '''cadena iva reporte'''
        seccion = f""" with params as (
            select  '{self.jd.contri}' contri, 'INA' estado,
            '{self.jd.periodo_inicial}'::date periodo_inicial,
                    '{self.jd.periodo_finalisima}'::date periodo_final,
                    '{self.jd.usuario}' usuario
        )"""
        if self.jd.procedencia == 'externa':
            seccion = f"""with params as ( select  contri, estado,
                        periodo_inicial,
                        periodo_final,   usuario from dev_memoria_casos where
                        idmemoria = {self.jd.memoria} ) """

        return f""" {seccion},
        validas as (
            select distinct anio_fiscal::int anio_fiscal,
                mes_fiscal::int  mes_fiscal,
                    camino, diferencia_arr_ct, diferencia_x_ct, calculo_ct_adq,
                    calculo_ct_ret,
                    diferencia_adquisiciones, diferencia_retenciones, totales,
                    codigo_impuesto
                      from temporal.dev_declaraciones_validas inner join params
                        using (contri, estado, periodo_inicial,
                        periodo_final, usuario)
        )
        , analisi_ret as (
            select distinct anio anio_fiscal, mes mes_fiscal, valor_retencion
                  from temporal.dev_resultado_analisis_retencion
                insner join params
                using (contri, estado, periodo_inicial, periodo_final, usuario)
        )
        select distinct
            anio_fiscal, mes_fiscal, camino, fecha_recepcion,
            sustitutiva_original tipo_declaracion, numero_adhesivo,
            sct_adquisicion_mesanterior,
            sct_retenciones_mesanterior,
            ajuste_x_adquisiciones, ajuste_x_retenciones, sct_mes_anterior,
            sct_mesanterior_retenciones, total_impuestos_mes_actual,
            ct_factor_proporcionalidad, impuesto_causado, ct_mes_actual,
            retenciones_fuente_iva, sct_x_adquisiciones, sct_x_retenciones,
            tot_impuesto_pagar_x_percepcion, diferencia_arr_ct,
            diferencia_x_ct,
            diferencia_adquisiciones, diferencia_retenciones, totales,
            c.codigo_impuesto, calculo_ct_adq, calculo_ct_ret
                from  temporal.dev_analisis_previo a inner join analisi_ret b
                using(anio_fiscal, mes_fiscal)
                inner join validas c using(anio_fiscal, mes_fiscal)
                inner join params
                using (contri, estado, periodo_inicial, periodo_final, usuario)
                order by 1 asc, 2 asc;
            """

    def get_sql_declaraciones_contri(self):
        '''declaraciones del contribuyente'''
        return f"""select anio_fiscal, mes_fiscal, numero_adhesivo,
                    fecha_recepcion, codigo_impuesto,
                    tot_imp_vnl_mac_iaf_1260,  crt_acu_fap_2130,
                        impuesto_causado_2140, credito_tributario_mac_2150,
                        saldo_crt_cle_man_2160, saldo_crt_rfu_man_2170,
                        rfu_mes_actual_2200, saldo_crt_clo_ipr_msi_2220,
                        saldo_crt_rfu_msi_2230,
                        AJU_IDR_PC_IPT_CRT_MAC_RF_2212,
                        AJU_IDR_PC_IPT_CRT_MAC_2210,
                        SUBTOTAL_APA_AIP_2250, TOT_IMP_APA_PERCEPCION_2270,
                            TOT_IVA_RETENIDO_2550,  TOTAL_PAGADO_2640,
                            VLB_EAF_TDC_450,        TOT_VLN_EAF_TDC_480
                from owbtar.owb_ods_declaraciones_104
                where numero_identificacion = '{self.jd.contri}'
                and (anio_fiscal || '-' || mes_fiscal || '-01')::date-1 between
                 ('{self.jd.periodo_inicial}' )::date-1
                  and  (date_trunc('month', '{self.jd.periodo_final}'::date) +
                  interval '1 month' - interval '1 day')::date
                order by anio_fiscal asc, mes_fiscal asc;
                """

    def get_sql_listado_out_range(self):
        '''descartados'''
        return f"""
                    select agente_retencion, fecha_emision, serie,
                    comprobante, autorizacion, porcentaje_iva,
                    porcentaje_retencion_iva,
                    valor_retenido, fecha_carga::varchar fecha_carga,
                    razon --, string_agg(distinct razon,',') razon
                     from temporal.dev_cargas_archivos_nv
                    where contri = '{self.jd.contri}'
                    and periodo_inicial = '{self.jd.periodo_inicial}'
                    and periodo_final = '{self.jd.periodo_final}'
                    and estado='INA'  and usuario = '{self.jd.usuario}';
                    --group by 1,2,3,4,5,6,7,8,9
                    ;
                """

    def get_sql_futuras(self):
        '''comprensaion futura'''
        seccion = f""" with params as (
        select  '{self.jd.contri}' contri, 'INA' estado,
                '{self.jd.periodo_inicial}'::date periodo_inicial,
                '{self.jd.periodo_finalisima}'::date periodo_final,
                '{self.jd.usuario}' usuario
        )"""
        if self.jd.procedencia == 'externa':
            seccion = f"""with params as ( select  contri, estado,
                        periodo_inicial,
                        periodo_final,   usuario from dev_memoria_casos
                        where idmemoria = {self.jd.memoria} ) """
        return f"""{seccion}
                    select anio_fiscal, mes_fiscal, camino, fecha_recepcion,
                            sustitutiva_original, numero_adhesivo,
                            sct_credito_mes_anterior_rca_adq_ret,
                            ajuste_x_adquisiciones, saldo_de_ct_mes_anterior,
                            impuesto_causado, ct_mes_actual,
                            retenciones_fuente_iva,
                            tot_impuesto_pagar_x_percepcion,
                            compensa_futuro_reco_sol_atendida,
                            saldo_cred_resulta_next_mes,
                            impuesto_pagar_resulta_mes
                            from temporal.dev_compensa_futuro a
                            inner join params b
                                using (contri, estado, periodo_inicial,
                                periodo_final, usuario)
                            order by 1 asc, 2 asc;"""
