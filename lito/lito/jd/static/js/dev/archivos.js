/*
Template JS: SRI -  development javascript
Author: jagonzalezj
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: Form file upload Js File
*/






// FilePond
FilePond.registerPlugin(
    // encodes the file as base64 data
    FilePondPluginFileEncode,
    // validates the size of the file
    FilePondPluginFileValidateSize,
    // corrects mobile image orientation
    FilePondPluginImageExifOrientation,
    // previews dropped images
    FilePondPluginImagePreview
);





FilePond.create(
    document.querySelector('.filepond'),
    
    {
    instantUpload: true,
    server: {
        process: (fieldName, file, metadata, load, error, progress, abort, transfer, options) => {
            // fieldName is the name of the input field
            // file is the actual file object to send
            const formData = new FormData();
            formData.append(fieldName, file, file.name);

            const request = new XMLHttpRequest();
            request.open('POST', '/papeles/cargar_retenciones_contri');

            // Should call the progress method to update the progress to 100% before calling load
            // Setting computable to false switches the loading indicator to infinite mode
            request.upload.onprogress = (e) => {
                progress(e.lengthComputable, e.loaded, e.total);
            };

            // Should call the load method when done and pass the returned server file id
            // this server file id is then used later on when reverting or restoring a file
            // so your server knows which file to return without exposing that info to the client
            request.onload = function () {
                if (request.status >= 200 && request.status < 300) {
                    // the load method accepts either a string (id) or an object
                    //console.log(request.responseText);
                    //load(request.responseText);
                    let trama = JSON.parse(request.response)


                    //VALIDOS
                    if (trama.validos.length > 0){
                        let srilanka = trama.validos;         
                        $('#tbl_comprobantes_validos tbody').empty();   
                        $('#tbl_comprobantes_validos tbody').html('');                                        
                        if (srilanka.length>0){
                            $.each(srilanka, function(i, item) {
                            //for (var i=0;i<srilanka.length;i++){  
                                $('<tr  class="fila">').html(`
                                                <td> ${srilanka[i].RUC} </td>
                                                <td> ${srilanka[i].fecha_emision  }     </td>
                                                <td> ${srilanka[i].no_comprobante_venta  }     </td>
                                                <td> ${srilanka[i].valor_retenido  }     </td>
                                               `).appendTo('#tbl_comprobantes_validos tbody');
                            //}
                            });
                        }                        

                    }                          
                    //PHANTOMS
                    if (trama.phantoms.length > 0){
                        let nepal = trama.phantoms;         

                        $('#tbl_comprobantes_fantasmas tbody').empty();   
                        $('#tbl_comprobantes_fantasmas tbody').html('');                                        
                        if (nepal.length>0){
                            $.each(nepal, function(i, item) {
                                //<td> ${micronesia[i].numero_adhesivo} </td>
                                $('<tr  class="fila">').html(`
                                                <td> ${nepal[i].RUC} </td>
                                                <td> ${nepal[i].RAZON_SOCIAL  }     </td>
                                                <td> ${nepal[i].fecha_emision  }     </td>
                                                <td> ${nepal[i].no_comprobante_venta  }     </td>
                                                <td> ${nepal[i].valor_retenido  }     </td>
                                                
                                                `
                                                ).appendTo('#tbl_comprobantes_fantasmas tbody');
                            });
                        }                        

                    }                          

                    //INICIA fallecidos
                    if (trama.unreal.length > 0){
                        let noruega = trama.unreal;         

                        $('#tbl_comprobantes_fallecidos tbody').empty();   
                        $('#tbl_comprobantes_fallecidos tbody').html('');                                        
                        if (noruega.length>0){
                            $.each(noruega, function(i, item) {
                                //<td> ${micronesia[i].numero_adhesivo} </td>
                                $('<tr  class="fila">').html(`
                                                <td> ${noruega[i].RUC} </td>
                                                <td> ${noruega[i].RAZON_SOCIAL  }     </td>
                                                <td> ${noruega[i].fecha_emision  }     </td>
                                                <td> ${noruega[i].no_comprobante_venta  }     </td>
                                                <td> ${noruega[i].valor_retenido }     </td>
                                                
                                                `
                                                ).appendTo('#tbl_comprobantes_fallecidos tbody');
                            });
                        }                        
                    }                          





                    //INICIA ffpv
                    if (trama.ffpv.length > 0){
                        let suecia = trama.ffpv;         

                        $('#tbl_comprobantes_ffpv tbody').empty();   
                        $('#tbl_comprobantes_ffpv tbody').html('');                                        
                        if (suecia.length>0){
                            $.each(suecia, function(i, item) {
                                //<td> ${micronesia[i].numero_adhesivo} </td>
                                $('<tr  class="fila">').html(`
                                                <td> ${suecia[i].RUC } </td>
                                                <td> ${suecia[i].razon  }     </td>
                                                <td> ${suecia[i].fecha_emision  }     </td>
                                                <td> ${suecia[i].no_comprobante_venta  }     </td>
                                                <td> ${suecia[i].valor_retenido }     </td>
                                                
                                                `
                                                ).appendTo('#tbl_comprobantes_ffpv tbody');
                            });
                        }                        
                    }














                    //TERMINA PROC









                } else {
                    // Can call the error method if something is wrong, should exit after
                    error('oh no');
                }
            };

            request.send(formData);

            // Should expose an abort method so the request can be cancelled
            return {
                abort: () => {
                    // This function is entered if the user has tapped the cancel button
                    request.abort();

                    // Let FilePond know the request has been cancelled
                    abort();
                },
            };
        },
            },
});






//}