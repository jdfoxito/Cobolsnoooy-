
/*
+--------------------+--------------------------------------------+
| URL                |  TAX REFUND                                |
|                    |                                            |
+--------------------+--------------------------------------------+
| Diciembre 2023     |V1                                          |
+--------------------+--+-----------------------------------------+
| jagonzaj  19_AB_24 |  incluye eval                              |
|                    |                                            |
+--------------------+--------------------------------------------+
*/
axios.defaults.headers.common["X-CSRFToken"] = $("#csrf_token").val();
const config = {
    headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'X-CSRFToken': $("#csrf_token").val()
    }
}

let g_saldo_adq_ma = ''
let g_saldo_ret_ma = ''
let numerodeperiodos = 0;
let los_adhesivos = '';
let cerrar_ta = 1;
let cerrar_tb = 1;
let pre_flo_txt = 0.0;
let futuro_pasado = 0;
let df_segmentados = []
let aprobados_segmentos = []

$('#div_todos_tabs').hide();
$('#div_barra_menu').hide();
$('#div_tramite').hide();

$('#div_compensa_futuro_final').hide();

let USDollar = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

function replaceAll(string, search, replace) {
    return string.split(search).join(replace);
}
const USDollarDEC = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 20
})

function mes_short(mes) {
    let descripcion = " "
    switch (mes) {

        case 1: descripcion = 'ENE'; break;
        case 2: descripcion = 'FEB'; break;
        case 3: descripcion = 'MAR'; break;
        case 4: descripcion = 'ABR'; break;
        case 5: descripcion = 'MAY'; break;
        case 6: descripcion = 'JUN'; break;
        case 7: descripcion = 'JUL'; break;
        case 8: descripcion = 'AGO'; break;
        case 9: descripcion = 'SEP'; break;
        case 10: descripcion = 'OCT'; break;
        case 11: descripcion = 'NOV'; break;
        case 12: descripcion = 'DIC'; break;
    }
    return descripcion;
}

function mensaje(tipo, texto) {
    Swal.fire({
        title: 'Devoluciones!',
        text: texto,
        icon: tipo,
        showCancelButton: true,
        confirmButtonClass: 'btn btn-primary w-xs me-2 mt-2',
        cancelButtonClass: 'btn btn-danger w-xs mt-2',
        buttonsStyling: false,
        showCloseButton: true
    })
}

const isdigito = (value) => {
    const val = Number(value) ? true : false
    return val
}

function quitarMoneda(n) {
    let m = '0';
    m = n.replace(/\$/g, "");
    m = replaceAll(m, ',', '');
    return m;
}

function num(n) {
    return parseFloat(n).toFixed(2)
}

function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function fun_rango_fecha(start, end) {
    let startDate = Date.parse(start);
    let endDate = Date.parse(end);
    if (isNaN(startDate)) {
        mensaje("error", "Ingrese una fecha valida de inicio");
        return false;
    }
    if (isNaN(endDate)) {
        mensaje("error", "Ingrese una fecha valida final");
        return false;
    }

    let difference = (endDate - startDate) / (86400000);
    if (difference < 0) {
        mensaje("error", "La fecha final debe ser mayor a la de inicio");
        return false;
    }
    return true;
}

const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',

});

function sortDeclaraciones() {
    let table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("tabla_declaraciones_cumplen");
    switching = true;
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[0];
            y = rows[i + 1].getElementsByTagName("TD")[0];
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

function fun_novedades(egipto) {
    let texto = '';
    if (egipto.length > 0) {
        $.each(egipto, function (i, item) {
            let tipo = 'info';
            if (egipto[i].category == 'fantasma') {
                tipo = 'danger';
                $('#div_todos_tabs tbody').hide();
                $('#div_barra_menu tbody').hide();
            }

            if (['archivo', 'contri', 'fechas'].includes(egipto[i].category)) {
                tipo = 'danger';
            }

            texto += `<li> <div class="alert alert-${tipo} alert-dismissible alert-label-icon rounded-label fade show" role="alert">
                            <i class="ri-error-warning-line label-icon"></i><strong>${item.mensaje}</strong> 
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div></li>`
        });

        let lista = $("#div_novedades").append('<ul></ul>').find('ul');
        lista.append(texto);
    }

}

function fx_totalizar(tabla) {
    let tablaResumen4 = document.getElementById(tabla);
    let trResumen4 = tablaResumen4.getElementsByTagName("tr");
    let valor_declarado = 0;
    let mayores = 0;
    let diferencias = 0;
    let ingresados = 0;
    let no_consta_base = 0;
    let no_sustentado = 0;
    let negados = 0;
    let a_devolver = 0;
    const ntotales = []
    for (let k = 0; k < trResumen4.length - 1; k++) {
        if (trResumen4[k].getElementsByTagName("td")[3]) {
            let valor_declarado_ = (trResumen4[k].getElementsByTagName("td")[2]).innerText;
            let valor_declarado_celda = parseFloat(quitarMoneda(valor_declarado_))
            valor_declarado = valor_declarado + valor_declarado_celda
            let mayor_celda = 0;
            let pre_mayor = trResumen4[k].getElementsByTagName("td")[3]
            if (pre_mayor) {
                if (pre_mayor.getElementsByTagName("input").length > 0) {
                    if (pre_mayor.getElementsByTagName("input")[0]) {
                        mayor_celda = parseFloat(pre_mayor.getElementsByTagName("input")[0].value)
                        mayores = mayores + mayor_celda
                    }
                }
            }

            let diferencia_actualizar = 0;
            if ((parseFloat(valor_declarado_celda) > parseFloat(mayor_celda)) && (parseFloat(mayor_celda) >= 0)) {
                diferencia_actualizar = parseFloat(valor_declarado_celda) - parseFloat(mayor_celda).toFixed(2);
            }
            diferencias = diferencias + diferencia_actualizar
            if (trResumen4[k].getElementsByTagName("td")[5]) {
                ingresados = ingresados + parseFloat((trResumen4[k].getElementsByTagName("td")[5]).innerText)
            }
            if (trResumen4[k].getElementsByTagName("td")[6]) {
                no_consta_base = no_consta_base + parseFloat((trResumen4[k].getElementsByTagName("td")[6]).innerText)
            }
            if (trResumen4[k].getElementsByTagName("td")[7]) {
                no_sustentado = no_sustentado + parseFloat((trResumen4[k].getElementsByTagName("td")[7]).innerText)
            }
            if (trResumen4[k].getElementsByTagName("td")[8]) {
                negados = negados + parseFloat((trResumen4[k].getElementsByTagName("td")[8]).innerText)
            }
            if (trResumen4[k].getElementsByTagName("td")[10]) {
                let pre_devuelve = parseFloat((trResumen4[k].getElementsByTagName("td")[10]).innerText)
                a_devolver = a_devolver + pre_devuelve
                ntotales.push({ anio: parseInt((trResumen4[k].getElementsByTagName("td")[0]).innerText), mes: parseInt((trResumen4[k].getElementsByTagName("td")[1]).innerText), total: parseFloat(pre_devuelve).toFixed(2) })

            }
        }
    }

    $('#tabla_retenciones_periodo tfoot').empty();
    $('#tabla_retenciones_periodo tfoot').html('');


    $('<tr>').html(`<td colspan="2"> Totales </td>
    <td> ${parseFloat(valor_declarado).toFixed(2)} </td>
    <td> ${parseFloat(mayores).toFixed(2)}  </td>
    <td> ${parseFloat(diferencias).toFixed(2)}</td>
    <td> ${parseFloat(ingresados).toFixed(2)}</td>
    <td> ${parseFloat(no_consta_base).toFixed(2)}</td>
    <td> ${parseFloat(no_sustentado).toFixed(2)}</td>
    <td> ${parseFloat(negados).toFixed(2)}</td>
    <td> ${parseFloat(a_devolver).toFixed(2)}</td>
    <td class="td_resaltado_tr"> ${parseFloat(a_devolver).toFixed(2)}</td>                                                        
    `
    ).appendTo('#tabla_retenciones_periodo tfoot');

    let tabla_cadena = document.getElementById("tab_cadena_iva_transpuesta");
    let tabla_cadena_filas = tabla_cadena.getElementsByTagName("tr");
    let listanios = []
    let listameses = []
    if (ntotales.length > 0) {
        for (var k = 2; k < tabla_cadena_filas.length - 1; k++) {
            if (tabla_cadena_filas[k].getElementsByTagName("td")) {

                if (tabla_cadena_filas[k].getElementsByTagName("td").length > 0) {

                    if (tabla_cadena_filas[k].getElementsByTagName("td")[0]) {
                        fila = ((tabla_cadena_filas[k].getElementsByTagName("td")[0]).innerText).trim()
                        if (fila == 'AÑO FISCAL') {
                            for (var m = 1; m < tabla_cadena_filas[k].getElementsByTagName("td").length; m++) {
                                listanios.push(parseInt(tabla_cadena_filas[k].getElementsByTagName("td")[m].innerText))
                            }
                        }
                        if (fila == 'MES FISCAL') {
                            for (var m = 1; m < tabla_cadena_filas[k].getElementsByTagName("td").length; m++) {
                                listameses.push(parseInt(tabla_cadena_filas[k].getElementsByTagName("td")[m].innerText))
                            }
                        }
                        if (fila == 'RETENCIONES EN LA FUENTE DE IVA QUE LE HAN SIDO EFECTUADAS') {
                            for (var l = 0; l < tabla_cadena_filas[k].getElementsByTagName("td").length; l++) {
                                //if (l>1){
                                var totalBuscado = ntotales.find((fox) => (fox.anio == listanios[l] && fox.mes == listameses[l]))
                                if (totalBuscado) {
                                    tabla_cadena_filas[k].getElementsByTagName("td")[l + 1].innerHTML = totalBuscado.total;
                                }
                                //}
                            }
                        }
                    }
                }
            }
        }
    }
}

function compensar_futuro_pasado(sumaValores_arrastre, suma_cordo_analisis, compensa, grabar) {
    const ruc = $("#txt_ruc_ingresado").val();
    const periodo1 = $("#txt_desde").val();
    const periodo2 = $("#txt_hasta").val();
    const requesta = {
        param1: ruc,
        param2: periodo1,
        param3: periodo2,
        param4: 'F',
        param5: ($("#span_tramite").html()).trim(),
        lastre: sumaValores_arrastre,
        ia: suma_cordo_analisis,
        agrega: compensa,
        grab: grabar,
        usuario: $("#csrf_user").val(),
        mu: $("#in_xyz").val()
    }
    axios.post(`get_elecciones_futuras`, JSON.stringify(requesta), config)
        .then(function (resultado) {
            if (resultado.data.declas_futura) {
                if (resultado.data.declas_futura.length > 0) {
                    let polinesia = resultado.data.declas_futura;
                    let nuevazelanda = resultado.data.nfilas_futuras;
                    let fila_a = resultado.data.valor_Declarado_ultimo_mes_xct_riva;
                    let fila_sip = resultado.data.suma_impuesto_pagar;
                    if (resultado.data.vacio === 1) {
                        mensaje("error", "No existen periodos para compensar luego del periodo solicitado!")
                        $('#tab_compensacion_futuro tbody').empty();
                        $('#tab_compensacion_futuro tbody').html('');
                        $("#li_a_compensa_futuro").hide();
                        let tres_diferencia = parseFloat(quitarMoneda($('#h6_liq_9').text())) - parseFloat(quitarMoneda($('#h6_liq_10').text()));
                        let tres_diferencia_exp = tres_diferencia < 0 ? 0 : parseFloat(tres_diferencia).toFixed(2);
                        $('#h6_liq_11').text(USDollar.format(tres_diferencia_exp));
                        $("#spa_graba_devolver").empty();
                        $("#spa_graba_devolver").html(USDollar.format(tres_diferencia_exp));
                        return
                    }
                    $("#div_exportar_excel_futuras").empty();
                    $("#div_exportar_excel_futuras").append(resultado.data.enlace_futuro);
                    $('#span_fila_a').empty();
                    $('#span_fila_a').html(fila_a);
                    $('#h6_liq_10').empty();
                    $('#h6_liq_10').html(fila_sip);
                    $('#h6_liq_10').text(fila_sip);

                    let filab = (parseFloat(parseFloat($('#txt_de_baja').val()) - parseFloat(fila_sip))).toFixed(2);
                    $('#span_fila_b').html(filab);
                    let filac = (parseFloat(filab) - parseFloat(fila_a)).toFixed(2)
                    let filac_exp = (parseFloat(filac) < 0 ? 0 : parseFloat(filac)).toFixed(2)
                    $('#span_fila_c').html(filac_exp);

                    $('#span_fila_obs').html(parseFloat(filac_exp) == 0.00 ? '' : 'CONFORME LA ÚLTIMA DECLARACIÓN PRESENTADA POR EL CONTRIBUYENTE, EL SALDO A FAVOR DE RETENCIONES EN LA FUENTE RECOMPENSADO O DISMINUIDO EN PERÍODOS POSTERIORES AL SOLICITADO');

                    let tres_diferencia = parseFloat(quitarMoneda($('#h6_liq_9').text())) - parseFloat($('#h6_liq_10').text());
                    let tres_diferencia_exp = tres_diferencia < 0 ? 0 : parseFloat(tres_diferencia).toFixed(2);

                    let el10 = $('#h6_liq_10').text()
                    let el11 = tres_diferencia_exp

                    if (el10.toString() == '') {
                        el10 = '0';
                    }
                    if (el11.toString() == '') {
                        el11 = '0';
                    }

                    const requesta = {
                        param1: ruc,
                        param2: periodo1,
                        param3: periodo2,
                        param5: ($("#span_tramite").html()).trim(),
                        el_diez: el10,
                        el_once: el11,
                        expediente: 1,
                        usuario: $("#csrf_user").val(),
                        mu: $("#in_xyz").val()
                    }
                    axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
                        .then(function (resultadoD) {
                            if (parseInt(resultadoD.data.valida) == -100) {
                                window.location = "/account/login";
                            }

                        });
                    $('#h6_liq_10').text(USDollar.format($('#h6_liq_10').text()));
                    $('#h6_liq_11').text(USDollar.format(tres_diferencia_exp));
                    $("#spa_graba_devolver").empty();
                    $("#spa_graba_devolver").html(USDollar.format(tres_diferencia_exp));
                    $('#tab_compensacion_futuro tbody').empty();
                    $('#tab_compensacion_futuro tbody').html('');
                    if (polinesia.length > 0) {

                        $.each(polinesia, function (i, item) {
                            let descripcion = polinesia[i].fx_1;
                            let tempdesc = descripcion;
                            descripcion = get_descripciones(descripcion);
                            let xinternas = '';
                            let especial1 = 0;
                            let agregarfilasvacias = 0;
                            if (['sct_retenciones_mesanterior', 'sct_adquisicion_mesanterior', 'sct_x_adquisiciones', 'sct_x_retenciones'].includes(tempdesc)) {
                                especial1 = 1;
                            }
                            if (['total_impuesto_a_pagar_2610'].includes(tempdesc)) {
                                agregarfilasvacias = 1;
                            }
                            for (let k = 1; k <= nuevazelanda + 1; k++) {
                                let elementox = 'polinesia[i].fx_' + k;
                                let elementoy = eval(elementox);
                                if (k == 1) {
                                    elementoy = descripcion;
                                }
                                let especial = 0;
                                if ((k >= 2) && (['compensa_futuro_reco_sol_atendida'].includes(tempdesc))) {
                                    especial = 1;
                                }
                                if ((k >= 2) && (['mes_fiscal'].includes(tempdesc))) {
                                    elementoy = mes_short(parseInt(elementoy));
                                }
                                if (especial === 0) {
                                    if (k == 1) {
                                        xinternas = xinternas + `<td style="width:25%"><label class="form-check-label" for="formCheckboxRight1">${elementoy}</label></td>`;
                                    } else {
                                        xinternas = xinternas + `<td><label class="form-check-label " for="formCheckboxRight1">${elementoy}</label></td>`;
                                    }
                                } else {
                                    //if (k>2){
                                    let posicion = '';
                                    let deshabilitar = '';
                                    if (compensa.toString().length > 2) {
                                        let nr = compensa.split('_');
                                        posicion = parseInt(nr[1]);
                                        let valores_agregados = parseFloat(elementoy);
                                        if ((k === posicion) || (valores_agregados > 0)) {
                                            deshabilitar = 'disabled';
                                        }
                                    }

                                    xinternas = xinternas + `<td><input type="text" class="ctxt_futuro" id="txt_${k}_pasadofuturo" placeholder="Valor" value='${elementoy}'  ${deshabilitar}></input>`;
                                    //}
                                }
                            }

                            var bcolor = 'trColorblanco';
                            if (especial1 === 1) {
                                bcolor = 'trColorNNN';
                            }

                            $(`<tr class="${bcolor}">`).html(xinternas).appendTo('#tab_compensacion_futuro tbody');

                            if (agregarfilasvacias === 1) {
                                $(`<tr class="trColorMetallicSeaweed">`).html(`<td colspan="10"> </td>`).appendTo('#tab_compensacion_futuro tbody');
                            }

                        });
                    }
                }
            }
        });
}


function reiniciar_tablas() {
    g_saldo_adq_ma = ''
    g_saldo_ret_ma = ''
    numerodeperiodos = 0;
    los_adhesivos = '';
    cerrar_ta = 1;
    cerrar_tb = 1;
    pre_flo_txt = 0.0;
    futuro_pasado = 0;
    df_segmentados = []
    aprobados_segmentos = []
    $('#div_todos_tabs').hide();
    $('#div_barra_menu').hide();
    $("#p_strong_calculado_en").empty()
    $("#p_strong_duplicados").empty()
    $("#p_strong_descartados").empty()
    $("#p_strong_excel_load").empty()
    $("#p_cruce_retenciones").empty()
    $('#tabla_declaraciones_cumplen tbody').empty();
    $('#tabla_declaraciones_cumplen tbody').html('');
    $('#tabla_declaraciones_no_cumplen tbody').empty();
    $('#tabla_declaraciones_no_cumplen tbody').html('');
    $('#tabla_declaraciones_transpuesta tbody').empty();
    $('#tabla_declaraciones_transpuesta tbody').html('');
    $('#tabla_retenciones_periodo tbody').empty();
    $('#tabla_retenciones_periodo tbody').html('');
    $('#tab_cadena_iva_transpuesta tbody').empty();
    $('#tab_cadena_iva_transpuesta tbody').html('');
    $('#tab_resumen_periodos tbody').empty();
    $('#tab_resumen_periodos tbody').html('');
    $('#tab_Informe_Revision tbody').empty();
    $('#tab_Informe_Revision tbody').html('');
    $('#tab_Informe_Revision_no tbody').empty();
    $('#tab_Informe_Revision_no tbody').html('');
    $('#tab_archivo_fantasmas tbody').empty();
    $('#tab_archivo_fantasmas tbody').html('');
    $('#tab_archivo_fallecidos tbody').empty();
    $('#tab_archivo_fallecidos tbody').html('');
    $('#tab_liquidacion tbody').empty();
    $('#tab_liquidacion tbody').html('');
    $('#tab_resumen_valores tbody').empty();
    $('#tab_resumen_valores tbody').html('');
    $('#tab_verifica_resultados tbody').empty();
    $('#tab_verifica_resultados tbody').html('');
    $('#tab_creditos_tributario tbody').empty();
    $('#tab_creditos_tributario tbody').html('');
    $('#div_novedades').empty();
    $('#div_novedades').html('');
    $('#tab_compensacion_futuro tbody').empty();
    $('#tab_compensacion_futuro tbody').html('');
    $('#tab_archivo_duplicados tbody').empty();
    $('#tab_archivo_duplicados tbody').html('');
    $('#tabla_retenciones_periodo tr > :nth-child(0)').css('background-color', '#f5f5dc');
    $('#tabla_retenciones_periodo tr > :nth-child(1)').css('background-color', '#f5f5dc');
    $('#tabla_retenciones_periodo tr > :nth-child(2)').css('width', '100px');
    $('#tabla_retenciones_periodo tr > :nth-child(3)').css('width', '100px');
    $('#tabla_retenciones_periodo tr > :nth-child(4)').css('width', '110px');
    $("#span_ruc").html('');
    $("#span_razonsocial").html('');
    $("#span_m_contabilidad").html('');
    $("#span_m_fechaingreso").html('');
    $("#span_legal").html('');
    $("#span_rango_declas").html('');
    $("#span_tramite").html('');
    $("#span_tramite_texto").html('');
    $("#p_strong_descartados").html('');
    $("#li_a_tab_contri").hide();
    $("#li_a_cheklist").hide();
    $("#li_a_tab_declaraciones").hide();
    $("#li_a_tab_analisis").hide();
    $("#li_a_tab_revision").hide();
    $("#li_a_tab_retenciones").hide();
    $("#li_a_tab_cadenaiva").hide();
    $("#li_a_resumen_periodos").hide();
    $("#li_a_compensa_futuro").hide();
    $("#li_a_datos_resolucion").hide();
    $('.ctxt_diferencias_adq').attr('disabled', false);
    $('.ctxt_diferencias_ret').attr('disabled', false);
    $("#span_ruc").html('');
    $("#span_razonsocial").html('');
    $("#span_m_contabilidad").html('');
    $("#span_m_fechaingreso").html('');
    $("#span_tipo").html('');
    $("#span_jurisdiccion").html('');
    $("#span_legal").html('');
    cerrar_ta = 1;
    cerrar_tb = 1;
    pre_flo_txt = 0.0;
}

function validaVerificado(valor) {
    let valor_rta = "no"
    if (valor === "S") {
        valor_rta = "SI"
    }
    return valor_rta
}

function verificartramites(escena) {
    reiniciar_tablas();
    $('#div_todos_tabs').show();
    $('#div_barra_menu').show();
    let egipto = '';
    const ruc = $("#txt_ruc_ingresado").val();
    const periodo1 = $("#txt_desde").val();
    const periodo2 = $("#txt_hasta").val();
    const requesta = {
        param1: ruc,
        param2: periodo1,
        param3: periodo2,
        param4: escena.param4,
        usuario: $("#csrf_user").val(),
        mu: $("#in_xyz").val()
    }
    axios.post(`get_fonts`, JSON.stringify(requesta), config)
        .then(function (resultado) {
            egipto = resultado.data.novedades;
            if (resultado.data.detener === 0) {
                $('#div_todos_tabs').show();
                $('#div_barra_menu').show();
                $('#div_tramite').show();
                $("#li_a_tab_contri").show();
                $("#li_a_cheklist").show();
                $("#li_a_tab_declaraciones").show();
                $("#li_a_tab_analisis").show();
                $("#li_a_tab_revision").show();
                $("#li_a_tab_retenciones").show();
                $("#li_a_tab_cadenaiva").show();
                $("#span_legal").html(resultado.data.repre);
                let argelia = resultado.data.contri;
                let kenia = resultado.data.lhistoria;
                if (argelia.length > 0) {
                    $("#span_ruc").html(argelia[0].numero_ruc);
                    $("#span_razonsocial").html(argelia[0].razon_social);
                    let oli = validaVerificado(argelia[0].obligado);
                    $("#span_m_contabilidad").html(oli);
                    $("#span_m_fechaingreso").html(argelia[0].estado);
                    $("#span_tipo").html(argelia[0].clase_contribuyente);
                    $("#span_jurisdiccion").html(argelia[0].jurisdiccion);

                    if (kenia.length > 0) {
                        $("#span_ruc_desde").html(` Desde ${kenia[0].fecha_inicio}  Hasta  ${kenia[0].fecha_fin}  `);
                    }
                } else {
                    mensaje("warning", `NO existe el RUC ${$("#txt_ruc_ingresado").val()} `)
                    $("#span_ruc").html('');
                    $("#span_razonsocial").html('');
                    $("#span_m_contabilidad").html('');
                    $("#span_m_fechaingreso").html('');
                    $("#span_legal").html('');
                    $("#span_rango_declas").html('');
                    $("#span_tramite").html('');
                    $("#span_ruc_desde").html('');
                    return;
                }

                let palestina = resultado.data.tramites;
                $('#tabla_detalle_tramite_xruc tbody').empty();
                $('#tabla_detalle_tramite_xruc tbody').html('');

                if (palestina.length > 0) {
                    $.each(palestina, function (i, item) {

                        $('<tr>').html(`<td></td>
                                        <td style="width:10%">
                                            <div class="form-check form-radio-outline form-radio-primary mb-3">
                                                <input class="form-check-input clase_radio_tramite" type="radio"  
                                                    name="rad_tramites" 
                                                    id="${item.numero_tramite}"
                                                    value="${item.numero_tramite}">
                                            </div>                                    
                                        </td>
                                        <td>${palestina[i].fecha_ingreso}</td>
                                        <td>${palestina[i].numero_tramite}</td>
                                        <td>${palestina[i].estado}</td>
                                        <td>${palestina[i].anio_fiscal}</td>
                                        <td>${palestina[i].mes_fiscal}</td>
                                        <td>${palestina[i].monto_solicitado}</td>
                                        <td>${palestina[i].nombre_sub_tipo_tramite}</td>
                                        <td>${palestina[i].se_resuelve_con}</td>
                                        <td>${palestina[i].prescrito}</td>
                                        <td>                  
                                            <div class="edit">
                                                <button class="btn btn-sm btn-success add_btn_104" >${palestina[i].similares} / PREVIOS ${palestina[i].previos} </button>
                                            </div>
                                        </td>
                                        `
                        ).appendTo('#tabla_detalle_tramite_xruc tbody');
                    });
                } else {
                    mensaje("warning", `el RUC ${$("#txt_ruc_ingresado").val()} no tiene tramites disponibles.`)
                }


                axios.post(`get_declaraciones_periodo`, JSON.stringify(requesta), config)
                    .then(function (resultadoD) {
                        let hay_cumplen = 0;
                        let hay_no_cumplen = 0;
                        let len_no_cumplen = resultadoD.data.len_no_cumplen;

                        df_segmentados = resultadoD.data.segmentados;

                        $("#li_a_tab_declaraciones").html(` Declaraciones (${resultadoD.data.stat}) `)

                        $("#div_exportar_excel_declaraciones").empty();
                        $("#div_exportar_excel_declaraciones").append(resultadoD.data.enlace_declas);

                        if (resultadoD.data.df_cumplen.length > 0) {
                            let polinesia = resultadoD.data.df_cumplen;
                            $('#tabla_declaraciones_cumplen tbody').empty();
                            $('#tabla_declaraciones_cumplen tbody').html('');
                            if (polinesia.length > 0) {

                                $.each(polinesia, function (i, item) {
                                    $('<tr>').html(`<td  id="periodo${polinesia[i].numero_adhesivo}"> ${polinesia[i].anio_fiscal}_${polinesia[i].mes_fiscal} </td>
                                                    <td> ${polinesia[i].fecha_recepcion}  </td>
                                                    <td> ${polinesia[i].numero_adhesivo} </td>
                                                    <td> ${polinesia[i].condicion}  </td>
                                                    <td> ${polinesia[i].codigo_impuesto}  </td>
                                                `
                                    ).appendTo('#tabla_declaraciones_cumplen tbody');
                                });
                                hay_cumplen = 1;
                            }

                        } else {
                            mensaje("warning", " Ninguna declaracion cumple!");

                        }

                        if (resultadoD.data.df_no_cumplen.length > 0) {
                            let micronesia = resultadoD.data.df_no_cumplen;
                            let jakarta = resultadoD.data.periodos_no;
                            let longitudperiodos = resultadoD.data.longitud_no;
                            numerodeperiodos = longitudperiodos

                            $('#tabla_declaraciones_no_cumplen tbody').empty();
                            $('#tabla_declaraciones_no_cumplen tbody').html('');

                            if (micronesia.length > 0) {
                                $.each(micronesia, function (i, item) {
                                    $('<tr style="background-color:#FAECEA">').html(`<th scope="row">
                                                    <input class="form-check-input clase_radio" type="radio"  
                                                        name="${micronesia[i].anio_fiscal}_${micronesia[i].mes_fiscal}"" 
                                                        id="${micronesia[i].numero_adhesivo}"
                                                        value="${micronesia[i].numero_adhesivo}">
                                                </th> 
                                                <td> ${micronesia[i].anio_fiscal}-${micronesia[i].mes_fiscal} </td>
                                                <td> ${micronesia[i].fecha_recepcion} </td>
                                                <td> ${micronesia[i].numero_adhesivo} </td>
                                                <td > ${micronesia[i].codigo_impuesto} </td>
                                                <td style="display:none;"> ${micronesia[i].segmento} </td>
                                                <td style="display:none;"> ${micronesia[i].periocidad} </td>
                                                <td style="display:none;"> ${micronesia[i].conteo} </td>
                                                <td style="display:none;">${micronesia[i].ciclo}</td>
                                                <td style="display:none;">${micronesia[i].num_limite}</td>
                                    
                                                `
                                    ).appendTo('#tabla_declaraciones_no_cumplen tbody');
                                });
                                hay_no_cumplen = 1;
                            }

                            $('#ul_fox a[href="#nav_declaraciones"]').tab('show')
                            $("#li_a_tab_analisis").hide();
                            $("#li_a_tab_revision").hide();
                            $("#li_a_tab_retenciones").hide();
                            $("#li_a_tab_cadenaiva").hide();
                            mensaje("warning", "Seleccione las declaraciones de forma manual !");
                            let target = $('#div_universo_seven');
                            if (target.length) {
                                $('html,body').animate({
                                    scrollTop: target.offset().top
                                }, 1000);
                                return false;
                            }

                            $('html, body').scrollTop($("#div_universo_seven").offset().top);


                        } else {
                            mensaje("warning", "Ninguna declaración esta fuera del año!");

                        }
                        if ((hay_cumplen === 1) && (hay_no_cumplen === 0)) {
                            tablaCumple = document.getElementById("tabla_declaraciones_cumplen");
                            trCumple = tablaCumple.getElementsByTagName("tr");
                            fx_adhesivos(1, trCumple, escena.param4);
                        }
                    });
            } else {
                fun_novedades(egipto);

            }
        });
}

function fx_adhesivos(consultar_adhesivos, trCumple, escenario) {
    if (consultar_adhesivos === 1) {
        los_adhesivos = '';
        for (let i = 0; i < trCumple.length; i++) {
            td_adh = trCumple[i].getElementsByTagName("td")[2];
            if (td_adh) {
                let pre_adh = td_adh.innerHTML
                let adh = ''
                if (typeof pre_adh === 'string') {
                    adh = pre_adh.replace(/ /g, '')
                    adh = adh.replace("-", "_");
                    los_adhesivos = los_adhesivos + ',' + adh
                }
            }
        }
        const ruc = $("#txt_ruc_ingresado").val();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();

        const requesta = {
            param1: ruc,
            param2: periodo1,
            param3: periodo2,
            param4: escenario,
            usuario: $("#csrf_user").val(),
            bonder: los_adhesivos,
            mu: $("#in_xyz").val()
        }

        axios.post(`get_elecciones`, JSON.stringify(requesta), config)
            .then(function (resultado) {
                if (resultado.data.declas) {

                    if (resultado.data.declas.length > 0) {
                        let polinesia = resultado.data.declas;
                        let nuevazelanda = resultado.data.nfilas;
                        $('#tabla_declaraciones_transpuesta tbody').empty();
                        $('#tabla_declaraciones_transpuesta tbody').html('');
                        if (polinesia.length > 0) {
                            $("#div_exportar_cadena_earlier").empty();
                            $("#div_exportar_cadena_earlier").append(resultado.data.enlace_cad_f1);
                            $.each(polinesia, function (i, item) {
                                let descripcion = polinesia[i].fx_1;
                                let tempdesc = descripcion;
                                descripcion = get_descripciones(descripcion);
                                let xinternas = '';
                                let especial1 = 0;
                                let agregarfilasvacias = 0;
                                if (['sct_retenciones_mesanterior', 'sct_adquisicion_mesanterior', 'sct_x_adquisiciones', 'sct_x_retenciones'].includes(tempdesc)) {
                                    especial1 = 1;
                                }
                                if (['total_impuesto_a_pagar_2610'].includes(tempdesc)) {
                                    agregarfilasvacias = 1;
                                }
                                for (let k = 1; k <= nuevazelanda; k++) {
                                    let elementox = 'polinesia[i].fx_' + k;
                                    let elementoy = eval(elementox);
                                    let ancho = ``
                                    if (k == 1) {
                                        elementoy = descripcion;
                                        ancho = ` style="width:25%;" `
                                    }
                                    if ((k == 2) && (['sct_retenciones_mesanterior', 'sct_adquisicion_mesanterior'].includes(tempdesc))) {
                                        especial = 1;
                                        switch (tempdesc) {
                                            case "sct_adquisicion_mesanterior": g_saldo_adq_ma = quitarMoneda(elementoy); break;
                                            case "sct_retenciones_mesanterior": g_saldo_ret_ma = quitarMoneda(elementoy); break;
                                        }

                                        console.log(g_saldo_adq_ma);
                                        console.log(g_saldo_ret_ma);
                                    }
                                    if ((k >= 2) && (['mes_fiscal'].includes(tempdesc))) {
                                        elementoy = mes_short(parseInt(elementoy));

                                    }

                                    if (!['saldo_crt_clo_ipr_msi_2220', 'total_impuesto_a_pagar_2610', 'total_pagado'].includes(tempdesc)) {

                                        xinternas = xinternas + `<td ${ancho}><label class="form-check-label" for="formCheckboxRight1">${elementoy}</label></td>`;
                                    }
                                }

                                let bcolor = 'trColorblanco';
                                if (especial1 === 1) {
                                    bcolor = 'trColorNNN';
                                }

                                $(`<tr class="${bcolor}">`).html(xinternas).appendTo('#tabla_declaraciones_transpuesta tbody');

                                if (agregarfilasvacias === 1) {
                                    $(`<tr class="trColorMetallicSeaweed">`).html(`<td colspan="10"> </td>`).appendTo('#tabla_declaraciones_transpuesta tbody');
                                }

                            });
                        }
                    }
                }
                const body = JSON.stringify(requesta)
                const url = `get_compritas`;
                loading(true);
                axios.post(url, body, config).then(function (compra) {
                    //spinner.removeAttribute('hidden');
                    if (compra.data.df_pagina_exp) {
                        if (compra.data.df_pagina_exp.length > 0) {
                            let argentina = compra.data.df_pagina_exp;
                            let sovietica = compra.data.df_paginado_exp;
                            let rubik = parseInt(compra.data.longitudcompras);
                            let italia = compra.data.df_longitudes_exp;
                            let doble = compra.data.duplicados;
                            let capadocia = compra.data.df_informe_exp;
                            let pompeya = compra.data.df_ingresado_exp;
                            let venecia = compra.data.out_of_range_fe;
                            let num_descartes = compra.data.num_descartes;
                            $("#btn_lista_todo").html(` Todos (${compra.data.longitudcompras}) `)
                            $("#btn_lista_fantasmas").html(` Fantasmas (${italia[3].longitudes}) `)
                            $("#btn_lista_fallecidos").html(` Fallecidos (${italia[4].longitudes}) `)
                            $("#btn_lista_ffpv").html(` No Cruzan (${italia[5].longitudes}) `)
                            $("#btn_lista_cruza").html(` Cruzan (${italia[9].longitudes}) `)
                            $("#li_a_duplicados").html(` <b class="text-success"  > Duplicados (${italia[8].longitudes}) </b> `)
                            $("#p_strong_duplicados").html(` + Duplicados (${italia[8].longitudes}) `)
                            $("#p_strong_excel_load").html(` = Listado Excel (${parseInt(compra.data.longitudcompras) + parseInt(italia[8].longitudes) + parseInt(num_descartes)}) `)
                            $("#li_a_descartados").html(` <b class="text-success"> Descartados (${num_descartes})  </b>   `)
                            let mensaje_de = '';
                            $("#mensaje_descartados").html(`    `);
                            if (parseInt(num_descartes) != parseInt(venecia.length)) {
                                $("#mensaje_descartados").html(` Se muestran unicamente 1000 filas de un total de ${num_descartes} descartados, utilice la descarga para revvisar la totallidad del archivo!  `)
                            }
                            $("#p_strong_descartados").html(` + Descartados (${num_descartes}) `)
                            $("#div_exportar_excel_ir").empty();
                            $("#div_exportar_excel_ir").append(compra.data.enlace_inf_rev);
                            $("#div_exportar_excel_res_period").empty();
                            $("#div_exportar_excel_res_period").append(compra.data.enlace_periodos);
                            $("#div_exportar_descartados").empty();
                            $("#div_exportar_descartados").append(compra.data.enlace_descartes);
                            $("#p_cruce_retenciones").html(" Procesables (" + compra.data.longitudcompras + ")")

                            if (compra.data.df_informe_exp) {
                                if (resultado.data.periodos.length > 0) {
                                    let indonesia = capadocia;
                                    $('#tabla_retenciones_periodo tbody').empty();
                                    $('#tabla_retenciones_periodo tbody').html('');
                                    if (indonesia.length > 0) {
                                        $.each(indonesia, function (i, item) {
                                            var color_back = '#eee6ff';
                                            if (parseInt(item.codigo_impuesto) == 2021) {
                                                color_back = '#6fa8dc ';
                                            }
                                            $(`<tr style="background-color:${color_back}" class="fila">`).html(`
                                                                <td> ${item.anio} </td>
                                                                <td> ${item.mes} </td>
                                                                <td> ${parseFloat(item.retenciones_fuente_iva).toFixed(2)}     </td>                                                
                                                                <td class="col_200px"> <input type="text" class="ctxt_mayores" id="mayor_${item.numero_adhesivo}_${i}" placeholder="Valor" value="${parseFloat(item.retenciones_fuente_iva).toFixed(2)}"> </td>
                                                                <td> ${parseFloat(item.diferencia_actualizar).toFixed(2)} </td>
                                                                <td> ${parseFloat(item.ingresados).toFixed(2)} </td>
                                                                <td> ${parseFloat(item.no_consta_base).toFixed(2)}  </td>
                                                                <td> ${parseFloat(item.nocruzan).toFixed(2)}  </td>
                                                                <td> ${parseFloat(item.negados_dups).toFixed(2)}  </td>                                                                                                                
                                                                <td> ${parseFloat(item.aceptados_cadena).toFixed(2)}  </td>                                                        
                                                                <td> ${parseFloat(item.aceptados_cadena).toFixed(2)}  </td>                                                        
                                                                <td style="display:none;"> ${parseFloat(item.nocruzan).toFixed(2)} </td>
                                                                <td style="display:none;"> ${parseFloat(item.aceptados_cadena).toFixed(2)} </td>
                                                                `
                                            ).appendTo('#tabla_retenciones_periodo tbody');

                                            fx_totalizar("tabla_retenciones_periodo")

                                        });
                                        let parceros = { la_diez: -1, posicion: -1 }

                                        //enlace con la cadena de iva
                                        pre_in_chains(ruc, los_adhesivos, -1, -1, 0, parceros, -1);
                                    }
                                }

                            }

                            /* END */
                            $('#tab_Informe_Revision tbody').empty();
                            $('#tab_Informe_Revision tbody').html('');
                            if (argentina.length > 0) {
                                $.each(argentina, function (i, item) {

                                    $("#li_a_retenciones").html(` <b class="text-success"> Detalle Retenciones (${rubik})  </b>`)

                                    let mes_curso = parseInt(argentina[i].mes);
                                    let anio_curso = parseInt(argentina[i].anio);
                                    let mes_siguiente = 0;
                                    let anio_siguiente = 0;
                                    let unitamas = 0;
                                    if (i < rubik) {
                                        if (argentina[i + 1]) {
                                            mes_siguiente = parseInt(argentina[i + 1].mes);
                                            anio_siguiente = parseInt(argentina[i + 1].anio);
                                        } else {
                                            unitamas = 1;
                                        }
                                    }

                                    let clean = '';
                                    let backg = "trlimon";
                                    if ((argentina[i].es_fantasma === 'si') || (argentina[i].es_fallecido === 'si') || (argentina[i].es_ffpv === 'si') || (argentina[i].cruza === 'no')) {
                                        backg = "trColorRojoBajo";
                                        clean = `class="fila ${backg}"`;
                                    }
                                    $(`<tr   ${clean}>`).html(`
                                                        <td> ${i} </td>
                                                        <td> ${(item.ruc_contrib_informan).toString()} </td>
                                                        <td> ${argentina[i].razon_social} </td>
                                                        <td> ${argentina[i].fecha_emi_retencion} </td>                                                
                                                        <td> ${argentina[i].secuencial_retencion} </td>
                                                        <td> ${(item.autorizacion).toString()} </td>                                                             
                                                        <td> ${argentina[i].valor_retenido_listado} </td>
                                                        <td> ${argentina[i].valor_retenido_administracion} </td>
                                                        <td> ${argentina[i].no_reporta} </td>
                                                        <td> ${argentina[i].es_fantasma} </td>
                                                        <td> ${argentina[i].es_fallecido} </td>
                                                        <td> ${parseInt(item.conteo) > 0 ? (item.conteo).toString() : ''} </td>
                                                        <td> ${argentina[i].cruza} </td>                                                
                                                        <td> ${item.valor_retencion} </td>
               
                                                        `
                                    ).appendTo('#tab_Informe_Revision tbody');

                                    if (((anio_curso === anio_siguiente) && (mes_curso != mes_siguiente)) || (unitamas === 1) || (anio_curso !== anio_siguiente)) {
                                        let valor = 0;

                                        for (var k = 0; k < pompeya.length; k++) {
                                            if (parseInt(argentina[i].mes) === parseInt(pompeya[k].mes) && parseInt(argentina[i].anio) === parseInt(pompeya[k].anio)) {
                                                valor = pompeya[k].ingresados;
                                                break;
                                            }
                                        }
                                        let elnombre = '';
                                        switch (parseInt(argentina[i].mes)) {
                                            case 1: elnombre = 'ENERO'; break;
                                            case 2: elnombre = 'FEBRERO'; break;
                                            case 3: elnombre = 'MARZO'; break;
                                            case 4: elnombre = 'ABRIL'; break;
                                            case 5: elnombre = 'MAYO'; break;
                                            case 6: elnombre = 'JUNIO'; break;
                                            case 7: elnombre = 'JULIO'; break;
                                            case 8: elnombre = 'AGOSTO'; break;
                                            case 9: elnombre = 'SEPTIEMBRE'; break;
                                            case 10: elnombre = 'OCTUBRE'; break;
                                            case 11: elnombre = 'NOVIEMBRE'; break;
                                            case 12: elnombre = 'DICIEMBRE'; break;

                                        }

                                        $('<tr style="background-color:#e0ffff" >').html(`<td colspan="2" align="center">SUBTOTAL VÁLIDO ${elnombre} </td><td> ${valor} </td>
                                            
                                                        `
                                        ).appendTo('#tab_Informe_Revision tbody');

                                    }

                                });


                                if (sovietica.length > 0) {

                                    let texto = ``;
                                    $('#ul_ir').empty()

                                    $.each(sovietica, function (i, item) {
                                        if (item.inicial - 1 !== 0) {
                                            texto = `<li class="page-item" id="${item.inicial - 1}_${item.contri}"><button class="page-link boton_ir" id="${item.inicial - 1}_${item.contri}">Anterior</button></li>`;
                                            $("#ul_ir").append(texto);
                                        }

                                        for (let nz = item.inicial; nz <= item.final; nz++) {
                                            let activo = '';
                                            if (nz == item.actual) {
                                                activo = 'active'
                                            }
                                            texto = `<li class="page-item ${activo}" id="${nz}_${item.contri}">
                                                        <button class="page-link boton_ir" id="${nz}_${item.contri}"> ${nz}</button>
                                                        
                                                        </li>`;
                                            $("#ul_ir").append(texto);
                                        }
                                        if ((item.final + 1 !== item.paginas) || (item.final !== item.paginas)) {
                                            texto = `<li class="page-item" id="${item.final + 1}_${item.contri}"><button class="page-link boton_ir" id="${item.final + 1}_${item.contri}">Siguiente</button></li>`;
                                            $("#ul_ir").append(texto);
                                        }
                                    });

                                }


                            }

                            $('#tab_archivo_duplicados tbody').empty();
                            $('#tab_archivo_duplicados tbody').html('');

                            if (doble) {
                                if (doble.length > 0) {
                                    if (doble.indexOf("Empty DataFrame") < 0) {

                                        $.each(doble, function (fila, item) {

                                            $(`<tr>`).html(`
                                                                <td> ${fila} </td>
                                                                <td> ${item.agente_retencion} </td>
                                                                <td> ${item.fecha_emision} </td>
                                                                <td> ${item.comprobante} </td>
                                                                <td> ${item.autorizacion} </td>
                                                                <td> ${item.valor_retencion} </td>
                                                                <td> </td>                                                
                                                            `
                                            ).appendTo('#tab_archivo_duplicados tbody');

                                        });
                                    }
                                }
                            }

                            $('#tab_archivo_descartados tbody').empty();
                            $('#tab_archivo_descartados tbody').html('');

                            if (venecia) {
                                if (venecia.length > 0) {
                                    if (venecia.indexOf("Empty DataFrame") < 0) {

                                        $.each(venecia, function (fila, item) {
                                            $(`<tr>`).html(`
                                                                <td> ${fila} </td>
                                                                <td> ${item.agente_retencion} </td>
                                                                <td> ${item.fecha_emision} </td>
                                                                <td> ${item.serie} </td>
                                                                <td> ${item.comprobante} </td>
                                                                <td> ${item.autorizacion} </td>
                                                                <td> ${item.porcentaje_iva} </td>
                                                                <td> ${item.valor_retenido} </td>
                                                                <td> ${item.fecha_carga} </td>
                                                                <td> ${item.razon} </td>                                                                
                                                                <td> </td>                                                
                                                            `
                                            ).appendTo('#tab_archivo_descartados tbody');

                                        });
                                    }
                                }
                            }





                        }
                    }
                }).finally(() => {
                    //  spinner.setAttribute('hidden', '');
                    loading(false);
                });;
                $("#div_append_prov").hide()
                $('#texto_providencia').html('');
                $("#li_a_providencia").html(` No Cruzan (0) `);
                $("#li_a_fantasmas").html(` Fantasmas (0) `);
                $("#li_a_fallecidos").html(` Fallecidos (0) `);
                loading(true);
                axios(`get_providencias?ufx=${JSON.stringify(requesta)}`).then(function (compra) {
                    $('#tab_Informe_Revision_no tbody').empty();
                    $('#tab_Informe_Revision_no tbody').html('');
                    $('#tab_archivo_fantasmas tbody').empty();
                    $('#tab_archivo_fantasmas tbody').html('');
                    $('#tab_archivo_fallecidos tbody').empty();
                    $('#tab_archivo_fallecidos tbody').html('');
                    let por_oficio = compra.data.jd_providencias;
                    let por_fantasma = compra.data.jd_fantasma;
                    let por_fallecido = compra.data.jd_fallecido;
                    if (por_oficio.length > 0) {
                        $("#li_a_providencia").html(` No Cruzan (${compra.data.longitud_real}) `)
                        $("#div_exportar_excel_prov_ir").empty();
                        $("#div_exportar_excel_prov_ir").append(compra.data.enlace);

                        if (parseInt(compra.data.longitud_real) !== parseInt(compra.data.longitud_prov)) {
                            $("#div_append_prov").show()
                            $('#texto_providencia').empty();
                            $('#texto_providencia').html(` Se muestran menos providencias debido a la excesiva cantidad de providencias ${compra.data.longitud_real} de un excel de ${compra.data.longitud_excel} filas, 
                                                revise su listado excel, para analisis completo descargue  en excel todas las providencias! `);



                            if (parseInt(compra.data.longitud_fisicas) == 0) {
                                $('#texto_providencia').empty();
                                $('#texto_providencia').html(` Se muestran menos providencias ${compra.data.longitud_prov} debido a la excesiva cantidad de providencias (${compra.data.longitud_real}) 
                                                                respecto al excel cargado  ( ${compra.data.longitud_excel} ) , 
                                                                revise su listado! Para analisis completo descargue  en excel todas las providencias!
                                                                No existen retenciones fisicas, utilice el sistema de descarga de archivo de excel, se muestran las primeras mil filas `);
                            }


                        }

                        //0	                1	                2	                        3	                4	                    5	                    6	                7	                    8	                9	        10	     11	 12	        13
                        //contri	ruc_contrib_informan	numero_ruc_emisor_pintar	fecha_emi_retencion	fecha_emision_pintar	autorizacion	numero_autorizacion_pintar	secuencial_retencion	secuencial_pintar	valor_retencion	anio	mes	ffpv	documento

                        $.each(por_oficio, function (i, item) {
                            let propiedad_lectura = '';
                            let emisor = `<td>${(item.c1).toString()}</td>`;
                            let fecha = `<td>${(item.c3).toString()}</td>`;
                            let autto = `<td> ${(item.c5).toString()}</td>`;
                            let secuencial = `<td>${(item.c7).toString()}</td>`;
                            let ffpv = `<td>${(item.c12).toString()}</td>`;
                            let documento = `<td>${(item.c15).toString()}</td>`;
                            if (item.c5.length > 20) {
                                propiedad_lectura = 'readonly disabled'
                            }
                            if (item.c2 == 0) {
                                emisor = `<td style="background-color:#FE8166"> ${(item.c1).toString()} </td>`;
                            }
                            if (item.c4 == 0) {
                                fecha = `<td style="background-color:#FE8166"> ${(item.c3).toString()} </td>`;
                            }
                            if (item.c6 == 0) {
                                autto = `<td style="background-color:#FE8166"> ${(item.c5).toString()} </td>`;
                            }
                            if (item.c8 == 0) {
                                secuencial = `<td style="background-color:#FE8166"> ${(item.c7).toString()} </td>`;
                            }
                            if (item.c12 == 'si') {
                                ffpv = `<td style="background-color:#FE8166"> ${(item.c12).toString()} </td>`;
                            }
                            if ((item.c15 !== "RETENCION") && (item.c15.length > 0)) {
                                documento = `<td style="background-color:#FE8166"> ${(item.c15).toString()} </td>`;
                            }
                            $(`<tr>`).html(`
                                            <td> ${i} </td>
                                            <td> ${item.c10}</td>
                                            <td> ${item.c11}</td>
                                            ${emisor}                                                 
                                            ${fecha} 
                                            ${secuencial} 
                                            ${autto} 
                                            ${documento} 
                                            ${ffpv} 
                                            <td> ${item.c9} </td>
                                            <td style="width:50px"><input type="text" class="ctxt_retenido" id="txt_val_retenido_${i}"  ${propiedad_lectura} placeholder="Valor"  value="0"> </td>
                                            <td style="display:none;">${item.c13}</td>
                                            <td style="display:none;">${item.c14}</td>
                                        `
                            ).appendTo('#tab_Informe_Revision_no tbody');
                        });
                        loading(false);
                    }



                    if (por_fantasma.length > 0) {
                        $("#li_a_fantasmas").html(` Fantasmas (${compra.data.longitud_fan}) `)
                        $.each(por_fantasma, function (i, item) {

                            //ruc_contrib_informan, razon_social, to_char(fecha_emi_retencion,'yyyy-mm-dd')::varchar  fecha_emision, secuencial_retencion, autorizacion, valor_retencion                         
                            $(`<tr>`).html(`
                                        <td> ${i} </td>
                                        <td> ${item.c0} </td>
                                        <td> ${item.c1} </td>
                                        <td> ${item.c2}     </td>                                                
                                        <td> ${item.c3} </td>
                                        <td> ${item.c4} </td>
                                        <td> ${item.c5} </td>
                                        <td> __ </td>`
                            ).appendTo('#tab_archivo_fantasmas tbody');

                        });
                    }


                    if (por_fallecido.length > 0) {
                        $("#li_a_fallecidos").html(` Fallecidos (${compra.data.longitud_fall}) `)
                        $.each(por_fallecido, function (i, item) {

                            $(`<tr>`).html(`
                                        <td> ${i} </td>
                                        <td> ${item.c0} </td>
                                        <td> ${item.c1} </td>
                                        <td> ${item.c2}     </td>                                                
                                        <td> ${item.c3} </td>
                                        <td> ${item.c4} </td>
                                        <td> ${item.c5} </td>
                                        <td> __ </td>`
                            ).appendTo('#tab_archivo_fallecidos tbody');

                        });
                    }
                });

            });

    }
}

let waiting = document.querySelector("#waiting");
let loadAnim = document.querySelector("#waitanim");

function loading(fire) {
    if (fire) {
        waiting.classList.add("loading");
        loadAnim.classList.add("animation");
    } else {
        waiting.classList.remove("loading");
        loadAnim.classList.remove("animation");
    }
}

function get_descripciones(descripcion_iva) {
    let descripcion = descripcion_iva;
    switch (descripcion_iva) {
        case 'anio': descripcion = 'AÑO FISCAL'; break;
        case 'mes': descripcion = 'MES FISCAL'; break;
        case 'camino': descripcion = 'CAMINO'; break;

        case 'diferencia_arr_ct': descripcion = 'DIFERENCIA ARRASTRE CREDITO TRIBUTARIO'; break;
        case 'diferencia_x_ct': descripcion = 'DIFERENCIA POR CREDITO TRIBUTARIO'; break;
        case 'diferencia_adquisiciones': descripcion = 'DIFERENCIA_ADQUISICIONES'; break;
        case 'diferencia_retenciones': descripcion = 'DIFERENCIA_RETENCIONES'; break;
        case 'totales': descripcion = 'TOTALES'; break;
        case 'codigo_impuesto': descripcion = 'CODIGO_IMPUESTO'; break;
        case 'calculo_ct_adq': descripcion = 'CALCULO_CT_ADQ'; break;
        case 'calculo_ct_ret': descripcion = 'CALCULO_CT_RET'; break;

        case 'valor_retencion_valida': descripcion = 'RETENCIONES EN LA FUENTE DE IVA QUE LE HAN SIDO EFECTUADAS'; break;
        case 'ct_adq_proximo_mes': descripcion = 'SALDO CREDITO TRIBUTARIO X ADQUISICIONES PROXIMO MES'; break;
        case 'ct_ret_proximo_mes': descripcion = 'SALDO CREDITO TRIBUTARIO X RETENCIONES PROXIMO MES'; break;
        case 'total_impuesto_a_pagar': descripcion = 'TOTAL IMPUESTO A PAGAR'; break;
        case 'retenciones_a_devolver': descripcion = 'RETENCIONES DE IVA A DEVOLVER'; break;
        case 'sct_retenciones_mesanterior': descripcion = 'SALDO CREDITO TRIBUTARIO POR RETENCIONES MES ANTERIOR'; break;
        case 'sct_adquisicion_mesanterior': descripcion = 'SALDO CREDITO TRIBUTARIO POR ADQUISICIONES MES ANTERIOR'; break;
        case 'anio_fiscal': descripcion = 'AÑO FISCAL'; break;
        case 'mes_fiscal': descripcion = 'MES FISCAL'; break;
        case 'numero_adhesivo': descripcion = 'NUMERO ADHESIVO'; break;
        case 'fecha_recepcion': descripcion = 'FECHA RECEPCIÓN'; break;
        case 'sustitutiva_original': descripcion = 'TIPO DE DECLARACIÓN'; break;
        case 'sct_credito_mes_anterior_rca_adq_ret': descripcion = 'SALDO CREDITO TRIBUTARIO POR RETENCIONES y ADQUISICIONES'; break;
        case 'saldo_de_ct_mes_anterior': descripcion = 'SALDO CREDITO TRIBUTARIO MES ANTERIOR RESULTANTE DE LA CADENA ANALIZADA POR ADQUISICIONES Y RETENCIONES'; break;
        case 'saldo_crt_rfu_man_2170': descripcion = 'SALDO CREDITO TRIBUTARIO POR RETENCIONES EN LA FUENTE DE IVA MES ANTERIOR'; break;
        case 'ajuste_x_adquisiciones': descripcion = 'AJUSTE POR IVA DEVUELTO POR ADQUISICIONES'; break;
        case 'ajuste_x_retenciones': descripcion = 'AJUSTE POR IVA DEVUELTO POR RETENCIONES'; break;
        case 'sct_mes_anterior': descripcion = 'SALDO CREDITO TRIBUTARIO POR ADQUISICIONES MES ANTERIOR'; break;
        case 'sct_mesanterior_retenciones': descripcion = 'SALDO CREDITO TRIBUTARIO POR RETENCIONES MES ANTERIOR'; break;
        case 'total_impuestos_mes_actual': descripcion = 'TOTAL IMPUESTO VENTAS A LIQUIDAR MES ACTUAL'; break;
        case 'ct_factor_proporcionalidad': descripcion = 'CREDITO TRIBUTARIO APLICABLE EN ESTE PERIODO (FACTOR DE PROPORCIONALIDAD)'; break;
        case 'impuesto_causado': descripcion = 'IMPUESTO CAUSADO'; break;
        case 'ct_mes_actual': descripcion = 'CREDITO TRIBUTARIO MES ACTUAL'; break;
        case 'retenciones_fuente_iva': descripcion = '(-) RETENCIONES EN LA FUENTE DE IVA QUE LE HAN SIDO EFECTUADAS'; break;
        case 'sct_x_adquisiciones': descripcion = 'SALDO CREDITO TRIBUTARIO POR ADQUISICIONES MES SIGUIENTE'; break;
        case 'sct_x_retenciones': descripcion = 'SALDO CREDITO TRIBUTARIO POR RETENCIONES MES SIGUIENTE'; break;
        case 'tot_impuesto_pagar_x_percepcion': descripcion = 'TOTAL IMPUESTO A PAGAR POR PERCEPCION'; break;
        case 'saldo_crt_clo_ipr_msi_2220': descripcion = 'TOTAL IVA RETENIDO'; break;
        case 'total_impuesto_a_pagar_2610': descripcion = 'IMPUESTO A PAGAR'; break;
        case 'total_pagado': descripcion = 'TOTAL PAGADO'; break;
        case 'compensa_futuro_reco_sol_atendida': descripcion = 'COMPENSACION A FUTURO RECONOCIDA EN RESOLUCIONES ATENDIDAS'; break;
        case 'saldo_cred_resulta_next_mes': descripcion = 'SALDO CREDITO RESULTANTE PROXIMO MES '; break;
        case 'impuesto_pagar_resulta_mes': descripcion = 'IMPUESTO A PAGAR RESULTANTE EN EL MES'; break;
    }
    return descripcion
}

function pre_in_chains(ruc, los_adhesivos, adq, ret, grabar, parceros, flo_in) {
    //totales

    let valor_b = parseInt(parceros.posicion)
    valor_b = valor_b > 0 ? valor_b + 2 : -1;

    let listallevar = []
    let lista_totalizado = []
    let lista_a_m = []
    let tabla_columna_foot = document.getElementById("tabla_retenciones_periodo");
    if (tabla_columna_foot) {
        let tab_filasB = tabla_columna_foot.getElementsByTagName("tr");
        let longitudfilasB = tab_filasB.length;
        if (longitudfilasB >= 4) {

            if (tab_filasB[longitudfilasB - 1]) {
                let longitud_columnas = tab_filasB[3].getElementsByTagName("td").length
                let longitud_columnas13 = tab_filasB[longitudfilasB - 1].getElementsByTagName("td").length

                for (let k = 1; k < longitudfilasB; k++) {
                    let aaaa_ = (tab_filasB[k].getElementsByTagName("td")[0])
                    let mm_ = (tab_filasB[k].getElementsByTagName("td")[1])
                    let aaaa = '';
                    let mm = '';
                    let nn = '';
                    if (aaaa_ && mm_) {
                        aaaa = aaaa_.innerText;
                        mm = mm_.innerText;
                        nn = aaaa.toString().trim().padStart(4, '0') + mm.toString().trim().padStart(2, '0');
                    }
                    if (nn.length > 0) {
                        lista_a_m.push(nn)
                    }
                }
                for (let k = 1; k < longitud_columnas13; k++) {
                    let controlcero = (tab_filasB[longitudfilasB - 1].getElementsByTagName("td")[k]).innerText

                    if (controlcero.trim() === '') {
                        controlcero = '0.00'
                    }
                    lista_totalizado.push(controlcero)

                }
                for (let m = 2; m < tab_filasB.length - 1; m++) {
                    let controlcero = (tab_filasB[m].getElementsByTagName("td")[10]).innerText;
                    if (controlcero.trim() === '') {
                        controlcero = '0.00'
                    }
                    if (m == valor_b) {
                        listallevar.push(parceros.la_diez);
                    } else {
                        listallevar.push(controlcero.trim())
                    }
                }
            }
        }
    }


    const periodo1 = $("#txt_desde").val();
    const periodo2 = $("#txt_hasta").val();
    const tparam1 = $("#txt_ruc_ingresado").val();
    const requesta = {
        param1: tparam1,
        param2: periodo1,
        param3: periodo2,
        param4: 'F',
        param5: ($("#span_tramite").html()).trim(),
        bonder: los_adhesivos,
        adquisiciones: adq,
        retenciones: ret,
        grab: grabar,
        ufo: listallevar,
        ufa: lista_totalizado,
        ufx: lista_a_m,
        adq_ingre: flo_in,
        usuario: $("#csrf_user").val(),
        mu: $("#in_xyz").val()
    }

    axios.post(`get_pre_chain_norm`, JSON.stringify(requesta), config)
        .then(function (resultado) {
            if (resultado.data.declas) {

                if (resultado.data.declas.length > 0) {
                    let polinesia = resultado.data.declas;
                    let nuevazelanda = resultado.data.nfilas;
                    let salvando = resultado.data.historia;
                    let supervision = resultado.data.supervisores;
                    $("#p_strong_calculado_en").empty()
                    $("#p_strong_calculado_en").html("Calculado en: " + resultado.data.atendido_en)
                    $('#tab_cadena_iva_transpuesta tbody').empty();
                    $('#tab_cadena_iva_transpuesta tbody').html('');
                    if (polinesia.length > 0) {
                        $.each(polinesia, function (i, item) {
                            let descripcion = polinesia[i].fx_1;
                            let tempdesc = descripcion;
                            descripcion = get_descripciones(descripcion);
                            $("#div_exportar_excel_cad_warp_ir").empty();
                            $("#div_exportar_excel_cad_warp_ir").append(resultado.data.enlace);
                            $("#div_exportar_excel_cad_warp_valids").empty();
                            $("#div_exportar_excel_cad_warp_valids").append(resultado.data.enlace_infos);
                            if (salvando.length > 0) {
                                $.each(salvando, function (i, item) {
                                    $("#p_graba_nombre_contri").empty();
                                    $("#p_graba_nombre_contri").html(item.razon_social);
                                    $("#spa_graba_ruc").empty();
                                    $("#spa_graba_ruc").html(item.contri);
                                    $("#p_graba_fecha_ingreso").empty();
                                    $("#p_graba_fecha_ingreso").html(item.fecha_ingreso);
                                    $("#b_graba_tramite").empty();
                                    $("#b_graba_tramite").html(item.tramite);
                                    $("#spa_graba_desde").empty();
                                    $("#spa_graba_desde").html(item.periodo_inicial);
                                    $("#spa_graba_hasta").empty();
                                    $("#spa_graba_hasta").html(item.periodo_final);
                                    $("#spa_graba_solicitado").empty();
                                    $("#spa_graba_solicitado").html(USDollar.format(item.monto_solicitado));
                                });
                                $("#div_supervisores").html('');
                                let texto = '';
                                if (supervision.length == 0) {
                                    $("#div_supervisores_boton").hide();
                                    texto += `<li> <div class="alert alert-danger alert-dismissible alert-label-icon rounded-label fade show" role="alert">
                                                <i class="ri-airplay-line label-icon"></i><strong>No existen supervisores, solicitelos a su jefatura inmediata!</strong> 
                                              </div>
                                         </li>`;

                                } else {
                                    texto += `<li><p>Listado de Supervisores<p></li>`
                                    $.each(supervision, function (i, item) {
                                        texto += `<li> <div class="alert alert-info alert-dismissible alert-label-icon rounded-label fade show" role="alert">
                                                    <i class="ri-airplay-line label-icon"></i><strong>${i} - ${item.nombre}</strong> 
                                                  </div>
                                             </li>`

                                    });

                                    $("#div_supervisores_boton").show();
                                }
                                let lista = $("#div_supervisores").append('<ul></ul>').find('ul');
                                lista.append(texto);
                            }
                            let xinternas = '';
                            let especial1 = 0;
                            if (['sct_retenciones_mesanterior', 'sct_adquisicion_mesanterior', 'sct_x_adquisiciones', 'sct_x_retenciones'].includes(tempdesc)) {
                                especial1 = 1;
                            }
                            for (let k = 1; k <= nuevazelanda; k++) {
                                let elementox = 'polinesia[i].fx_' + k;
                                let elementoy = eval(elementox);
                                if (k == 1) {
                                    elementoy = descripcion;
                                }
                                let especial = 0;
                                if ((k == 2) && (['sct_retenciones_mesanterior', 'sct_adquisicion_mesanterior'].includes(tempdesc))) {
                                    especial = 1;
                                }
                                if ((k >= 2) && (['mes'].includes(tempdesc))) {
                                    elementoy = parseInt(elementoy);
                                }
                                if (especial === 0) {
                                    if (!['tot_impuesto_pagar_x_percepcion', 'calculo_ct_adq', 'calculo_ct_ret', 'diferencia_arr_ct', 'diferencia_x_ct', 'diferencia_adquisiciones', 'diferencia_retenciones', 'ajuste_x_adquisiciones', 'ajuste_x_retenciones', 'sct_x_adquisiciones', 'sct_x_retenciones'].includes(tempdesc)) {
                                        if (k == 1) {
                                            xinternas = xinternas + `<td style="width:28%"><label class="form-check-label" for="formCheckboxRight1">${elementoy}</label></td>`;
                                        } else {
                                            xinternas = xinternas + `<td><label class="form-check-label " for="formCheckboxRight1">${isNumeric(elementoy) && i > 3 ? parseFloat(elementoy).toFixed(2) : elementoy}</label></td>`;
                                        }
                                    }
                                } else {
                                    switch (tempdesc) {
                                        case 'sct_adquisicion_mesanterior': xinternas = xinternas + `<td><input type="text" class="ctxt_diferencias_adq" id="txt_iva_${tempdesc}" placeholder="Valor" value='${elementoy}'></input>`;
                                            break;
                                        case 'sct_retenciones_mesanterior': xinternas = xinternas + `<td><input type="text" class="ctxt_diferencias_ret" id="txt_iva_${tempdesc}" placeholder="Valor" value='${elementoy}'></input>`;
                                            break;
                                    }
                                }
                            }
                            let bcolor = 'trColorblanco';
                            if (especial1 === 1) {
                                bcolor = 'trColorNNN';
                            }
                            $(`<tr class="${bcolor}">`).html(xinternas).appendTo('#tab_cadena_iva_transpuesta tbody');

                        });
                    }
                    if (cerrar_ta === 0) {
                        $('.ctxt_diferencias_adq').attr('disabled', 'disabled');
                    }
                    if (cerrar_tb === 0) {
                        $('.ctxt_diferencias_ret').attr('disabled', 'disabled');
                    }
                }
                let sumaValores_arrastre = 0.0;
                let sumaValores_cuerdo_analisis = 0.0;
                let sumaValores_darse_baja = 0.0;
                if (parseInt(grabar) === 1) {
                    if (resultado.data.resumen1.length > 0) {
                        let suiza = resultado.data.resumen1;
                        $('#tab_resumen_periodos tbody').empty();
                        $('#tab_resumen_periodos tbody').html('');
                        if (suiza.length > 0) {
                            $.each(suiza, function (i, item) {
                                texto_anio = suiza[i].anio
                                if (parseInt(texto_anio) === 0) {
                                    texto_anio = 'TOTAL'
                                }
                                $('<tr>').html(`<td> ${texto_anio} </td>
                                                <td><h6 class="mb-sm-0"> ${mes_short(parseInt(suiza[i].mes))}  </h6pan></td>
                                                <td><h6 class="mb-sm-0"> ${USDollar.format(suiza[i].total_impuesto_a_pagar)}  </h6></td>
                                                <td><h6 class="mb-sm-0"> ${USDollar.format(suiza[i].retenciones_a_devolver)}  </h6></td>
                                                <td><h6 class="mb-sm-0"> ${USDollar.format(suiza[i].saldos)} </h6></td>                                                
                                            `
                                ).appendTo('#tab_resumen_periodos tbody');
                            });
                        }
                    }
                    if (resultado.data.resumen2.length > 0) {
                        let mexico = resultado.data.resumen2;
                        $('#tab_liquidacion tbody').empty();
                        $('#tab_liquidacion tbody').html('');
                        if (mexico.length > 0) {
                            $.each(mexico, function (i, item) {
                                if ([7, 8].includes(i)) {
                                    sumaValores_arrastre += parseFloat(mexico[i].valor);
                                    console.log(sumaValores_arrastre)
                                }
                                $('<tr>').html(`
                                                <td style="width:60%"><span class="d-none d-xl-block ms-1 fs-12 text-muted user-name-sub-text"> ${mexico[i].detalle}  </span></td>
                                                <td style="width:40%"><h6 class="mb-sm-0" id="h6_liq_${i}" name="h6_liq_${i}" > ${USDollar.format(mexico[i].valor)}  </h6></td>
                                            `
                                ).appendTo('#tab_liquidacion tbody');
                            });
                        }
                    }

                    if (resultado.data.resumen3.length > 0) {
                        let elsalvador = resultado.data.resumen3;
                        $('#tab_resumen_valores tbody').empty();
                        $('#tab_resumen_valores tbody').html('');
                        if (elsalvador.length > 0) {
                            $.each(elsalvador, function (i, item) {
                                if ([5, 6].includes(i)) {
                                    sumaValores_cuerdo_analisis += parseFloat(elsalvador[i].valor);
                                }

                                if ([0, 1, 2, 3, 4, 7, 8].includes(i)) {
                                    sumaValores_darse_baja += parseFloat(elsalvador[i].valor);
                                }


                                $('<tr>').html(`
                                                <td style="width:60%"><span class="d-none d-xl-block ms-1 fs-12 text-muted user-name-sub-text"> ${elsalvador[i].detalle}  </span></td>
                                                <td style="width:40%"><h6 class="mb-sm-0"> ${elsalvador[i].valor}  </h6></td>
                                            `
                                ).appendTo('#tab_resumen_valores tbody');
                            });
                        }
                    }

                    $('#txt_de_baja').val('');
                    $('#txt_de_baja').val(sumaValores_darse_baja);


                    if (resultado.data.resumen3_5.length > 0) {
                        let honduras = resultado.data.resumen3_5;
                        $('#tab_verifica_resultados tbody').empty();
                        $('#tab_verifica_resultados tbody').html('');
                        if (honduras.length > 0) {
                            $.each(honduras, function (i, item) {

                                let l1 = (USDollar.format(honduras[i].valor1)).toString().trim() === "$NaN" ? 'OK' : USDollar.format(honduras[i].valor1);
                                let l2 = honduras[i].valor2;

                                $('<tr>').html(`
                                                <td style="width:40%;"><span class="d-none d-xl-block ms-1 fs-12 text-muted user-name-sub-text""> ${honduras[i].detalle}  </span></td>
                                                <td style="width:30%"><h6 class="mb-sm-0"> ${l1}  </h6></td>
                                                <td style="width:30%"><h6 class="mb-sm-0"> ${l2}  </h6></td>
                                            `
                                ).appendTo('#tab_verifica_resultados tbody');
                            });
                        }
                    }

                    if (resultado.data.resumen4.length > 0) {
                        let costarica = resultado.data.resumen4;
                        $('#tab_creditos_tributario tbody').empty();
                        $('#tab_creditos_tributario tbody').html('');

                        //total_impuesto_a_pagar, retenciones_a_devolver
                        if (costarica.length > 0) {
                            $.each(costarica, function (i, item) {

                                let l1 = (USDollar.format(costarica[i].valor1)).toString().trim() === "$NaN" ? 'OK' : USDollar.format(costarica[i].valor1);
                                let l2 = (USDollar.format(costarica[i].valor2)).toString().trim() === "$NaN" ? 'OK' : USDollar.format(costarica[i].valor2);


                                $('<tr>').html(`
                                                <td  style="width:40%"><span class="d-none d-xl-block ms-1 fs-12 text-muted user-name-sub-text"> ${costarica[i].detalle}  </span></td>
                                                <td style="width:30%"><h6 class="mb-sm-0"> ${l1}  </h6></td>
                                                <td style="width:30%"><h6 class="mb-sm-0"> ${l2}  </h6></td>    
                                                <td></td>
                                                <td></td>                                                
                                            `
                                ).appendTo('#tab_creditos_tributario tbody');
                            });
                        }
                    }


                    $('#ul_fox a[href="#resumen_periodos"]').tab('show')
                    compensar_futuro_pasado(sumaValores_arrastre, sumaValores_cuerdo_analisis, 0, 10);
                    mensaje("success", `Revise los resumenes, se ha grabado correctamente los resultados! `);
                }
            }
        });
}

$(document).ready(function () {
    function filtrado2(tabla, filtro, columna) {
        var input, filter, table, tr, td, i, txtValue;
        var filter = filtro.toUpperCase();
        var table = document.getElementById(tabla);
        var tr = table.getElementsByTagName("tr");
        for (i = 1; i < tr.length; i++) {
            var td = tr[i].getElementsByTagName("td")[columna];
            if (td) {
                var txtValue = td.textContent || td.innerText;
                if (filter != '-1') {
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                } else {
                    if (parseInt(txtValue) > 0) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            } else {
                tr[i].style.display = "none";

            }
        }
    }

    function filtrado(tabla, filtro, columna) {
        var input, filter, table, tr, td, i, txtValue;
        var table = document.getElementById(tabla);
        var tr = table.getElementsByTagName("tr");

        for (var i = 1; i < tr.length; i++) {
            var td = tr[i].getElementsByTagName("td")[columna];
            var td1 = tr[i].getElementsByTagName("td")[1];

            if (td && td1) {
                if (filtro != "todo") {
                    let txtValue = td.textContent || td.innerText;

                    if (txtValue.trim() == filtro) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                } else {
                    tr[i].style.display = "";
                }
            }
        }
    }

    $("#btn_lista_fantasmas").click(function () {
        filtrado2("tab_Informe_Revision", "SI", 9)
    });

    $("#btn_lista_fallecidos").click(function () {
        filtrado2("tab_Informe_Revision", "SI", 10)
    });

    $("#btn_lista_ffpv").click(function () {
        filtrado2("tab_Informe_Revision", "", 12)
    });

    $("#btn_lista_cruza").click(function () {
        filtrado2("tab_Informe_Revision", "SI", 12)
    });

    $("#btn_lista_dups").click(function () {
        filtrado2("tab_Informe_Revision", "-1", 11)
    });

    $("#btn_lista_todo").click(function () {
        filtrado("tab_Informe_Revision", "todo", 1)
    });

    $("#nav_ir").on('click', 'li', function () {
        let partes = $(this).attr('id').split("_");
        const tramite = ($("#span_tramite").html()).trim() == '' ? 'PENDIENTE' : ($("#span_tramite").html()).trim();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();
        const usx = $("#csrf_user").val();
        const mu = $("#in_xyz").val();
        const url = `get_paginado_ir/${partes[0]}/${partes[1]}/${periodo1}/${periodo2}/${tramite}/${usx}/${mu}`;
        axios(url).then(function (compra) {
            if (parseInt(compra.data.valida) == -100) {
                window.location = "/account/login";
            }
            else {
                if (compra.data.df_pagina_exp) {
                    if (compra.data.df_pagina_exp.length > 0) {
                        let argentina = compra.data.df_pagina_exp;
                        let sovietica = compra.data.df_paginado_exp;
                        let rubik = 100;
                        let pompeya = compra.data.df_ingresado_exp;

                        $('#tab_Informe_Revision tbody').empty();
                        $('#tab_Informe_Revision tbody').html('');
                        if (argentina.length > 0) {
                            $.each(argentina, function (i, item) {
                                let mes_curso = parseInt(argentina[i].mes);
                                let anio_curso = parseInt(argentina[i].anio);
                                let mes_siguiente = 0;
                                let anio_siguiente = 0;
                                let unitamas = 0;
                                if (i < rubik) {
                                    if (argentina[i + 1]) {
                                        mes_siguiente = parseInt(argentina[i + 1].mes);
                                        anio_siguiente = parseInt(argentina[i + 1].anio);
                                    } else {
                                        unitamas = 1;
                                    }
                                }

                                let clean = '';
                                let backg = "trlimon";
                                if ((argentina[i].es_fantasma === 'si') || (argentina[i].es_fallecido === 'si') || (argentina[i].es_ffpv === 'si') || (argentina[i].cruza === 'no')) {
                                    backg = "trColorRojoBajo";
                                    clean = `class="fila ${backg}"`;
                                }
                                $(`<tr   ${clean}>`).html(`
                                                    <td> ${i} </td>
                                                    <td> ${(item.ruc_contrib_informan).toString()} </td>
                                                    <td> ${argentina[i].razon_social} </td>
                                                    <td> ${argentina[i].fecha_emi_retencion} </td>                                                
                                                    <td> ${argentina[i].secuencial_retencion} </td>
                                                    <td> ${(item.autorizacion).toString()} </td>                                                             
                                                    <td> ${argentina[i].valor_retenido_listado} </td>
                                                    <td> ${argentina[i].valor_retenido_administracion} </td>
                                                    <td> ${argentina[i].no_reporta} </td>
                                                    <td> ${argentina[i].es_fantasma} </td>
                                                    <td> ${argentina[i].es_fallecido} </td>
                                                    <td> ${parseInt(item.conteo) > 0 ? (item.conteo).toString() : ''} </td>
                                                    <td> ${argentina[i].cruza} </td>                                                
                                                    <td> ${item.valor_retencion} </td>
            
                                                    `
                                ).appendTo('#tab_Informe_Revision tbody');

                                if (((anio_curso === anio_siguiente) && (mes_curso != mes_siguiente)) || (unitamas === 1) || (anio_curso !== anio_siguiente)) {
                                    let valor = 0;

                                    for (var k = 0; k < pompeya.length; k++) {
                                        if (parseInt(argentina[i].mes) === parseInt(pompeya[k].mes) && parseInt(argentina[i].anio) === parseInt(pompeya[k].anio)) {
                                            valor = pompeya[k].ingresados;
                                            break;
                                        }
                                    }
                                    let elnombre = '';
                                    switch (parseInt(argentina[i].mes)) {
                                        case 1: elnombre = 'ENERO'; break;
                                        case 2: elnombre = 'FEBRERO'; break;
                                        case 3: elnombre = 'MARZO'; break;
                                        case 4: elnombre = 'ABRIL'; break;
                                        case 5: elnombre = 'MAYO'; break;
                                        case 6: elnombre = 'JUNIO'; break;
                                        case 7: elnombre = 'JULIO'; break;
                                        case 8: elnombre = 'AGOSTO'; break;
                                        case 9: elnombre = 'SEPTIEMBRE'; break;
                                        case 10: elnombre = 'OCTUBRE'; break;
                                        case 11: elnombre = 'NOVIEMBRE'; break;
                                        case 12: elnombre = 'DICIEMBRE'; break;
                                    }
                                    $('<tr style="background-color:#e0ffff" >').html(`<td colspan="2" align="center"> ${anio_curso} SUBTOTAL VÁLIDO ${elnombre} </td><td> ${valor} </td>
                                        
                                                    `
                                    ).appendTo('#tab_Informe_Revision tbody');

                                }

                            });

                            if (sovietica.length > 0) {

                                let texto = ``;
                                $('#ul_ir').empty()

                                $.each(sovietica, function (i, item) {
                                    if (item.inicial - 1 !== 0) {
                                        texto = `<li class="page-item" id="${item.inicial - 1}_${item.contri}"><button class="page-link boton_ir" id="${item.inicial - 1}_${item.contri}">Anterior</button></li>`;
                                        $("#ul_ir").append(texto);
                                    }

                                    for (let nz = item.inicial; nz <= item.final; nz++) {
                                        let activo = '';
                                        if (nz == item.actual) {
                                            activo = 'active'
                                        }
                                        texto = `<li class="page-item ${activo}" id="${nz}_${item.contri}">
                                                        <button class="page-link boton_ir" id="${nz}_${item.contri}"> ${nz}</button>
                                                    </li>`;
                                        $("#ul_ir").append(texto);
                                    }
                                    if ((item.final + 1 !== item.paginas) || (item.final !== item.num_paginas)) {
                                        texto = `<li class="page-item" id="${item.final + 1}_${item.contri}"><button class="page-link boton_ir" id="${item.final + 1}_${item.contri}">Siguiente</button></li>`;
                                        $("#ul_ir").append(texto);
                                    }
                                });

                            }



                        }

                    }


                }
            }
        });
    });



    $("#btn_guardar_providencia").click(function () {
        var tablaRevision = document.getElementById("tab_Informe_Revision_no");
        var trRevision = tablaRevision.getElementsByTagName("tr");

        for (var k = 0; k < trRevision.length; k++) {
            let limite_aceptacion_ = trRevision[k].getElementsByTagName("td")[9];
            let aceptados_pre_ = trRevision[k].getElementsByTagName("td")[10];
            if (limite_aceptacion_) {
                const limite_aceptacion = parseFloat(limite_aceptacion_.innerText).toFixed(2);
                const aceptados_pre = parseFloat(aceptados_pre_.getElementsByTagName("input")[0].value).toFixed(2)

                if (parseFloat(aceptados_pre) > parseFloat(limite_aceptacion)) {
                    mensaje("success", `   El valor ingresado  ${aceptados_pre}  es mayor al permitido ${limite_aceptacion}, realice el ajuste! `)
                    aceptados_pre_.getElementsByTagName("input")[0].value = 0

                    return
                }
            }
        }
        var tablaResumen4 = document.getElementById("tabla_retenciones_periodo");
        var trResumen4 = tablaResumen4.getElementsByTagName("tr");


        for (k = 0; k < trResumen4.length; k++) {
            numeroDocumento4 = trResumen4[k].getElementsByTagName("td")[11];
            if (numeroDocumento4) {
                trResumen4[k].getElementsByTagName("td")[7].innerHTML = trResumen4[k].getElementsByTagName("td")[11].innerHTML;
                trResumen4[k].getElementsByTagName("td")[9].innerHTML = trResumen4[k].getElementsByTagName("td")[12].innerHTML;
                trResumen4[k].getElementsByTagName("td")[10].innerHTML = trResumen4[k].getElementsByTagName("td")[12].innerHTML;
                //trResumen4[k].getElementsByTagName("td")[12].innerHTML  = trResumen4[k].getElementsByTagName("td")[12].innerHTML;
            }
        }
        const ruc = $("#txt_ruc_ingresado").val();
        const desde = $("#txt_desde").val();
        const hasta = $("#txt_hasta").val();
        for (var i = 0; i < trRevision.length; i++) {
            let numeroDocumento = trRevision[i].getElementsByTagName("td")[4];
            let anio_ = trRevision[i].getElementsByTagName("td")[1];
            let mes_ = trRevision[i].getElementsByTagName("td")[2];
            let valor_nuevo_ = trRevision[i].getElementsByTagName("td")[10];

            let frecuencia_ = trRevision[i].getElementsByTagName("td")[11];
            let cod_impuesto_ = trRevision[i].getElementsByTagName("td")[12];

            let suma_no_sus = 0;
            let suma_acepta = 0;
            let suma_mayo = 0;
            let adhesivo = '';
            //let valor_tope_ = trRevision[i].getElementsByTagName("td")[7];            
            if (numeroDocumento) {

                let retencion_providencia = valor_nuevo_.getElementsByTagName("input")[0].value;
                for (var k = 0; k < trResumen4.length; k++) {
                    numeroDocumento4 = trResumen4[k].getElementsByTagName("td")[4];
                    let anio4_ = trResumen4[k].getElementsByTagName("td")[0];
                    let mes4_ = trResumen4[k].getElementsByTagName("td")[1];
                    let no_sustentado_pre = trResumen4[k].getElementsByTagName("td")[7];
                    let aceptados_pre = trResumen4[k].getElementsByTagName("td")[9];
                    let campo_txt_mayo = trResumen4[k].getElementsByTagName("td")[3];

                    if (no_sustentado_pre) {
                        let anio = anio_.innerText;
                        let mes = mes_.innerText;
                        //let valor_tope = valor_tope_.innerText;

                        let anio4 = anio4_.innerText;
                        let mes4 = mes4_.innerText

                        let no_sustentado = no_sustentado_pre.innerText;
                        let aceptados = aceptados_pre.innerText;

                        let frecuencia = frecuencia_.innerText
                        let cod_impuesto = cod_impuesto_.innerText
                        if (cod_impuesto === '2021') {
                            alternador = frecuencia.split('_')
                            if (alternador.length == 2) {
                                mes = alternador[1]
                            }
                        }

                        if ((parseInt(anio) === parseInt(anio4)) && (parseInt(mes) === parseInt(mes4))) {
                            let mayo_pre_valor = campo_txt_mayo.getElementsByTagName("input")[0].value;
                            let mayo_pre_id = campo_txt_mayo.getElementsByTagName("input")[0].id;

                            let partes = mayo_pre_id.split("_");
                            adhesivo = partes[1];

                            suma_mayo = parseFloat(mayo_pre_valor).toFixed(2)
                            suma_no_sus = parseFloat(parseFloat(no_sustentado) - parseFloat(retencion_providencia)).toFixed(2)
                            suma_acepta = parseFloat(parseFloat(aceptados) + parseFloat(retencion_providencia)).toFixed(2)

                            if (suma_acepta < 0) {
                                suma_acepta = 0.00;
                            }

                            trResumen4[k].getElementsByTagName("td")[7].innerHTML = suma_no_sus
                            trResumen4[k].getElementsByTagName("td")[9].innerHTML = suma_acepta
                            trResumen4[k].getElementsByTagName("td")[10].innerHTML = suma_acepta
                            //trResumen4[k].getElementsByTagName("td")[12].innerHTML = suma_acepta
                        }
                    }
                }
                //grabando no sustentado    
                const requesta = {
                    param1: ruc,
                    param2: desde,
                    param3: hasta,
                    param4: "F",
                    param5: ($("#span_tramite").html()).trim(),
                    adhesivo: adhesivo,
                    mayor_ajuste: suma_mayo,
                    no_sustentado: suma_no_sus,
                    expediente: 10,
                    usuario: $("#csrf_user").val(),
                    mu: $("#in_xyz").val()
                }
                axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
                    .then(function (resultadoD) {
                        if (parseInt(resultadoD.data.valida) == -100) {
                            window.location = "/account/login";
                        }
                    });
            }
        }
        //grabado de totales    
        fx_totalizar("tabla_retenciones_periodo");
        let parceros = { la_diez: -1, posicion: -1 }
        pre_in_chains($("#txt_ruc_ingresado").val(), los_adhesivos, -1, -1, 0, parceros, -1);
        mensaje("success", "La Providencia ha sido guardada! ")
    });


    //END TRAMITES
    //var semaforizacion = []
    function declas_nocumplen(currentRow) {
        let periodo = currentRow.find("td:eq(0)").text();
        let fecharecepcion = currentRow.find("td:eq(1)").text();
        let adhesivo = currentRow.find("td:eq(2)").text();
        let validacion = '';
        let codigo_impuesto = currentRow.find("td:eq(3)").text().trim();
        let segmento = currentRow.find("td:eq(4)").text().trim();
        let meses_limite = parseInt(currentRow.find("td:eq(8)").text().trim());

        periodo = periodo.replaceAll(" ", "");
        let periodoParalelo = periodo;
        periodo = periodo.replace("-", "_");

        let valoradhesivo = $(`input[name='` + periodo + `']:checked`).val()
        valoradhesivo = valoradhesivo.replaceAll(" ", "");
        //tabla_declaraciones_cumplen
        tablaCumple = document.getElementById("tabla_declaraciones_cumplen");
        trCumple = tablaCumple.getElementsByTagName("tr");
        // efecto agreaga boorra
        for (var i = 0; i < trCumple.length; i++) {
            let td = trCumple[i].getElementsByTagName("td")[0];
            //adhesivoCumple = trCumple[i].getElementsByTagName("td")[2]
            if (td) {
                let periodoCumple = td.innerHTML.replaceAll(" ", "");
                periodoCumple = periodoCumple.replace("-", "_");
                if (periodoCumple.indexOf(periodo) > -1) {
                    trCumple[i].remove();
                }
            }
        }
        let periodicas = $('#tabla_declaraciones_no_cumplen tr:has(td:contains("' + periodoParalelo + '"))');
        for (var l = 0; l < periodicas.length; l++) {
            periodicas[l].style.backgroundColor = "#FAECEA";
        }
        let adhesivos_frm = $('#tabla_declaraciones_no_cumplen tr:has(td:contains("' + valoradhesivo + '"))');
        for (var l = 0; l < adhesivos_frm.length; l++) {
            adhesivos_frm[l].style.backgroundColor = "#D1EFBD";
        }
        /* control de declaracion semestral doble */
        let consultar_adhesivos = 0;
        let segmentados = $('#tabla_declaraciones_no_cumplen tr:has(td:contains("' + segmento + '"))');
        let num_selecciones_mensuales = 0;
        let num_selecciones_semestrales = 0;
        let hay_semestrales = false;
        let periocidad = '';
        //if (!segmento.startsWith("M-",0)){
        if (segmentados) {
            for (var m = 0; m < segmentados.length; m++) {
                let estado = segmentados[m].getElementsByTagName("input")[0].checked;
               // let tipo = segmentados[m].getElementsByTagName("td")[3].getInnerHTML().toString().trim();
                // periocidad = segmentados[m].getElementsByTagName("td")[5].getInnerHTML().toString().trim();
                let tipo = segmentados[m].getElementsByTagName("td")[3].getHTML().toString().trim();
                periocidad = segmentados[m].getElementsByTagName("td")[5].getHTML().toString().trim();

                if (estado) {
                    if (tipo == "SEMESTRAL") {
                        hay_semestrales = true;
                        num_selecciones_semestrales += 1;
                    }
                    if (tipo == "MENSUAL") {
                        num_selecciones_mensuales += 1;
                    }
                }
            }
        }
        if (num_selecciones_semestrales > 1) {
            mensaje("warning", "No puede tener dos declaraciones semestrales en el mismo periodo");
            return;
        }
        /* periodos agregar */
        let aprobar = 0
        let tiposeg = 'M';
        if (segmento.startsWith("M", 0) && (meses_limite == num_selecciones_mensuales)) {
            aprobar = 1
        }
        if (segmento.startsWith("S", 0) && ((meses_limite < 7 && num_selecciones_semestrales == 1) || (meses_limite == num_selecciones_mensuales))) {
            aprobar = 1
            tiposeg = 'S';
        }

        $('<tr>').html(`<td id="periodo"> ${periodo} </td>
            <td> ${fecharecepcion} </td>
            <td> ${adhesivo}</td>
            <td> ${validacion}</td>
            <td> ${codigo_impuesto}</td>
            <td> ${segmento}</td>
            `
        ).appendTo('#tabla_declaraciones_cumplen tbody');

        if (aprobar === 1) {
            if (!aprobados_segmentos.includes(segmento)) {
                aprobados_segmentos.push(segmento)
            }
        }
        if (aprobados_segmentos.length == df_segmentados.length) {
            mensaje("success", "Se procede a descargar las declaraciones")
            consultar_adhesivos = 1;
            fx_adhesivos(consultar_adhesivos, trCumple, $("#inp_escena").val());
            $('#ul_fox a[href="#li_a_tab_analisis"]').tab('show');
            $("#li_a_tab_analisis").show();
            $("#li_a_tab_revision").show();
            $("#li_a_tab_retenciones").show();
            $("#li_a_tab_cadenaiva").show();
        }
    }
    $("#tabla_declaraciones_no_cumplen").on('click', '.clase_radio', function () {
        //e.preventDefault();
        let currentRow = $(this).closest("tr");
        declas_nocumplen(currentRow);
        sortDeclaraciones();
    });
    //tramites similares
    $("#tabla_detalle_tramite_xruc").on('click', '.add_btn_104', function () {
        let currentRow = $(this).closest("tr");
        const ruc = $("#txt_ruc_ingresado").val();
        const anio = currentRow.find("td:eq(5)").text();
        const mes = currentRow.find("td:eq(6)").text();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();
        const requesta = {
            param1: ruc,
            param2: periodo1,
            param3: periodo2,
            param4: 'F',
            //param5:  ($("#span_tramite").html()).trim(),        
            anio: anio,
            mes: mes,
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val()
        }
        if ((parseInt(anio) > 2010 && parseInt(anio) < 2090) && (parseInt(mes) > 0 && parseInt(mes) < 13)) {
            const config = {
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    'X-CSRFToken': 'csrftoken'
                }
            }
            axios.post(`get_internas`, JSON.stringify(requesta), config)
                .then(function (resultado) {
                    if (resultado.data.tramites.length > 0) {
                        let polinesia = resultado.data.tramites;
                        $('#tabla_tramites_similares tbody').empty();
                        $('#tabla_tramites_similares tbody').html('');
                        if (polinesia.length > 0) {
                            $.each(polinesia, function (i, item) {
                                $('<tr>').html(`<td>
                                                <div class="form-check">
                                                <input class="form-check-input clase_btn104" type="checkbox"  name="checkAll" value="${item.anio_fiscal}-${item.mes_fiscal}">
                                                </div>
                                                </td> 
                                                <td> ${polinesia[i].fecha_ingreso} </td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].numero_tramite}  </span></td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].estado}  </span></td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].anio_fiscal}  </span></td>
                                                    <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].mes_fiscal}  </span></td>
                                                    <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].numero_contestacion}  </span></td>
                                                    <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].archivo_contestacion}  </span></td>                                                                                                                                                
                                                `
                                ).appendTo('#tabla_tramites_similares tbody');
                            });
                        }
                    }
                });
            axios.post(`get_previas`, JSON.stringify(requesta), config)
                .then(function (resultado) {
                    if (resultado.data.tramites.length > 0) {
                        let polinesia = resultado.data.tramites;
                        $('#tabla_tramites_previos tbody').empty();
                        $('#tabla_tramites_previos tbody').html('');

                        if (polinesia.length > 0) {
                            $.each(polinesia, function (i, item) {
                                $('<tr>').html(`<td style="width:20%">
                                                <input class="form-check-input clase_btn104" type="checkbox"  name="checkAll" value="${polinesia[i].anio_fiscal}-${polinesia[i].mes_fiscal}">

                                                </td> 
                                                    <td> ${polinesia[i].fecha_ingreso} </td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].numero_tramite}  </span></td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].estado}  </span></td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].anio_fiscal}  </span></td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].mes_fiscal}  </span></td>                                                
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].numero_contestacion}  </span></td>
                                                    <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].archivo_contestacion}  </span></td>                                                                                                                                                
                                                                                                                                                                
                                                `
                                ).appendTo('#tabla_tramites_previos tbody');
                            });
                        }

                    }
                });
            let galleryModal = new bootstrap.Modal(document.getElementById('modalF104'), {
                keyboard: false
            });
            galleryModal.show();

        } else {
            mensaje("error", ` Entrada Incorrecta ${anio} and ${mes} `)
        }
    });
    //tramites previos
    $("#tabla_detalle_tramite_xruc").on('click', '.add_btn_previos', function () {
        let currentRow = $(this).closest("tr");
        const ruc = $("#txt_ruc_ingresado").val();
        const anio = currentRow.find("td:eq(3)").text();
        const mes = currentRow.find("td:eq(4)").text();
        const requesta = {
            param1: ruc,
            param2: periodo1,
            param3: periodo2,
            param4: 'F',
            //param5:  ($("#span_tramite").html()).trim(),            
            anio: anio,
            mes: mes,
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val()
        }
        axios.post(`get_previas`, JSON.stringify(requesta), config)
            .then(function (resultado) {
                if (resultado.data.tramites.length > 0) {
                    let polinesia = resultado.data.tramites;
                    $('#tabla_tramites_previos tbody').empty();
                    $('#tabla_tramites_previos tbody').html('');
                    if (polinesia.length > 0) {
                        $.each(polinesia, function (i, item) {
                            $('<tr>').html('<th scope="row">'
                                + '<div class="form-check">'
                                + `<input class="form-check-input clase_btn104" type="checkbox"  name="checkAll" value="${polinesia[i].anio_fiscal}-${polinesia[i].mes_fiscal}">`
                                + '</div>'
                                + '</th>'
                                + `<td> ${polinesia[i].fecha_ingreso} </td>
                                                <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].numero_tramite}  </span></td>
                                                <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].estado}  </span></td>
                                                <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].anio_fiscal}  </span></td>
                                                <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].mes_fiscal}  </span></td>                                                
                                                                                                                                                         
                                            `
                            ).appendTo('#tabla_tramites_previos tbody');
                        });
                    }

                }
            });

        let galleryModalz = new bootstrap.Modal(document.getElementById('modalprevios'), {
            keyboard: false
        });
        galleryModalz.show();
    });

    //declaraciones 
    $("#tabla_detalle_tramite_xruc").on('click', '.add_btn_analisis', function () {
        let currentRow = $(this).closest("tr");
        const ruc = $("#txt_ruc_ingresado").val();
        let anio = currentRow.find("td:eq(3)").text();
        let mes = currentRow.find("td:eq(4)").text();
        let clase = currentRow.find("td:eq(6)").text();
        let tipotramite = currentRow.find("td:eq(7)").text();
        let subtipotramite = currentRow.find("td:eq(8)").text();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();

        if (periodo1 > 0 && periodo2 > 0) {
            let periodo1 = periodo1 + '-01';
            let periodo2 = periodo2 + '-27';
            const requesta = {
                param1: ruc,
                param2: periodo1,
                param3: periodo2,
                param4: 'F',
                param5: ($("#span_tramite").html()).trim(),
                usuario: $("#csrf_user").val(),
                mu: $("#in_xyz").val()
            }
            axios.post(`get_declaraciones_periodo`, JSON.stringify(requesta), config)
                .then(function (resultado) {
                    if (resultado.data.decla.length > 0) {
                        let polinesia = resultado.data.decla;
                        $('#tabla_declaraciones tbody').empty();
                        $('#tabla_declaraciones tbody').html('');
                        if (polinesia.length > 0) {
                            $.each(polinesia, function (i, item) {
                                $('<tr>').html(`<th scope="row">
                                            <div class="form-check form-radio-outline form-radio-primary mb-3">
                                                <input class="form-check-input clase_btn104" type="radio"  name="checkAll" value="${polinesia[i].anio_fiscal}-${polinesia[i].mes_fiscal}" checked>
                                            </div>
                                            </th> 
                                            <td> ${polinesia[i].anio_fiscal}-${polinesia[i].mes_fiscal} </td>
                                                <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].numero_identificacion}  </span></td>
                                                <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].fecha_recepcion}  </span></td>
                                                <td><span class="badge badge-soft-info text-uppercase"> ${polinesia[i].estadentro_del_year}  </span></td>
                                                <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].numero_adhesivo}  </span></td>                                               
                                                <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].declaracion_cero}  </span></td>
                                                <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].sct_adquisicion_mesanterior}  </span></td>
                                                <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].ajuste_x_adquisiciones}  </span></td>
                                                <td><span class="badge badge-soft-danger text-uppercase"> ${polinesia[i].ajuste_x_retenciones}  </span></td>
                                            `
                                ).appendTo('#tabla_declaraciones tbody');
                            });
                        }
                    }
                });
        }
    });


    $("#tabla_detalle_tramite_xruc").on('click', '.clase_radio_tramite', function () {
        let rad_numero_tramite = $(`input[name='rad_tramites']:checked`).val()
        $("#span_tramite_texto").html(" TRAMITE ELEGIDO : ");
        $("#span_tramite").html(rad_numero_tramite);
        const ruc = $("#txt_ruc_ingresado").val();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();
        const requesta = {
            param1: ruc,
            param2: periodo1,
            param3: periodo2,
            expediente: 1500,
            param5: rad_numero_tramite,
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val()
        }
        axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
            .then(function (resultadoD) {
                if (parseInt(resultadoD.data.valida) == -100) {
                    window.location = "/account/login";
                }
            });

    });


    function fn_mayorizar(currentRow) {
        let el_pre_mayor = currentRow.find("td:eq(3)")
        if (!isNumeric(el_pre_mayor[0].getElementsByTagName("input")[0].value)) {
            return true
        }
        let valorMayorB = parseFloat(el_pre_mayor[0].getElementsByTagName("input")[0].value);
        let divisores_sp = (el_pre_mayor[0].getElementsByTagName("input")[0].id);
        let partes = divisores_sp.split("_");
        let adhesivo = partes[1]
        let posicion = partes[2]
        let def = 0
        if (valorMayorB >= 0) {
            let valorDeclarado_a = currentRow.find("td:eq(2)").text();
            valorDeclarado_a = valorDeclarado_a.replace(/\$/g, "");
            valorDeclarado_a = replaceAll(valorDeclarado_a, ',', '');
            let valorDeclaradoA = parseFloat(valorDeclarado_a).toFixed(2);
            let diferencia_actualizar = 0;
            let ingresado = parseFloat(currentRow.find("td:eq(5)").text()).toFixed(2);
            let no_constan_base = 0;
            if (Math.min(parseFloat(valorDeclaradoA), valorMayorB) - ingresado >= 0) {
                no_constan_base = (Math.min(parseFloat(valorDeclaradoA), valorMayorB) - ingresado).toFixed(2);
            }
            currentRow.find("td:eq(6)").text(parseFloat(no_constan_base).toFixed(2));
            let no_sustentado = parseFloat(currentRow.find("td:eq(7)").text()).toFixed(2);
            let negados = parseFloat(currentRow.find("td:eq(8)").text()).toFixed(2);
            //Diferencia
            if (parseFloat(valorDeclaradoA) >= parseFloat(valorMayorB)) {
                diferencia_actualizar = parseFloat(valorDeclaradoA) - parseFloat(valorMayorB).toFixed(2);
            }
            currentRow.find("td:eq(4)").text(parseFloat(diferencia_actualizar).toFixed(2));
            if ((valorDeclaradoA - diferencia_actualizar - parseFloat(no_constan_base).toFixed(2) - no_sustentado - negados) >= 0) {
                def = (valorDeclaradoA - diferencia_actualizar - parseFloat(no_constan_base).toFixed(2) - no_sustentado - negados).toFixed(2)
            }
            let la_diez = parseFloat(def).toFixed(2);
            if (la_diez < 0) {
                la_diez = 0.00;
            }
            currentRow.find("td:eq(9)").text(la_diez);
            currentRow.find("td:eq(10)").text(la_diez);
            currentRow.find("td:eq(12)").text(la_diez);
            fx_totalizar("tabla_retenciones_periodo");
            const ruc = $("#txt_ruc_ingresado").val();
            const periodo1 = $("#txt_desde").val();
            const periodo2 = $("#txt_hasta").val();
            const requesta = {
                param1: ruc,
                param2: periodo1,
                param3: periodo2,
                param5: ($("#span_tramite").html()).trim(),
                adhesivo: adhesivo,
                mayor_ajuste: valorMayorB,
                no_sustentado: no_sustentado,
                expediente: 10,
                usuario: $("#csrf_user").val(),
                mu: $("#in_xyz").val()
            }

            axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
                .then(function (resultadoD) {
                    if (parseInt(resultadoD.data.valida) == -100) {
                        window.location = "/account/login";
                    }
                });

            return { la_diez, posicion };

        } else {
            return true;

        }
    }

    function fn_resolver_comp_futuro(compensa) {
        if (compensa.length > 0) {
            compensar_futuro_pasado(-1, -1, compensa, 0);
        }
    }

    $("#tabla_retenciones_periodo").on("keyup", "tr .ctxt_mayores", function (event) {
        let currentRow = $(this).closest("tr");
        if ([37, 38, 39, 40, 8, 16].includes(event.keyCode)) {
            event.preventDefault();
            return true;
        }
        if ([13].includes(event.keyCode)) {
            let parceros = fn_mayorizar(currentRow);
            pre_in_chains($("#txt_ruc_ingresado").val(), los_adhesivos, -1, -1, 0, parceros, -1);
        } else {
            return true;
        }
    });

    // PANTALLA compensacion a futuro
    $("#tab_compensacion_futuro").on("keyup", "tr .ctxt_futuro", function (event) {
        let compensa = $(this).val();
        let pre_position = $(this)[0].id;
        let espacios = pre_position.split('_')
        let posicion = espacios[1];
        if ([37, 38, 39, 40, 8, 16].includes(event.keyCode)) {
            event.preventDefault();
            return true;
        }
        if (!isNumeric(compensa)) {
            return
        }
        if ([13].includes(event.keyCode)) {
            futuro_pasado = 1;
            fn_resolver_comp_futuro(compensa.toString() + "_" + posicion.toString());
        } else {
            return true;
        }
    });

    $("#tab_Informe_Revision_no").on("keyup", "tr .ctxt_retenido", function (event) {
        if ([37, 38, 39, 40, 8, 16].includes(event.keyCode)) {
            event.preventDefault();
            return;
        }
        if ([13].includes(event.keyCode)) {
            let currentRow = $(this).closest("tr");
            let valorRetencionNuevo_ = $(this).val();
            if ((valorRetencionNuevo_.length > 0) && isNumeric(valorRetencionNuevo_)) {
                let valorDeclaradox_ = currentRow.find("td:eq(9)").text();
                if (!isNumeric(valorRetencionNuevo_)) {
                    mensaje("error", " La columna de retencion no contiene un valor numerico, por favor revise! ");
                    $(this).val('0')
                    return;
                }
                if (!isNumeric(valorDeclaradox_)) {
                    mensaje("error", " el valor ingresado no es numerico! ");
                    return;
                }
                let valorRetencionNuevo = parseFloat(valorRetencionNuevo_);
                let valorDeclaradox = parseFloat(valorDeclaradox_);
                if (valorRetencionNuevo > valorDeclaradox) {
                    mensaje("error", " el valor ingresado supera al valor retenido proyectado! ");
                    $(this).val('0')
                    return;
                }
            }
        }
    });

    function fn_re_encadenado(se_graba, tipo) {
        let ruc = $("#txt_ruc_ingresado").val();
        let flo_adq = -1;
        let flo_ret = -1;
        let pre_flo = -1;
        pre_flo = $("#txt_iva_sct_adquisicion_mesanterior").val();
        if (!isNumeric(pre_flo)) {
            mensaje("error", " El valor no es valido ");
            $("#txt_iva_sct_adquisicion_mesanterior").val('0');
            return;
        }
        if (parseFloat(pre_flo) < 0) {
            mensaje("error", ` el valor ${pre_flo} debe ser mayor a cero `);
        }
        $('#txt_iva_sct_adquisicion_mesanterior').attr('disabled', 'disabled');
        if (['adq'].includes(tipo)) {
            flo_adq = pre_flo;
        }

        if (['ret'].includes(tipo)) {
            flo_ret = $("#txt_iva_sct_retenciones_mesanterior").val();


            if (!isNumeric(flo_ret)) {
                mensaje("error", " el valor ingresado no es valido! ");
                $("#txt_iva_sct_retenciones_mesanterior").val('0');
                return;
            }
            if (parseFloat(flo_ret) < 0) {
                mensaje("error", ` el valor ${flo_ret} debe ser mayor a cero `);
            }
            $('#txt_iva_sct_retenciones_mesanterior').attr('disabled', 'disabled');
        }
        let parceros = { la_diez: -1, posicion: -1 }
        pre_in_chains(ruc, los_adhesivos, flo_adq, flo_ret, se_graba, parceros, pre_flo_txt);
    }


    $("#tab_cadena_iva_transpuesta").on("keyup", "tr .ctxt_diferencias_adq", function (event) {
        let currentRow = $(this).closest("tr");

        if ([37, 38, 39, 40, 8, 16].includes(event.keyCode)) {
            event.preventDefault();
            return true;
        }

        if (!isNumeric($(this).val())) {
            return
        }

        if (([13].includes(event.keyCode)) && (cerrar_ta === 1)) {
            cerrar_ta = 0;
            $('.ctxt_diferencias_adq').attr('disabled', 'disabled');
            g_saldo_adq_ma = quitarMoneda(g_saldo_adq_ma.toString());

            pre_flo_txt = $('.ctxt_diferencias_adq').val();
            switch (currentRow.find("td:eq(0)").text().trim()) {
                case "SALDO CREDITO TRIBUTARIO POR ADQUISICIONES MES ANTERIOR": if (parseFloat($("#txt_iva_sct_adquisicion_mesanterior").val()) > parseFloat(g_saldo_adq_ma)) { $("#txt_iva_sct_adquisicion_mesanterior").val(g_saldo_adq_ma); return false } break;
            }
            fn_re_encadenado(0, 'adq');
            /* FIN */
        } else {
            return true;
        }
    });

    $("#tab_cadena_iva_transpuesta").on("keyup", "tr .ctxt_diferencias_ret", function (event) {
        let currentRow = $(this).closest("tr");
        if ([37, 38, 39, 40, 8, 16].includes(event.keyCode)) {
            event.preventDefault();
            return true;
        }

        if (!isNumeric($(this).val())) {
            return
        }

        if (([13].includes(event.keyCode)) && (cerrar_tb === 1)) {
            g_saldo_ret_ma = quitarMoneda(g_saldo_ret_ma.toString());
            cerrar_tb = 0;
            $('.ctxt_diferencias_ret').attr('disabled', 'disabled');

            switch (currentRow.find("td:eq(0)").text().trim()) {
                case "SALDO CREDITO TRIBUTARIO POR RETENCIONES MES ANTERIOR": if (parseFloat($("#txt_iva_sct_retenciones_mesanterior").val() > parseFloat(g_saldo_ret_ma))) { $("#txt_iva_sct_retenciones_mesanterior").val(g_saldo_ret_ma); return false } break;
            }
            fn_re_encadenado(0, 'ret');
            /* FIN */
        } else {
            return true;
        }
    });

    $("#btn_grabar_precadena").click(function () {
        let tram_ele = ($("#span_tramite").html()).trim();
        if (tram_ele.length === 0) {
            mensaje("warning", "Debe escoger un trámite, luego de guardar se muestra el boton de descarga de la cadena!");
            $('#ul_fox a[href="#papel-contri"]').tab('show');
        } else {
            $("#li_a_resumen_periodos").show();
            $("#li_a_compensa_futuro").show();
            $("#div_exportar_excel_cad_warp_ir").show();

            fn_re_encadenado(1, 'non');
            $("#div_exportar_excel_cad_warp_ir").show();
            $("#li_a_datos_resolucion").show();
        }
    });

    $("#inp_escena").val('F');

    //electronico
    $("#btn_encadenar_tramites").click(function () {
        const escena = {
            param4: "E"
        }
        verificartramites(escena.param4);
    });

    $("#btn_atras").click(function () {
        $("#div_escena_dos").hide();
        $("#div_escena_uno").show();
        $('#div_todos_tabs').hide();
        $('#div_barra_menu').hide();
        $('#txt_ruc_ingresado').val('');
        $('#txt_desde').val('');
        $('#txt_hasta').val('');
        reiniciar_tablas();
    });

    $("#btn_obsevaciones_gra").click(function () {
        const ruc = $("#txt_ruc_ingresado").val();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();
        const requesta = {
            param1: ruc,
            param2: periodo1,
            param3: periodo2,
            param4: 'F',
            param5: ($("#span_tramite").html()).trim(),
            obs: $("#txt_observacion_ut").val(),
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val()
        }
        axios.post(`save_anywhere`, JSON.stringify(requesta), config)
            .then(function (resultado) {
                if (parseInt(resultado.data.valida) == -100) {
                    window.location = "/account/login";
                } else {
                    mensaje("warning", "Mensaje guardado correctamente")
                }
            });
    });

    $("#btn_grabar_caso").click(function (event) {
        event.preventDefault()
        const ruc = $("#txt_ruc_ingresado").val();
        const periodo1 = $("#txt_desde").val();
        const periodo2 = $("#txt_hasta").val();
        const requesta = {
            param1: ruc,
            param2: periodo1,
            param3: periodo2,
            param4: 'Z',
            param5: ($("#span_tramite").html()).trim(),
            obs: $("#txt_observacion_ut").val(),
            campo_primario: ((Math.random() * 100) + 1).toString(),
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val()
        }
        loading(true);
        axios.post(`save_anywhere`, JSON.stringify(requesta), config)
            .then(function (resultado) {
                if (parseInt(resultado.data.valida) == -100) {
                    window.location = "/account/login";
                } else {
                    if (parseInt(resultado.data.valida) === 1) {
                        reiniciar_tablas();
                        $("#txt_ruc_ingresado").val('')
                        //$("#txt_desde").val('2023-01-01')
                        //$("#txt_hasta").val('2023-04-19')
                        $("#span_tramite").html('')
                        mensaje("warning", "CASO  guardado correctamente")
                        loading(false);
                    }
                }
            });
    });

    $("body").on("click", ".a_desca_interna", function (event) {

        let referencia = event.currentTarget.href;
        const llamado = event.currentTarget.download;
        let a = referencia.split("get_informe")
        let z = '';
        if (a.length > 0)
            z = a[1]
        $("#span_tramite_texto").html("-TRAMITE ELEGIDO : ");
        ($("#span_tramite").html()).trim();
        if (z.length > 0) {
            loading(true);
            referencia = "get_informe" + z;
            axios.post(referencia, null,
                {
                    headers:
                    {
                        'Content-Disposition': `attachment; filename=${llamado}`,
                        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    },
                    responseType: 'arraybuffer',
                }
            ).then((response) => {
                if (response.data.byteLength < 100) {
                    window.location = "/account/login";
                } else {
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', llamado);
                    document.body.appendChild(link);
                    link.click();
                }
                loading(false);
            })
                .catch((error) => console.log(error));
        }
        event.preventDefault();
    });
});
