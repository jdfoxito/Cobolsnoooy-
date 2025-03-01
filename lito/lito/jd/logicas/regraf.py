"""regraf,
Funcionalidades:

  -  Graficas

    +-------------------+-------------------+-------------------------------+
    | Fecha             | Modifier          | Descripcion                   |
    +-------------------+-------------------+-------------------------------+
    | 23DIC2023         | jagonzaj          | estadisticas de transparecnia |
    +-------------------+-------------------+-------------------------------+

ESTANDAR PEP8

"""

from jd import fox


class Graficas:
    '''transparencia'''

    def get_deta(self, cadena):
        '''detalle'''
        return fox.db.get_vector(cadena)

    def categorias(self):
        '''categorias'''
        df_grupo = self.get_deta("""select distinct  codreg
                                        from public.dev_usuario_cad_iva; """)
        return df_grupo

    def traer_estad(self):
        '''estadistica'''
        df_grupo = self.get_deta("""select codreg, a.estado, count(1)::int numero
            from dev_memoria_casos a inner join dev_usuario_cad_iva b on a.usuario = b.username
                group by 1, 2 order by estado asc, codreg asc;
        """)
        return df_grupo

    def traer_montos(self):
        '''clase con propiedades unicamente '''
        df_grupo = self.get_deta(""" with ta as (
                                    select extract(year from time_inicia)::int yea, extract(month from time_inicia)::int mon,
                                        extract(year from time_inicia )::int -2000 || '-' ||
                                        SUBSTRING(TO_CHAR(time_inicia::date, 'Month'),1,3) mes, sum(monto_a_devolver_calculado)/1000000  monto_devolver
                                    from dev_memoria_casos where estado not in ('BOR')  and fecha_analisis < '2024/08/01' group by 1,2,3
                                            order by 1 asc, 2 asc
                                    ), tb as (
                                    select extract(year from time_inicia)::int yea, extract(month from time_inicia)::int mon,
                                        extract(year from time_inicia )::int -2000 || '-' ||
                                        SUBSTRING(TO_CHAR(time_inicia::date, 'Month'),1,3) mes, sum(snt_monto_solicitado)/1000000  monto_solicitado
                                    from dev_memoria_casos where estado not in ('BOR')  and fecha_analisis < '2024/08/01' group by 1,2,3
                                            order by 1 asc, 2 asc )

                                    select *, monto_solicitado - monto_devolver  brecha  from ta a inner join tb b using(yea, mon, mes)
        """)
        return df_grupo

    def traer_empresas(self):
        '''traer empresas'''
        df_grupo = self.get_deta(""" with ta as (
                                select  numero_ruc, razon_social, count(numero_tramite) numero_tramites,  sum(b.monto_solicitado::float)/1000000::float montosolicitado from
                                        tramites.tra_tramites a inner join tramites.tra_detalles_tramite b using(id_tramite) where monto_solicitado is not null
                                        group by 1,2 order by 4 desc limit 100

                                ),
                                tb as (
                                    select contri, sum(monto_a_devolver_calculado)/1000000  monto_a_devolver_calculado
                                from dev_memoria_casos where estado not in ('BOR') group by 1
                                        order by 1 asc, 2 asc
                                    )
                                    select a.numero_ruc, a.razon_social, a.numero_tramites,
                                            round(a.montosolicitado::numeric ,2) montosolicitado,
                                            round(b.monto_a_devolver_calculado, 2) monto_a_devolver_calculado from ta a inner join tb b on a.numero_ruc = b.contri order by 4 desc limit 10


                            """)
        return df_grupo

    def reagrupar(self, df, estado):
        '''reagrupacion'''
        dfsec = df[df["estado"] == estado]
        seriesdata = []
        for ix, fila in dfsec.iterrows():
            seriesdata.append([fila.codreg, fila.numero])
        return seriesdata

    def graf_tramitacion(self):
        '''tramites categorizados'''
        df = self.traer_estad()
        df.numero = df.numero.astype(int)
        dfcats = self.categorias()
        zonas = dfcats["codreg"].values.tolist()
        serieslista = []
        estdos = df["estado"].unique().tolist()
        for estado in estdos:
            seriesdata = self.reagrupar(df, estado)
            estd = ''
            match (estado):
                case 'APR':  estd = 'Trámites Aprobados'
                case 'FIN':  estd = 'Trámites Finalizados'
                case 'BOR':  estd = 'Trámites Borrados'
                case 'SAV':  estd = 'Trámites Guardados'
            serieslista.append(
                            {
                                "type": "bar",
                                "stack": "WEATHER1",
                                "name": estd,
                                "data": seriesdata,
                                "encode": {
                                    "x": [
                                        0
                                    ],
                                    "y": [
                                        1
                                    ]
                                }
                            })

        tipo = {
                    "tooltip": {
                        "trigger": "axis"
                    },
                    "title": {
                            "text": 'Trámites Atendidos por Zonales',
                            "left": 'center'                        
                    },                
                    "xAxis": {
                        "data": zonas
                    },
                    "yAxis": {
                    },
                    'grid': {
                        "right": '10%',
                        "left": '5%'
                    },
                    "series": serieslista
                    ,
                    "legend": {
                        'orient': 'vertical',
                        'right': 100
                    }
                }
        return tipo

    def devuelto_vs_atentido(self):
        '''devueltos vs atendidos'''
        colors = ['#5470C6', '#91CC75', '#EE6666']

        df_mons = self.traer_montos()
        meses = df_mons["mes"].unique().tolist()

        fila_dev = df_mons["monto_devolver"].values.tolist()
        fila_sol = df_mons["monto_solicitado"].values.tolist()
        fila_bre = df_mons["brecha"].values.tolist()

        tipo = {
            "color": colors,
            "title": {
                    "text": 'Monto Devuelto vs Solicitado',
                    "left": 'center',
                    "top": 100
            }, 
            "tooltip": {
                    "trigger": 'axis',
                    "axisPointer": {
                        "type": 'cross'
                    }
            },
            "grid": {
                "right": '10%',
                "left": '5%',
                "containLabel": "true"
            },
            "legend": {
                "fontSize": 20,
                "data": ['Devuelto', 'Solicitado', 'Brecha']
            },
            "xAxis": [
                {
                "type": 'category',
                "axisTick": {
                    "alignWithLabel": "true"
                },
                    "data": meses
                }
            ],
            "yAxis": [
                {
                    "type": 'value',
                    "name": 'Devuelto',
                    "position": 'right',
                    "alignTicks": "true",
                    "fontSize": '30',
                    "axisLine": {
                        "show": "true",
                        "lineStyle": {
                            "color": colors[0]
                            }
                },
                "axisLabel": {
                    "formatter": '{value} Mill'
                }
                },
                {
                    "type": 'value',
                    "name": 'Solicitado',
                    "position": 'right',
                    "alignTicks": "true",
                    "offset": 80,
                    "axisLine": {
                            "show": "true",
                            "lineStyle": {
                            "color": colors[1]
                        }
                },
                    "axisLabel": {
                        "formatter": '{value} Mill'
                }
                },
                {
                    "type": 'value',
                    "name": 'Brecha',
                    "position": 'left',
                    "alignTicks": "true",
                    "axisLine": {
                        "show": "true",
                        "lineStyle": {
                            "color": colors[2]
                        }
                    },
                    "axisLabel": {
                        "formatter": '{value} Mill'
                }
                }
            ],
            "series": [
                {
                    "name": 'Monto Devuelto',
                    "type": 'bar',
                    "data": fila_dev
                },
                {
                    "name": 'Monto Solicitado',
                    "type": 'bar',
                    "yAxisIndex": 1,
                    "data": fila_sol
                },
                {
                    "name": 'Brecha',
                    "type": 'line',
                    "yAxisIndex": 2,
                    "data": fila_bre
                }
            ]
            }
        return tipo

    def empresas(self):
        '''empresas'''
        df = self.traer_empresas()
        emps = df.razon_social.unique().tolist()
        mon_sol = df.montosolicitado.unique().tolist()
        num_tram = df.numero_tramites.unique().tolist()
        mon_dev = df.monto_a_devolver_calculado.unique().tolist()

        tipo = {
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                    "type": 'shadow'
                }
                },
            "legend": {},
            "title": {
                    "text": 'Empresas Total Solicitado vs Atendido',
                    "left": 'center',
                    "top": 100,
                    "right": '10%'
            },
            "grid": {
                "left": '3%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": "true"
            },
            "xAxis": {
                "type": 'value'
            },
            "yAxis": {
                "type": 'category',
                "data": emps
            },
            "series": [
                {
                    "name": 'Monto Solicitado',
                    "type": 'bar',
                    "stack": 'total',
                    "label": {
                        "show": "true"
                        },
                    "emphasis": {
                            "focus": 'series'
                        },
                    "data": mon_sol
                },
                {
                    "name": 'Monto Devuelto',
                    "type": 'bar',
                    "stack": 'total',
                    "label": {
                        "show": "true"
                    },
                    "emphasis": {
                        "focus": 'series'
                    },
                    "data": mon_dev
                },
                {
                    "name": 'Numero Tramites',
                    "type": 'bar',
                    "stack": 'total',
                    "label": {
                        "show": "true"
                    },
                    "emphasis": {
                        "focus": 'series'
                    },
                    "data": num_tram
                },
            ]
        }

        return tipo

    def get_horas(self):
        '''horas'''
        df = self.get_deta("""select extract(dow from  time_inicia) numdia, extract(hour from  time_inicia) hora, count(1) numero_tramites
            from dev_memoria_casos
            --where extract(hour from  time_inicia) between  5 and 23
            group by 1, 2 order by 1 asc;""")
        return df

    def hora_atencion(self):
        '''hora de atencion'''
        days = [
                'Sabado', 'Viernes', 'Jueves',
                'Miercoles', 'Martes', 'Lunes', 'Domingo'
            ]

        datos = []
        df = self.get_horas()
        for x, fila in df.iterrows():
            datos.append([fila.numdia, fila.hora, fila.numero_tramites])

        horas = df.hora.unique().tolist()
        horas.sort()
        horas = [str(int(x)) + "H" for x in horas]

        opcion = {
                    "title": {
                        "text": 'Horas de Atencion'
                    },
                    "legend": {
                        "data": ['horarios'],
                        "left": 'right'
                    },
                    "tooltip": {
                        "position": 'top',
                        "formatter": """function (params) {
                                        return (
                                            params.value[2] +
                                            ' commits in ' +
                                            hours[params.value[0]] +
                                            ' of ' +
                                            days[params.value[1]]
                                        );
                                    }"""


                    },
                    "grid": {
                        "left": 2,
                        "bottom": 10,
                        "right": 10,
                        "containLabel": "true"
                    },
                    "xAxis": {
                        "type": 'category',
                        "data": horas,
                        "boundaryGap": "false",
                        "splitLine": {
                            "show": "true"
                        },
                        "axisLine": {
                            "show": "false"
                        }
                    },
                    "yAxis": {
                        "type": 'category',
                        "data": days,
                        "axisLine": {
                            "show": "false"
                        }
                    },
                    "series": [
                        {
                            "name": 'Horarios',
                            "type": 'scatter',
                            "symbolSize": """function (val) {
                                return val[2] * 2;
                            }""",
                            "data": datos,
                            "animationDelay": """function (idx) {
                                                    return idx * 5;
                                                }"""
                            }
                        ]
                }
        return opcion

    def get_usuarios(self):
        '''traer usuarios'''
        df_grupo = self.get_deta("""  with ta as (
                                        select usuario, count(1) numero_tramites from dev_memoria_casos group by 1 order by 2 desc limit 10
                                    )
                                    select usuario,  estado,  count(1) numero_tramites
                                        from dev_memoria_casos a inner join ta b using(usuario) group by 1, 2 order by 1 asc, 3 desc;


                                    """)
        return df_grupo

    def grafica_usuarios(self):
        '''pintar usuarios'''
        df = self.get_usuarios()

        funciona = df.usuario.unique().tolist()
        df = df.fillna(0)
        df1 = df.pivot(index='usuario', columns='estado', values='numero_tramites')
        df1 = df1.fillna(0)
        df1 = df1.reset_index()
        df1 = df1.drop([1])
        print(f"df1 \n {df1}")

        # dfa = df.groupby("usuario")['estado'].count().reset_index()
        # dfa = dfa[dfa.estado < 4]
        # estados = ['SAV', 'APR', 'BOR', 'FIN']
        # usuarios = dfa.usuario.unique().tolist()
        # for usu in usuarios:
        #    dfu = df[df.usuario == usu]
        #    esta = dfu.estado.unique().tolist()
        #    dife = list(set(estados) - set(esta))
        #    for usa in dife:
        #        dic = {'usuario': usu, 'estado': usa, "numero_tramites": 0}
        #        df = df._append(dic, ignore_index=True)

        lista_guarda = df1.SAV.tolist()
        lista_aproba = df1.APR.tolist()
        lista_borrad = df1.BOR.tolist()
        lista_finali = df1.FIN.tolist()
        lista_borrad = [x * -1 for x in lista_borrad]

        opcion = {
                    "tooltip": {
                                "trigger": 'axis',
                                "axisPointer": {
                                    "type": 'shadow'
                                }
                    },
                    "legend": {
                        "data": ['Guardados', 'Aprobados', 'Finalizados', 'Borrados']
                    },
                    "grid": {
                        "left": '3%',
                        "right": '4%',
                        "bottom": '3%',
                        "top": 100,
                        "containLabel": "true"
                    },
                    "xAxis": [
                        {
                            "type": 'value'
                        }
                    ],
                    "yAxis": [
                        {
                            "type": 'category',
                            "axisTick": {
                                "show": "false"
                            },
                            "data": funciona
                        }
                    ],
                    "series": [
                        {
                            "name": 'Guardados',
                            "type": 'bar',
                            "label": {
                                "show": "true",
                                "position": 'inside'
                            },
                            "emphasis": {
                                "focus": 'series'
                            },
                            "data": lista_guarda
                        },
                        {
                            "name": 'Aprobados',
                            "type": 'bar',
                            "stack": 'Total',
                            "label": {
                                "show": "true"
                            },
                            "emphasis": {
                                "focus": 'series'
                            },
                            "data": lista_aproba
                        },
                        {
                            "name": 'Finalizados',
                            "type": 'bar',
                            "stack": 'Total',
                            "label": {
                                "show": "true"
                            },
                            "emphasis": {
                                "focus": 'series'
                            },
                            "data": lista_finali
                        },
                        {
                            "name": 'Borrados',
                            "type": 'bar',
                            "stack": 'Total',
                            "label": {
                                "show": "true",
                                "position": 'left'
                            },
                            "emphasis": {
                                "focus": 'series'
                            },
                            "data": lista_borrad
                            }
                        ]
                    }
        return opcion
