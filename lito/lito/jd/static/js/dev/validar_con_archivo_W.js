
/*
+--------------------+--------------------------------------------+
| carga de archivo   |  ARCHIVOS                                  |
|                    |                                            |
+--------------------+--------------------------------------------+
| Diciembre 2023     |V1                                          |
+--------------------+--+-----------------------------------------+
| jagonzaj  19_AB_24 |  usando filepond                           |
|                    |                                            |
+--------------------+--------------------------------------------+
*/
/*
Template JS: SRI -  development javascript
Author: jagonzalezj
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: Form file upload Js File
*/
FilePond.registerPlugin(
    FilePondPluginFileEncode,
    FilePondPluginFileValidateSize,
    FilePondPluginImageExifOrientation,
    FilePondPluginImagePreview
);

FilePond.create(
    document.querySelector('.filepond'),
    {
    instantUpload: true,
    chunkUploads: true,
    chunkSize: 1024 * 1024 * 50, // 50MB
    chunkRetryDelays: [],
    maxFileSize: 1024 * 1024 * 1024, // 1 GB
    server: {
        process: (fieldName, file, metadata, load, error, progress, abort, transfer, options) => {
            reiniciar_tablas();
            const tparam1 = $("#txt_ruc_ingresado").val();
    
            if (!isdigito(tparam1)){
                mensaje("error","El campo RUC debe ser un valor numeríco")
                abort();
                $('#txt_ruc_ingresado').trigger('focus');
                return;
            }

            if ( [10].includes(tparam1.length ) )  {
                mensaje("error","Ingrese un número de RUC ")
                abort();
                return;
            }                    
    
            if ( ![13].includes(tparam1.length ) )  {
                mensaje("error","El campo RUC debe tener 13 dígitos")
                abort();
                return;
            }                    
    

            let periodo1 = $("#txt_desde").val();
            let periodo2 = $("#txt_hasta").val();

            if ( periodo1.length === 0 &&  periodo2.length === 0  )  {
                mensaje("error","Debe ingresar el periodo para validar declaraciones ! ")
                abort();
                return;
            }
            
            let val_txt_desde = Date.parse($("#txt_desde").val());
            let val_txt_hasta = Date.parse($("#txt_hasta").val());
        
            if (!isNaN(val_txt_desde) && !isNaN(val_txt_hasta) ) {
                periodo1 = periodo1 + '-01';
                periodo2 = periodo2 + '-27';
            }else{
                mensaje("error","Las fechas de los periodos no contienen un periodo valido ! ")
                abort();
                return;
            }   
            if (!fun_rango_fecha(periodo1, periodo2)){
                abort();
                return;
            }
            const formData = new FormData();
            formData.append(fieldName, file, file.name);
            const requesta = {
                param1: tparam1,
                param2: periodo1,
                param3: periodo2,
                param4: 'F',
                param5: '',
                usuario: $("#csrf_user").val(),
                mu: $("#in_xyz").val()  
            }
            loading(true); 
            const request = new XMLHttpRequest();
            request.open('POST', `/papeles/cargar_retenciones_ini?ufx=${JSON.stringify(requesta)}`);
            request.upload.onprogress = (e) => {
                progress(e.lengthComputable, e.loaded, e.total);
            };
            request.onload = function () {
                if (request.status >= 200 && request.status < 300) {
                    let trama = JSON.parse(request.response)
                    $('#div_novedades').empty();
                    $('#div_novedades').html('');           
                    let l1= 1;
                    if (trama.hasOwnProperty('valida')) {
                        l1= parseInt(trama.valida);
                    }
                    if (trama.stop == -100  || l1 ==-100 ){
                        mensaje("error","Reingrese al sistema nuevamente!")
                        window.location = "/account/login"; 
                    }
                    if (!trama.stop){
                        $('#div_todos_tabs').show();   
                        $('#div_barra_menu').show(); 
                        verificartramites(requesta);
                        $('#ul_fox a[href="#papel-contri"]').tab('show');    
                        $('#ul_fox a[href="#li_a_tab_contri"]').tab('show'); 
                        $("#li_a_tab_contri").show();                       

                    }else{
                        fun_novedades(trama.novedades);    
                    }
                } else {
                    mensaje("error","El archivo no ha podido ser cargado!")
                }
                loading(false); 
            };
            request.send(formData);
            return {
                abort: () => {
                    request.abort();
                    abort();
                },
            };
        },
        
        headers: {
            'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content'),
        }
    },
});
