/*
Template JS: SRI -  development javascript
Author: jagonzalezj
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: grid Js File
*/


const  isdigito =(value)=>{
    const val=Number(value)?true:false
    return val
}

$(document).ready(function () {
    
    $("#btn_generar_informe").click(function(){
        
        var desde = $("#txt_desde_ir").val();
        var hasta = $("#txt_hasta_ir").val();
        var ruc = $("#txt_ruc_ingresado_ir").val();
        

        if (!isdigito(ruc)){
            mensaje("error","El campo RUC debe ser un valor numerico")
            $('#txt_ruc_ingresado_ir').trigger('focus');
            return;
        }


        if ( ![10,13].includes(ruc.length ) )  {
            mensaje("error","El campo RUC debe ser tener 13 0 10  caracteres")
            return;
        }                    
                    


        if ( (desde.length>0) && (hasta.length>0)){
            desde = desde + '-01';
            hasta = hasta + '-27'; 



            var _periodo1 = desde;
            var _periodo2 = hasta;
            var escenario = 'E'
            
            
            var novalen = '';
                        var valen = '';                    
                        axios(`get_compritas?ufx=${ruc}&ufy=${_periodo1}&ufz=${_periodo2}&uf=${escenario}`).then(function (compra) {
                        if (compra.data.retencionesz){
                                if (compra.data.retencionesz.length>0){
                                    let argentina = compra.data.retencionesz;         
                                    let filipinas = compra.data.sumasretenciones;                                    
                                    let rubik = parseInt(compra.data.longitudcompras);
                                    let ghost = compra.data.gasper;
                                    let deadpool = compra.data.deadpool;
                                    let llave = compra.data.llave;
                                    let doble = compra.data.duplicados;
                                    let doblesum = compra.data.duplicados_sum;
                                    novalen = compra.data.dfnovalidos;
                                    valen = compra.data.dfvalidos;
                                    //longitudes
                                    $("#btn_lista_todo_ir").html(` Todos (${compra.data.len_todos}) `)                            
                                    $("#btn_lista_fantasmas_ir").html(` Fantasmas (${compra.data.len_fantasma}) `)                            
                                    $("#btn_lista_fallecidos_ir").html(` Fallecidos (${ compra.data.len_fallen  === undefined ? 0 : compra.data.len_fallen }) `)                            
                                    $("#btn_lista_ffpv_ir").html(` FFPV (${compra.data.len_ffpv}) `)                            
                                    $("#btn_lista_cruza_ir").html(` Cruzan (${compra.data.len_aceptados}) `)    
            
                                    //$("#li_a_duplicados").html(` Duplicados (${compra.data.len_duplicados}) `)    
                                    //$("#li_a_providencia").html(` Providencias (${compra.data.len_nocruzan}) `)    
            
            
                                    let corea_del_norte = compra.data.nocruzan;                              
            
                                        
            
                                    /* END */
                                    $('#tab_Informe_Revision_ir tbody').empty();   
                                    $('#tab_Informe_Revision_ir tbody').html('');                                        
                                    if (argentina.length>0){
                                        $.each(argentina, function(i, item) {
            
                                            let mes_curso = parseInt(argentina[i].mes);
                                            let anio_curso = parseInt(argentina[i].anio);
                                            var mes_siguiente = 0;
                                            var anio_siguiente = 0;
                                            var unitamas =0; 
                                            if (i<rubik) {  
                                                if (argentina[i+1]){
                                                    mes_siguiente = parseInt(argentina[i+1].mes);
                                                    anio_siguiente = parseInt(argentina[i+1].anio);
                                                }else{
                                                    unitamas =1;
                                                }
                                            }
            
                                            var backg = "trlimon";
                                            if ( (argentina[i].es_fantasma === 'si') || (argentina[i].es_fallecido === 'si') || (argentina[i].es_ffpv === 'si')  ){
                                                backg = "trColorRojoBajo";
                                            }
            
                                        
                                            $(`<tr  class="fila ${backg}">`).html(`
                                                            <td> ${i} </td>
                                                            <td> ${argentina[i].ruc_contrib_informan} </td>
                                                            <td> ${argentina[i].razon_social} </td>
                                                            <td> ${argentina[i].fecha_emi_retencion  }     </td>                                                
                                                            <td> ${argentina[i].serie} </td>
                                                            <td> ${argentina[i].secuencial_retencion} </td>
                                                            <td> ${argentina[i].valor_retencion} </td>
                                                            <td> ${argentina[i].es_fantasma} </td>
                                                            <td> ${argentina[i].es_fallecido} </td>
                                                            <td> ${argentina[i].es_ffpv} </td>
                                                            <td> ${argentina[i].cruza} </td>                                                
                                                            <td> ${argentina[i].conclusion} </td>
                                                            <td> </td>                         
                                                            <td> ${argentina[i].autorizacion} </td>                                                                       
                
                                                            `
                                                            ).appendTo('#tab_Informe_Revision_ir tbody');
                                            
                                                            if (  ( (anio_curso === anio_siguiente) &&  (mes_curso != mes_siguiente) )  || (unitamas===1) || (anio_curso !== anio_siguiente)  )  {
                                                                var valor = 0;
                                                                for (var k=0;k<filipinas.length;k++){
                                                                    if (parseInt(argentina[i].mes) === parseInt(filipinas[k].mes)  && parseInt(argentina[i].anio) === parseInt(filipinas[k].anio)){
                                                                        valor =    filipinas[k].valor_retencion;
                                                                        break;
                                                                    }
                                                                }
                                                                var elnombre = '';
                                                                switch (parseInt(argentina[i].mes))
                                                                { 
                                                                    case 1:  elnombre = 'ENERO'; break;
                                                                    case 2:  elnombre = 'FEBRERO'; break;
                                                                    case 3:  elnombre = 'MARZO'; break;
                                                                    case 4:  elnombre = 'ABRIL'; break;
                                                                    case 5:  elnombre = 'MAYO'; break;
                                                                    case 6:  elnombre = 'JUNIO'; break;
                                                                    case 7:  elnombre = 'JULIO'; break;
                                                                    case 8:  elnombre = 'AGOSTO'; break;
                                                                    case 9:  elnombre = 'SEPTIEMBRE'; break;
                                                                    case 10:  elnombre = 'OCTUBRE'; break;
                                                                    case 11:  elnombre = 'NOVIEMBRE'; break;
                                                                    case 12:  elnombre = 'DICIEMBRE'; break;
            
                                                                }    
            
                                                                $('<tr style="background-color:#e0ffff" >').html(`
                                                                <td colspan="12" align="center">SUBTOTAL VÁLIDO ${elnombre} </td>
                                                                <td> ${valor} </td>
                                                
                                                            `
                                                                ).appendTo('#tab_Informe_Revision_ir tbody');
                                            
                                                            } 
                                            
                                        });
                                    }                        
            
            
                                    /*
                                    $('#tab_Informe_Revision_no tbody').empty();   
                                    $('#tab_Informe_Revision_no tbody').html('');                                  
                                    if (corea_del_norte.length>0){
                                        $.each(corea_del_norte, function(i, item) {
            
                                            var propiedad_lectura= '';
                                    
                                            if ( (corea_del_norte[i].es_fantasma == 'si') ||  (corea_del_norte[i].es_fallecido == 'si') ||  (corea_del_norte[i].es_ffpv == 'si')   ){
                                                propiedad_lectura = 'readonly disabled'
                                            }
            
            
                                            $(`<tr>`).html(`
                                                            <td> ${i} </td>
                                                            <td> ${corea_del_norte[i].anio} </td>
                                                            <td> ${corea_del_norte[i].mes} </td>
                                                            <td> ${corea_del_norte[i].ruc_contrib_informan}     </td>                                                
                                                            <td> ${corea_del_norte[i].numero_documento} </td>
                                                            <td> ${corea_del_norte[i].razon_social} </td>
                                                            <td> ${corea_del_norte[i].fecha_emi_retencion} </td>
                                                            <td> ${corea_del_norte[i].serie}  </td>
                                                            <td> ${corea_del_norte[i].secuencial_retencion} </td>
                                                            <td> ${corea_del_norte[i].es_fantasma} </td>
                                                            <td> ${corea_del_norte[i].es_fallecido} </td>
                                                            <td> ${corea_del_norte[i].es_ffpv} </td>
                                                            <td> ${corea_del_norte[i].valor_retencion} </td>                                                
                                                            <td style="width:50px"><input type="text" class="ctxt_retenido" id="txt_val_retenido_${i}"  ${propiedad_lectura} placeholder="Valor"  value="0"> </td>
                                                            <td> ${corea_del_norte[i].autorizacion} </td>
                                                            <td> ${corea_del_norte[i].indice} </td>  
                                                            <td> </td>                                                
                                                        `
                                                            ).appendTo('#tab_Informe_Revision_no tbody');                                    
            
                                        });
                                    }
            */
            
            
            
            
            
            
            
            
            
            
            
                                }
                            }
                        });
            




        }
    });
    
    

})