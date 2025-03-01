

function mensaje(tipo, texto){
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



$.fn.dataTable.pipeline = function (opts) {
    // Configuration options
    var conf = $.extend({
        pages: 5, 
        url: '', 
        data: null, 
        method: 'GET'
    }, opts);

    // Private variables for storing the cache
    var cacheLower = -1;
    var cacheUpper = null;
    var cacheLastRequest = null;
    var cacheLastJson = null;

    return function (request, drawCallback, settings) {
        var ajax = false;
        var requestStart = request.start;
        var drawStart = request.start;
        var requestLength = request.length;
        var requestEnd = requestStart + requestLength;

        if (settings.clearCache) {
            ajax = true;
            settings.clearCache = false;
        } else if (cacheLower < 0 || requestStart < cacheLower || requestEnd > cacheUpper) {
            ajax = true;
        } else if (JSON.stringify(request.order) !== JSON.stringify(cacheLastRequest.order) ||
                JSON.stringify(request.columns) !== JSON.stringify(cacheLastRequest.columns) ||
                JSON.stringify(request.search) !== JSON.stringify(cacheLastRequest.search)
                ) {
            ajax = true;
        }

        cacheLastRequest = $.extend(true, {}, request);

        if (ajax) {
            // Need data from the server
            if (requestStart < cacheLower) {
                requestStart = requestStart - (requestLength * (conf.pages - 1));

                if (requestStart < 0) {
                    requestStart = 0;
                }
            }

            cacheLower = requestStart;
            cacheUpper = requestStart + (requestLength * conf.pages);

            request.start = requestStart;
            request.length = requestLength * conf.pages;

            // Provide the same `data` options as DataTables.
            if (typeof conf.data === 'function') {
                var d = conf.data(request);
                if (d) {
                    $.extend(request, d);
                }
            } else if ($.isPlainObject(conf.data)) {
                $.extend(request, conf.data);
            }

            return $.ajax({
                "type": conf.method,
                "url": conf.url,
                "data": request,
                "dataType": "json",
                "cache": false,
                "success": function (json) {
                    cacheLastJson = $.extend(true, {}, json);

                    if (cacheLower !== drawStart) {
                        json.data.splice(0, drawStart - cacheLower);
                    }
                    if (requestLength >= -1) {
                        json.data.splice(requestLength, json.data.length);
                    }

                    drawCallback(json);
                }
            });
        } else {
            json = $.extend(true, {}, cacheLastJson);
            json.draw = request.draw; // Update the echo for each response
            json.data.splice(0, requestStart - cacheLower);
            json.data.splice(requestLength, json.data.length);

            drawCallback(json);
        }
    };
};


$(document).ready(function () {

    $("#btn_buscar_ruc").click(function () {
        var url = "verificaRUC?ufx="+$("#txtNumeroRuc").val(); 
        $("#txtContribuyente").val('');        
        $.ajax({
            type: "POST",
            url: url,
            //data: {"ufx":  $("#txtNumeroRuc").val() },
            //data: $('form').serialize(), // serializes the form's elements.
            success: function (respuesta) {
                console.log(respuesta);  
                $("#txtContribuyente").val(respuesta);
            }
        });


        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
                }
            }
        })

    });

        $('#txtNumeroTramite').on('keypress', function(e) {
            var keyCode = e.keyCode;
              if (keyCode === 13) {
                e.preventDefault();
                let tramite = $('#txtNumeroTramite').val()
                axios.get("fx_consultar_tramite_snt?ufx="+tramite)
                .then(function (response) {
                  console.log(response.data);
                  console.log(response.status);
                  console.log(response.statusText);
                  console.log(response.headers);
                  console.log(response.config);
                });                



               }
            });

            $('#txtbusquedatramites').on('keypress', function(e) {
                var keyCode = e.keyCode;
                  if (keyCode === 13) {
                        e.preventDefault();
                        

                        //    let table = new DataTable('#tabla_detalle_tramite', {
                        //        "ajax": `fx_consultar_tramite_snt?ufx=${$("#txtbusquedatramites").val()}` 
                        //    });


                        axios(`fx_consultar_tramite_snt?ufx=${$("#txtbusquedatramites").val()}`)
                        .then(function (resultado) {
                                let argelia = resultado.data.cabecera;
                                if (argelia.length>0){
                                    let marruecos = resultado.data.detalle;
                                    //<!--
                                    //span_numtramite       span_clasetramite               span_estado     span_ruc        span_cedula     span_razonsocial        span_fechaingreso 
                                    //numtramite	        clasetramite	                estado  	    ruc     	    cedula	        razonsocial	            fechaingreso
                                    //117012020637116	    DEVOLUCIONES DE IMPUESTOS	    Notificado	    17924422795001	1	            INDRA SISTEMAS	        2020-11-27
                                    //-->                            
                                    
                                    $("#span_numtramite").html(argelia[0].numero_tramite);
                                    $("#span_clasetramite").html(argelia[0].nombre_clase_tramite);
                                    
                                    $("#span_estado").html(argelia[0].codigo_estado);
                                    $("#span_ruc").html(argelia[0].numero_ruc);
                                    $("#span_ruc_kuwait").html(argelia[0].numero_ruc);
                                    
                                    $("#span_razonsocial").html(argelia[0].razon_social);
                                    $("#span_fechaingreso").html(argelia[0].fecha_ingreso);

                                    $('#tabla_detalle_tramite tbody').empty();   
                                    $('#tabla_detalle_tramite tbody').html('');
                                    if (marruecos.length>0){
                                          $.each(marruecos, function(i, item) {
                                            $('<tr>').html("<td>" + marruecos[i].id_tramite + "</td><td>" 
                                                                + marruecos[i].numero_tramite  + "</td><td>" 
                                                                + marruecos[i].nombre_tipo_tramite + "</td><td>" 
                                                                + marruecos[i].nombre_sub_tipo_tramite  + "</td><td>"
                                                                + marruecos[i].anio_fiscal + "</td><td>"
                                                                + marruecos[i].mes_fiscal + "</td><td>"
                                                                + marruecos[i].monto_solicitado + "</td><td>"
                                                                + marruecos[i].forma_pago + "</td><td>"
                                                                + marruecos[i].actividades_tiempos 
                                                                + "</td>").appendTo('#tabla_detalle_tramite tbody');
                                        });
                                    }else{
                                        mensaje("warning",`NO existe detalles del tramite ${$("#txtbusquedatramites").val()} `)

                                    }

                                    let libano = resultado.data.contri;
                                    if (libano.length>0){

                                        $("#span_m_ruc").html(libano[0].numero_ruc);
                                        $("#span_m_rsocial").html(libano[0].razon_social);
                                        $("#span_m_fechaingreso").html(libano[0].fecha_inicio_actividades);
                                        $("#span_m_contabilidad").html(libano[0].obligado);                                                                                                                        


                                    }


                                    let palestina = resultado.data.xruc;                                    
                                    $('#tabla_detalle_tramite_xruc tbody').empty();   
                                    $('#tabla_detalle_tramite_xruc tbody').html('');

                                    if (palestina.length>0){
                                        $.each(palestina, function(i, item) {
                                            $('<tr>').html("<td>" + palestina[i].codigo_estado + "</td><td>" 
                                                                + palestina[i].nombre_clase_tramite + "</td><td>"                                                                 
                                                                + palestina[i].fecha_ingreso + "</td><td>" 
                                                                + palestina[i].fecha_vencimiento  + "</td><td>"
                                                                + palestina[i].nombre_tipo_tramite + "</td><td>"
                                                                + palestina[i].nombre_firmante + "</td><td>"
                                                                + palestina[i].numero_ruc + "</td><td>"
                                                                + palestina[i].numero_tramite + "</td><td>"
                                                                + palestina[i].descripcion_tramite  + "</td><td>"
                                                                + palestina[i].observaciones 
                                                                + "</td>").appendTo('#tabla_detalle_tramite_xruc tbody');
                                        });
                                    }

                                    let micronesia = resultado.data.el104;                                    
                                    $('#tabla_periodos_ruc_disponibles tbody').empty();   
                                    $('#tabla_periodos_ruc_disponibles tbody').html('');


                                /*    
                                <th scope="row">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="checkAll" value="option1">
                                </div>
                                </th>
                                <td class="id"><a href="javascript:void(0);" onclick="ViewTickets(this)" data-id="001" class="fw-medium link-primary">#VLZ001</a></td>
                                <td class="status"><span class="badge badge-soft-warning text-uppercase">Inprogress</span></td>
                                <td class="priority"><span class="badge bg-danger text-uppercase">High</span></td>
                                */    
                            



                                    if (micronesia.length>0){
                                        $.each(micronesia, function(i, item) {
                                            $('<tr>').html('<th scope="row">'
                                                            +'<div class="form-check">'
                                                    	    +`<input class="form-check-input clase_btn104" type="checkbox"  name="checkAll" value="${micronesia[i].anio_fiscal}-${micronesia[i].mes_fiscal}">`
                                                            +'</div>'
                                                            +'</th>' 
                                                            + `<td class="id">
                                                                <div class="edit">
                                                                    <button class="btn btn-sm btn-success add_btn_104" >${micronesia[i].anio_fiscal}-${micronesia[i].mes_fiscal}</button>
                                                                </div>                                                                
                                                                
                                                                ` 
                                                                +  "</td>"
                                                            + `<td><span class="badge badge-soft-warning text-uppercase">` + micronesia[i].numdeclas  + "</span></td>"
                                                            ).appendTo('#tabla_periodos_ruc_disponibles tbody');
                                        });
                                    }


                                    ///tabla_periodos_ruc_disponibles

  


                                }else{
                                    mensaje("error",`NO existe el trámite : ${$("#txtbusquedatramites").val()} `)
                                }

                                $("#txtbusquedatramites").val('');
            
                            })
                            .catch(function (error) {
                                mensaje("error",`NO existe el trámite : ${$("#txtbusquedatramites").val()}   ${error} `)

                            })
                            .then(function () {
                                // always executed
                            });
                    

                  }
            });

         
            
            


        $("#tabla_periodos_ruc_disponibles").on('click','.add_btn_104',function(){
            // get the current row
            //alert(1);
            var periodo =  this.getInnerHTML();
            //alert(periodo);
            //var currentRow=$(this).closest("tr"); 
            //var col1=currentRow.find("td:eq(0)").text(); // get current row 1st TD value
            //alert(data);

            axios(`get_canadian?ufx=${$("#span_m_ruc").html()}`)
            .then(function (resultado) {

                    if (resultado.data.decla104.length>0){

                        let polinesia = resultado.data.decla104;                                    
                        $('#tabla_f104_by_periodo tbody').empty();   
                        $('#tabla_f104_by_periodo tbody').html('');

                        //codigo_formulario	numero_secuencial  fecha_recepcion	numero_adhesivo	sustitutiva_original    total_pagado	valor_interes   ultima_declaracion	
                        //declaracion_cero	numero_formulario_sustituye	sal_crt_man_270	dev_crt_eft_mac_280	dev_rch_ipt_crt_290    
                        if (polinesia.length>0){
                            $.each(polinesia, function(i, item) {
                                $('<tr>').html('<th scope="row">'
                                                +'<div class="form-check">'
                                                +`<input class="form-check-input clase_btn104" type="checkbox"  name="checkAll" value="${polinesia[i].anio_fiscal}-${polinesia[i].mes_fiscal}">`
                                                +'</div>'
                                                +'</th>' 
                                                + `<td class="id">
                                                    <div class="edit">
                                                        <button class="btn btn-sm btn-success add_btn_104" >${polinesia[i].anio_fiscal}-${polinesia[i].mes_fiscal}</button>
                                                    </div>                                                                
                                                    
                                                    ` 
                                                    +  "</td>"
                                                + `<td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].codigo_formulario}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].numero_secuencial}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].fecha_recepcion}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].numero_adhesivo}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].sustitutiva_original}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].total_pagado}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].valor_interes}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].ultima_declaracion}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].declaracion_cero}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].numero_formulario_sustituye}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].sal_crt_man_270}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].dev_crt_eft_mac_280}  </span></td>
                                                    <td><span class="badge badge-soft-warning text-uppercase"> ${polinesia[i].dev_rch_ipt_crt_290}  </span></td>                                                                                                                                                            
                                                `
                                                ).appendTo('#tabla_f104_by_periodo tbody');
                            });
                        }







                    }
                });


            var galleryModal = new bootstrap.Modal(document.getElementById('modalF104'), {
                keyboard: false
              });
              
              
              galleryModal.show();

        });            




        $("#txtNumeroTramite11").click(function () {
            var url = `verificaRUC?ufx=${$("#txtNumeroRuc").val()}`; 
            $("#txtContribuyente").val('');
            $.ajax({
                type: "POST",
                url: url,
                //data: {"ufx":  $("#txtNumeroRuc").val() },
                //data: $('form').serialize(), // serializes the form's elements.
                success: function (respuesta) {
                    console.log(respuesta);  
                    $("#txtContribuyente").val(respuesta);
                }
            });
    
    
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
                    }
                }
            })
    




    });


});
