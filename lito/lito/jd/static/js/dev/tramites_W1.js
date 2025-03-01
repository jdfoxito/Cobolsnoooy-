
/*
+--------------------+--------------------------------------------+
| FLUJO TRAMITES     |  uso de DRAGULA                            |
|                    |                                            |
+--------------------+--------------------------------------------+
| Diciembre 2023     |V1                                          |
+--------------------+--+-----------------------------------------+
| jagonzaj  19_AB_24 |  para el flujo                             |
|                    |                                            |
+--------------------+--------------------------------------------+
*/
axios.defaults.headers.common["X-CSRFToken"] = $("#csrf_token").val();

let csrf_token = "{{ csrf_token() }}";
var productListAllData = [];
var productListPublishedData = [];
var datos_para_la_tercera = [];
var datos_para_la_cuarta = [];

//productListAllData, t)), (t = r(productListPublishedData, t)), (productListAllData = i), (productListPublishedData = 

axios.interceptors.request.use(function (config) {
    if (["post", "delete", "patch", "put"].includes(config["method"])) {
        if (csrf_token !== '') {
            config.headers["X-CSRF-Token"] = csrf_token
        }
    }
    return config;
}, function (error) {
    return Promise.reject(error);
});


const config = {
    headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'X-CSRFToken': $("#csrf_token").val()
    }
}

let USDollar = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});


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



function checkRemoveItem() {
    var e = document.querySelectorAll('a[data-bs-toggle="tab"]');
    Array.from(e).forEach(function (e) {
        e.addEventListener("show.bs.tab", function (e) {
            (isSelected = 0), (document.getElementById("selection-element").style.display = "none");
        });
    })
    setTimeout(function () {
        Array.from(document.querySelectorAll(".checkbox-product-list input")).forEach(function (e) {
            e.addEventListener("click", function (e) {
                1 == e.target.checked ? e.target.closest("tr").classList.add("gridjs-tr-selected") : e.target.closest("tr").classList.remove("gridjs-tr-selected");
                var t = document.querySelectorAll(".checkbox-product-list input:checked");
                (isSelected = t.length),
                    e.target.closest("tr").classList.contains("gridjs-tr-selected"),
                    (document.getElementById("select-content").innerHTML = isSelected),
                    (document.getElementById("selection-element").style.display = 0 < isSelected ? "block" : "none");
            });
        }),
            removeItems(),
            removeSingleItem();
    }, 100);
}

var checkboxes = document.querySelectorAll(".checkbox-wrapper-mail input");
function removeItems() {
    //document.getElementById("removeItemModal").addEventListener("show.bs.modal", function (e) {
    //   (isSelected = 0),
    //document.getElementById("delete-product").addEventListener("click", function () {
    Array.from(document.querySelectorAll(".gridjs-table tr")).forEach(function (e) {
        var t,
            i = "";
        function r(e, t) {
            return e.filter(function (e) {
                return e.id != t;
            });
        }
        //e.classList.contains("gridjs-tr-selected") &&
        //((i = r(productListAllData, t)), (t = r(productListPublishedData, t)), (productListAllData = i), (productListPublishedData = t), e.remove());

        ((i = r(productListAllData, t)), (i = r(productListPublishedData, t)), (i = r(datos_para_la_tercera, t)), (i = r(datos_para_la_cuarta, t)),

            (productListAllData = i), (productListPublishedData = i), (datos_para_la_tercera = i), (datos_para_la_cuarta = i),


            e.remove());

    });
    //document.getElementById("btn-close").click(),
    //document.getElementById("selection-element") && (document.getElementById("selection-element").style.display = "none"),
    // (checkboxes.checked = !1);
    //});
    //});
}


//var productListAllData = [];
//var productListPublishedData = [];
//var datos_para_la_tercera = [];
//var datos_para_la_cuarta = [];


function removeSingleItem() {
    var s, i;
    Array.from(document.querySelectorAll(".remove-list")).forEach(function (r) {
        r.addEventListener("click", function (e) {
            (s = r.getAttribute("data-id")),
                document.getElementById("delete-product").addEventListener("click", function () {
                    function e(e, t) {
                        return e.filter(function (e) {
                            return e.id != t;
                        });
                    }
                    var t = e(productListAllData, s) /*, i = e(productListPublishedData, s)*/;
                    (productListAllData = t), /* (productListPublishedData = i),*/ r.closest(".gridjs-tr").remove();
                });
        });
    });
    Array.from(document.querySelectorAll(".edit-list")).forEach(function (t) {
        t.addEventListener("click", function (e) {
            (i = t.getAttribute("data-edit-id")),
                (productListAllData = productListAllData.map(function (e) {
                    return e.id == i && sessionStorage.setItem("editInputValue", JSON.stringify(e)), e;
                }));
        });
    });
}


/*GRRID 1*/

var grid_uno = {};
var grid_dos = {};
var grid_tres = {};
var grid_cuatro = {};

/* FIN GRID */


/* UNO  */
function get_para_aprobar(productListAllData) {
    grid_uno =
        (
            new gridjs.Grid({
                columns: [
                    {
                        name: "CASO",
                        width: "100px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-primary">${e.id}</span>`
                            );
                        },

                    },
                    {
                        name: "Accion",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                `<button type="button" class="btn btn-soft-success waves-effect waves-light btn_caso_clase" id="btn_caso_${e.id}">${e.perfil_observador == 'Supervisor' ? 'APROBAR' : 'FINALIZAR'} </button>`
                            );
                        },
                    },
                    {
                        name: "DESCARGAR",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-shrink-0 me-3"><div class="avatar-sm bg-light rounded p-1">
                                    ${e.enlace_excel}</div>
                            </div>
                            `


                                /*  `<button type="button" class="btn btn-soft-primary waves-effect waves-light btn_caso_clase_descarga" id="btn_caso_des${e.id}">Excel </button>`*/
                            );
                        },
                    },
                    {
                        name: "CONTRIBUYENTE",
                        width: "180px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">
                                    ${e.razon_social} 
                                    </a></h5><p class="text-muted mb-0">RUC : <span class="fw-medium">
                                    ${e.contri} 
                                    </span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    { name: "FECHA_ANALISIS", width: "94px" },
                    {
                        name: "ANALISTA",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.usuario}</span>`
                            );
                        },
                        //formatter: function (e) {
                        //    return gridjs.html("$" + e);
                        //},
                    },
                    { name: "NUMERO_TRAMITE", width: "84px" },
                    {
                        name: "ESTADO",
                        width: "45px",
                        formatter: function (e) {
                            return gridjs.html('<span class="badge bg-light text-body fs-12 fw-medium"><i class="mdi mdi-star text-warning me-1"></i>' + e + "</span></td>");
                        },
                    },
                    {
                        name: "PERIODO",
                        width: "200px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge badge-soft-success">${e.periodo_inicial}</span>*` +
                                ` <span class="badge badge-label bg-success"><i class="mdi mdi-circle-medium"></i>${e.periodo_final}</span>`
                            );
                        },
                    },
                    {
                        name: "MONTOS",
                        width: "160px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">SOLICITADO: <span class="badge rounded-pill text-bg-danger">${e.snt_monto_solicitado}</span> </h5>
                                    <p class="text-muted mb-0">A DEVOLVER :  <span class="badge rounded-pill text-bg-success">${e.monto_a_devolver_calculado}</span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    {
                        name: "Atendido en:",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.resuelto_en}</span>`
                            );
                        },
                    }
                ],
                className: { th: "text-muted" },
                pagination: { limit: 10 },
                sort: !0,
                data: productListAllData,
            }).render(document.getElementById("table-product-list-all"))),
        searchProductList = document.getElementById("searchProductList"),
        slider =
        (searchProductList.addEventListener("keyup", function () {
            var e = searchProductList.value.toLowerCase();
            function t(e, t) {
                return e.filter(function (e) {
                    return -1 !== e.razon_social.toLowerCase().indexOf(t.toLowerCase());
                });
            }
            // var i = t(productListAllData, e);
            //  grid_uno.updateConfig({ data: i }).forceRender(), checkRemoveItem();
        }));

    return grid_uno;
}


function get_aprobadas(productListAllData) {
    productListAllData,
        inputValueJson = sessionStorage.getItem("inputValue"),
        editinputValueJson =
        (inputValueJson &&
            ((inputValueJson = JSON.parse(inputValueJson)),
                Array.from(inputValueJson).forEach((e) => {
                    productListAllData.unshift(e);
                })),
            sessionStorage.getItem("editInputValue")),
        productListAll_grid2 =
        (editinputValueJson &&
            ((editinputValueJson = JSON.parse(editinputValueJson)),
                (productListAllData = productListAllData.map(function (e) {
                    return e.id == editinputValueJson.id ? editinputValueJson : e;
                }))),
            new gridjs.Grid({
                columns: [
                    {
                        name: "CONTRIBUYENTE",
                        width: "180px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">
                                    ${e.razon_social} 
                                    </a></h5><p class="text-muted mb-0">RUC : <span class="fw-medium">
                                    ${e.contri} 
                                    </span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    {
                        name: "DESCARGAR",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-shrink-0 me-3"><div class="avatar-sm bg-light rounded p-1">
                                    ${e.enlace_excel}</div>
                            </div>
                            `


                                /*  `<button type="button" class="btn btn-soft-primary waves-effect waves-light btn_caso_clase_descarga" id="btn_caso_des${e.id}">Excel </button>`*/
                            );
                        },
                    },
                    { name: "FECHA_ANALISIS", width: "94px" },
                    {
                        name: "ANALISTA",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.usuario}</span>`
                            );
                        },
                        //formatter: function (e) {
                        //    return gridjs.html("$" + e);
                        //},
                    },
                    { name: "NUMERO_TRAMITE", width: "84px" },
                    {
                        name: "ESTADO",
                        width: "45px",
                        formatter: function (e) {
                            return gridjs.html('<span class="badge bg-light text-body fs-12 fw-medium"><i class="mdi mdi-star text-warning me-1"></i>' + e + "</span></td>");
                        },
                    },
                    {
                        name: "PERIODO",
                        width: "200px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge badge-soft-success">${e.periodo_inicial}</span>*` +
                                ` <span class="badge badge-label bg-success"><i class="mdi mdi-circle-medium"></i>${e.periodo_final}</span>`
                            );
                        },
                    },
                    {
                        name: "MONTOS",
                        width: "160px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">SOLICITADO: <span class="badge rounded-pill text-bg-danger">${e.snt_monto_solicitado}</span> </h5>
                                    <p class="text-muted mb-0">A DEVOLVER :  <span class="badge rounded-pill text-bg-success">${e.monto_a_devolver_calculado}</span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    {
                        name: "Atendido en:",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.resuelto_en}</span>`
                            );
                        },
                    },
                ],
                className: { th: "text-muted" },
                pagination: { limit: 10 },
                sort: !0,
                data: productListAllData,
            }).render(document.getElementById("table-product-list-published"))),
        searchProductList = document.getElementById("searchProductList"),
        slider =
        (searchProductList.addEventListener("keyup", function () {
            var e = searchProductList.value.toLowerCase();
            function t(e, t) {
                return e.filter(function (e) {
                    return -1 !== e.razon_social.toLowerCase().indexOf(t.toLowerCase());
                });
            }
            //var i = t(productListAllData, e);
            //productListAll_grid2.updateConfig({ data: i }).forceRender(), checkRemoveItem();
        }));

    return productListAll_grid2
}

/* la pestanha tres  */
function get_pestana_tres(productListAllData) {
    productListAllData,
        inputValueJson = sessionStorage.getItem("inputValue"),
        editinputValueJson =
        (inputValueJson &&
            ((inputValueJson = JSON.parse(inputValueJson)),
                Array.from(inputValueJson).forEach((e) => {
                    productListAllData.unshift(e);
                })),
            sessionStorage.getItem("editInputValue")),
        grid_tres =
        (editinputValueJson &&
            ((editinputValueJson = JSON.parse(editinputValueJson)),
                (productListAllData = productListAllData.map(function (e) {
                    return e.id == editinputValueJson.id ? editinputValueJson : e;
                }))),
            new gridjs.Grid({
                columns: [
                    {
                        name: "CASO",
                        width: "100px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-primary">${e.id}</span>`
                            );
                        },

                    },
                    {
                        name: "Accion",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                `<button type="button" class="btn btn-soft-success waves-effect waves-light btn_caso_clase_3ra" id="btn_caso_${e.id}">${e.perfil_observador == 'Supervisor' ? 'REVIVIR' : 'BORRAR'} </button>`
                            );
                        },
                    },
                    {
                        name: "DESCARGAR",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-shrink-0 me-3"><div class="avatar-sm bg-light rounded p-1">
                                    ${e.enlace_excel}</div>
                            </div>
                            `
                                /*  `<button type="button" class="btn btn-soft-primary waves-effect waves-light btn_caso_clase_descarga" id="btn_caso_des${e.id}">Excel </button>`*/
                            );
                        },
                    },
                    {
                        name: "CONTRIBUYENTE",
                        width: "180px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">
                                    ${e.razon_social} 
                                    </a></h5><p class="text-muted mb-0">RUC : <span class="fw-medium">
                                    ${e.contri} 
                                    </span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    { name: "FECHA_ANALISIS", width: "94px" },
                    {
                        name: "ANALISTA",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.usuario}</span>`
                            );
                        },
                        //formatter: function (e) {
                        //    return gridjs.html("$" + e);
                        //},
                    },
                    { name: "NUMERO_TRAMITE", width: "84px" },
                    {
                        name: "ESTADO",
                        width: "45px",
                        formatter: function (e) {
                            return gridjs.html('<span class="badge bg-light text-body fs-12 fw-medium"><i class="mdi mdi-star text-warning me-1"></i>' + e + "</span></td>");
                        },
                    },
                    {
                        name: "PERIODO",
                        width: "200px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge badge-soft-success">${e.periodo_inicial}</span>*` +
                                ` <span class="badge badge-label bg-success"><i class="mdi mdi-circle-medium"></i>${e.periodo_final}</span>`
                            );
                        },
                    },
                    {
                        name: "MONTOS",
                        width: "160px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">SOLICITADO: <span class="badge rounded-pill text-bg-danger">${e.snt_monto_solicitado}</span> </h5>
                                    <p class="text-muted mb-0">A DEVOLVER :  <span class="badge rounded-pill text-bg-success">${e.monto_a_devolver_calculado}</span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    {
                        name: "Atendido en:",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.resuelto_en}</span>`
                            );
                        },
                    }
                ],
                className: { th: "text-muted" },
                pagination: { limit: 10 },
                sort: !0,
                data: productListAllData,
            }).render(document.getElementById("tabla_pestanhatres"))),
        searchProductList = document.getElementById("searchProductList"),
        slider =
        (searchProductList.addEventListener("keyup", function () {
            var e = searchProductList.value.toLowerCase();
            function t(e, t) {
                return e.filter(function (e) {
                    return -1 !== e.razon_social.toLowerCase().indexOf(t.toLowerCase());
                });
            }
            //  var i = t(productListAllData, e);
            //  grid_tres.updateConfig({ data: i }).forceRender(), checkRemoveItem();
        }));
    return grid_tres

}

/* la pestanha cuatro  */
function get_pestana_cuatro(productListAllData) {
    productListAllData,
        inputValueJson = sessionStorage.getItem("inputValue"),
        editinputValueJson =
        (inputValueJson &&
            ((inputValueJson = JSON.parse(inputValueJson)),
                Array.from(inputValueJson).forEach((e) => {
                    productListAllData.unshift(e);
                })),
            sessionStorage.getItem("editInputValue")),
        grid_cuatro =
        (editinputValueJson &&
            ((editinputValueJson = JSON.parse(editinputValueJson)),
                (productListAllData = productListAllData.map(function (e) {
                    return e.id == editinputValueJson.id ? editinputValueJson : e;
                }))),
            new gridjs.Grid({
                columns: [
                    {
                        name: "CASO",
                        width: "100px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-primary">${e.id}</span>`
                            );
                        },

                    },
                    {
                        name: "Accion",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                //`<button type="button" class="btn btn-soft-success waves-effect waves-light btn_caso_clase_3ra" id="btn_caso_${e.id}">${  e.perfil_observador == 'Supervisor' ? 'REVIVIR' : 'BORRAR' } </button>`
                                `<p></sp>`
                            );
                        },
                    },
                    {
                        name: "DESCARGAR",
                        width: "100px",
                        sort: { enabled: !1 },
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-shrink-0 me-3"><div class="avatar-sm bg-light rounded p-1">
                                    ${e.enlace_excel}</div>
                            </div>
                            `
                                /*  `<button type="button" class="btn btn-soft-primary waves-effect waves-light btn_caso_clase_descarga" id="btn_caso_des${e.id}">Excel </button>`*/
                            );
                        },
                    },
                    {
                        name: "CONTRIBUYENTE",
                        width: "180px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">
                                    ${e.razon_social} 
                                    </a></h5><p class="text-muted mb-0">RUC : <span class="fw-medium">
                                    ${e.contri} 
                                    </span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    { name: "FECHA_ANALISIS", width: "94px" },
                    {
                        name: "ANALISTA",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.usuario}</span>`
                            );
                        },
                        //formatter: function (e) {
                        //    return gridjs.html("$" + e);
                        //},
                    },
                    { name: "NUMERO_TRAMITE", width: "84px" },
                    {
                        name: "ESTADO",
                        width: "45px",
                        formatter: function (e) {
                            return gridjs.html('<span class="badge bg-light text-body fs-12 fw-medium"><i class="mdi mdi-star text-warning me-1"></i>' + e + "</span></td>");
                        },
                    },
                    {
                        name: "PERIODO",
                        width: "200px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge badge-soft-success">${e.periodo_inicial}</span>*` +
                                ` <span class="badge badge-label bg-success"><i class="mdi mdi-circle-medium"></i>${e.periodo_final}</span>`
                            );
                        },
                    },
                    {
                        name: "MONTOS",
                        width: "160px",
                        data: function (e) {
                            return gridjs.html(
                                `<div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h5 class="fs-14 mb-1">SOLICITADO: <span class="badge rounded-pill text-bg-danger">${e.snt_monto_solicitado}</span> </h5>
                                    <p class="text-muted mb-0">A DEVOLVER :  <span class="badge rounded-pill text-bg-success">${e.monto_a_devolver_calculado}</span></p>
                                    </div>
                            </div>`
                            );
                        },
                    },
                    {
                        name: "Atendido en:",
                        width: "80px",
                        data: function (e) {
                            return gridjs.html(`<span class="badge rounded-pill badge-outline-secondary">${e.resuelto_en}</span>`
                            );
                        },
                    }
                ],
                className: { th: "text-muted" },
                pagination: { limit: 10 },
                sort: !0,
                data: productListAllData,
            }).render(document.getElementById("tabla_pestanhacuatro"))),
        searchProductList = document.getElementById("searchProductList"),
        slider =
        (searchProductList.addEventListener("keyup", function () {
            var e = searchProductList.value.toLowerCase();
            function t(e, t) {
                return e.filter(function (e) {
                    return -1 !== e.razon_social.toLowerCase().indexOf(t.toLowerCase());
                });
            }
            var i = t(productListAllData, e);
            grid_cuatro.updateConfig({ data: i }).forceRender(), checkRemoveItem();
        }));
    return grid_cuatro

}


$(document).ready(function () {


    //let productListAllData = []
    const usx = $("#csrf_user").val();
    const acx = $("#in_xyz").val().trim();

    document.getElementById("tabla_pestanhatres").addEventListener("show.bs.modal", function (e) {
        if (e.relatedTarget.classList.contains("edit-item-btn")) {
            document.getElementById("exampleModalLabel").innerHTML = "Editar Tramite 204";
            document.getElementById("tabla_pestanhatres").querySelector(".modal-footer").style.display = "block";
            document.getElementById("add-btn").style.display = "none";
            document.getElementById("edit-btn").style.display = "block";
        } else if (e.relatedTarget.classList.contains("add-btn")) {
            document.getElementById("modal-id").style.display = "none";
            document.getElementById("exampleModalLabel").innerHTML = "Add Order";
            document.getElementById("tabla_pestanhatres").querySelector(".modal-footer").style.display = "block";
            document.getElementById("edit-btn").style.display = "none";
            document.getElementById("add-btn").style.display = "block";
        } else {
            document.getElementById("exampleModalLabel").innerHTML = "List Order";
            document.getElementById("tabla_pestanhatres").querySelector(".modal-footer").style.display = "none";
        }
    });
    // ischeckboxcheck();

    document.getElementById("tabla_pestanhatres").addEventListener("hidden.bs.modal", function () {
        clearFields();
    });


    axios(`get_df/0/${usx}/${acx}`).then(function (volcados) {

        if (volcados.data.valida !== undefined) {
            if (parseInt(volcados.data.valida) == -100) {
                window.location = "/account/login";
            }
        } else {

            if (volcados.data) {
                $("#a_link_pestanha_uno").html('0')
                $("#a_link_pestanha_dos").html('0')
                $("#a_link_pestanha_tres").html('0')
                $("#a_link_pestanha_cuatro").html('0')
                //if (volcados.data.volca_ina.length>0){
                productListAllData = volcados.data.volca_ina;
                $("#a_link_pestanha_uno").html(productListAllData.length)
                grid_uno = get_para_aprobar(productListAllData);
                //}
                //if (volcados.data.volca_apr.length>0){
                productListPublishedData = volcados.data.volca_apr;
                grid_dos = get_aprobadas(productListPublishedData);
                $("#a_link_pestanha_dos").html(productListPublishedData.length)
                //}
                //if (volcados.data.volca_tercera.length>0){
                datos_para_la_tercera = volcados.data.volca_tercera;
                grid_tres = get_pestana_tres(datos_para_la_tercera);
                $("#a_link_pestanha_tres").html(datos_para_la_tercera.length)
                //}

                datos_para_la_cuarta = volcados.data.volca_cuarta;
                grid_cuatro = get_pestana_cuatro(datos_para_la_cuarta);
                $("#a_link_pestanha_cuatro").html(datos_para_la_cuarta.length)

                $("#div_supervisores").html('');
                if (volcados.data) {
                    let texto = '';
                    supervision = volcados.data.df_supervisores
                    if (supervision) {
                        if (supervision.length > 0) {
                            texto += `<li><p>Listado de Supervisores</p></li>`
                            $.each(supervision, function (i, item) {
                                texto += `<li> <div class="alert alert-info alert-dismissible alert-label-icon rounded-label fade show" role="alert">
                                        <i class="ri-airplay-line label-icon"></i><strong>${i} - ${item.nombre}</strong> 
                                    </div>
                                </li>`
                            });

                            let lista = $("#div_supervisores").append('<ul></ul>').find('ul');
                            lista.append(texto);
                        }
                    }
                }
            }
        }
    });





    $("#table-product-list-all").on('click', '.btn_caso_clase', function () {
        let currentRow = $(this).closest("tr");
        let caso = currentRow.find("td:eq(0)").text()
        $("#inp_caso_seleccionado").val(caso);
        let caso_txt = caso.toString().padStart(10, '0');
        $("#modalabel_caso").empty()
        $("#modalabel_caso").html("CASO : " + caso_txt)
        const usx = $("#csrf_user").val().trim();
        const acx = $("#in_xyz").val().trim();
        axios(`get_df/${caso}/${usx}/${acx}`).then(function (volcados) {
            if (volcados.data.valida !== undefined) {
                if (parseInt(volcados.data.valida) == -100) {
                    window.location = "/account/login";
                }
            } else {
                if (volcados.data) {
                    if (volcados.data.df_sin_grupos.length > 0) {
                        let poland = volcados.data.df_sin_grupos;
                        $.each(poland, function (i, item) {
                            $("#spa_txt_fecha_analisis").html(" ingresado en el sistema SNT en la fecha :" + item.snt_fecha_ingreso);

                            $("#spa_txt_contri_name").html(item.razon_social)
                            $("#spa_txt_contri_desde").html(item.periodo_inicial)
                            $("#spa_txt_contri_tramite").html(item.numero_tramite)
                            $("#spa_txt_analista").html(item.usuario)
                            $("#spa_txt_supervisor").html(item.supervisor_marca)
                            $("#spa_txt_inicia").html(item.time_inicia)
                            $("#spa_txt_resuelto_en").html(item.resuelto_en)
                            $("#spa_txt_monto_excel").html(USDollar.format(item.monto_excel_identificado))
                            $("#spa_txt_monto_solicitado").html(USDollar.format(item.snt_monto_solicitado))

                            $("#spa_txt_contri_ruc").html(item.contri)
                            $("#spa_txt_contri_hasta").html(item.periodo_final)
                            $("#spa_txt_snt_ingresado").html(item.snt_fecha_ingreso)
                            $("#spa_txt_analista_nombre").html(item.nombre_analista)
                            $("#spa_txt_supervisor_nombre").html(item.nombre_supervisor == '' || item.nombre_supervisor === null ? '[POR DEFIINIR]' : item.nombre_supervisor
                                + `( <small class="text-success">${item.time_actualiza_memoria} </small> )`)
                            $("#spa_txt_finaliza").html(item.time_graba_memoria)
                            $("#spa_txt_filas_listado").html(item.num_excel_filas)

                            $("#spa_txt_num_providencias").html(item.num_providencias)
                            $("#spa_txt_devuelto").html(USDollar.format(item.monto_a_devolver_calculado))
                        });
                    }
                }
            }
        });
        let galleryModal = new bootstrap.Modal(document.getElementById('modal_tramites'), {
            keyboard: false
        });
        galleryModal.show();

    });



    $("#tabla_pestanhatres").on('click', '.btn_caso_clase_3ra', function () {
        let currentRow = $(this).closest("tr");
        let caso = currentRow.find("td:eq(0)").text()
        $("#inp_caso_seleccionado_3ra").val(caso);
        let caso_txt = caso.toString().padStart(10, '0');
        $("#modalabel_caso_3ra").empty()
        $("#modalabel_caso_3ra").html("CASO : " + caso_txt)
        const usx = $("#csrf_user").val();
        const acx = $("#in_xyz").val();
        axios(`get_df/${caso}/${usx}/${acx}`).then(function (volcados) {
            if (volcados.data.valida !== undefined) {
                if (parseInt(volcados.data.valida) == -100) {
                    window.location = "/account/login";
                }
            } else {

                if (volcados.data) {
                    if (volcados.data.df_sin_grupos.length > 0) {
                        poland = volcados.data.df_sin_grupos;
                        $.each(poland, function (i, item) {
                            $("#spa_txt_fecha_analisis_3ra").html(" analizado en :" + item.snt_fecha_ingreso);

                            $("#spa_txt_contri_name_3ra").html(item.razon_social)
                            $("#spa_txt_contri_desde_3ra").html(item.periodo_inicial)
                            $("#spa_txt_contri_tramite_3ra").html(item.numero_tramite)
                            $("#spa_txt_analista_3ra").html(item.usuario)
                            $("#spa_txt_supervisor_3ra").html(item.supervisor_marca)
                            $("#spa_txt_inicia_3ra").html(item.time_inicia)
                            $("#spa_txt_resuelto_en_3ra").html(item.resuelto_en)
                            $("#spa_txt_monto_excel_3ra").html(USDollar.format(item.monto_excel_identificado))
                            $("#spa_txt_monto_solicitado_3ra").html(USDollar.format(item.snt_monto_solicitado))

                            $("#spa_txt_contri_ruc_3ra").html(item.contri)
                            $("#spa_txt_contri_hasta_3ra").html(item.periodo_final)
                            $("#spa_txt_snt_ingresado_3ra").html(item.snt_fecha_ingreso)
                            $("#spa_txt_analista_nombre_3ra").html(item.nombre_analista)
                            $("#spa_txt_supervisor_nombre_3ra").html(item.nombre_supervisor == '' || item.nombre_supervisor === null ? '[POR DEFIINIR]' : item.nombre_supervisor)
                            $("#spa_txt_finaliza_3ra").html(item.time_graba_memoria)
                            $("#spa_txt_filas_listado_3ra").html(item.num_excel_filas)

                            $("#spa_txt_num_providencias_3ra").html(item.num_providencias)
                            $("#spa_txt_devuelto_3ra").html(USDollar.format(item.monto_a_devolver_calculado))
                        });
                    }

                }

            }

        });


        let galleryModal = new bootstrap.Modal(document.getElementById('modal_tramites_3ra'), {
            keyboard: false
        });


        galleryModal.show();

    });




    function get_recarga_cero() {
        const usx = $("#csrf_user").val();
        const acx = $("#in_xyz").val().trim();
        axios(`get_df/0/${usx}/${acx}`).then(function (volcados) {

            if (volcados.data.valida !== undefined) {
                if (parseInt(volcados.data.valida) == -100) {
                    window.location = "/account/login";
                }
            } else {

                if (volcados.data) {
                    $("#a_link_pestanha_uno").html('0')
                    $("#a_link_pestanha_dos").html('0')
                    $("#a_link_pestanha_tres").html('0')
                    $("#a_link_pestanha_cuatro").html('0')
                    productListAllData = volcados.data.volca_ina;
                    $("#a_link_pestanha_uno").html(productListAllData.length)

                    productListPublishedData = volcados.data.volca_apr;
                    $("#a_link_pestanha_dos").html(productListPublishedData.length)

                    datos_para_la_tercera = volcados.data.volca_tercera;
                    $("#a_link_pestanha_tres").html(datos_para_la_tercera.length)


                    datos_para_la_cuarta = volcados.data.volca_cuarta;
                    $("#a_link_pestanha_cuatro").html(datos_para_la_cuarta.length)


                    grid_uno.updateConfig({
                        data: productListAllData
                    }).forceRender();
                    grid_dos.updateConfig({
                        data: productListPublishedData
                    }).forceRender();
                    grid_tres.updateConfig({
                        data: datos_para_la_tercera
                    }).forceRender();
                    grid_cuatro.updateConfig({
                        data: datos_para_la_cuarta
                    }).forceRender();




                }

            }
        });

    }


    $("#btn_aprobar_caso").click(function () {
        let caso = $("#inp_caso_seleccionado").val();
        const requesta = {
            expediente: 9999,
            memoria: caso,
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val().trim()
        }
        axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
            .then(function (resultadoD) {
                if (parseInt(resultadoD.data.valida) == -100) {
                    window.location = "/account/login";
                } else {
                    get_recarga_cero();
                }
            });

        $('.close').click();
        $('#modal_tramites').fadeOut();

    });

    $("#btn_devolver_caso").click(function () {
        let caso = $("#inp_caso_seleccionado").val();
        const requesta = {
            expediente: 9997,
            memoria: caso,
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val().trim()
        }
        axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
            .then(function (resultadoD) {
                if (parseInt(resultadoD.data.valida) == -100) {
                    window.location = "/account/login";
                } else {
                    get_recarga_cero();
                }
            });

        $('.close').click();
        $('#modal_tramites').fadeOut();

    });



    $("#btn_aprobar_caso_3ra").click(function () {
        let caso = $("#inp_caso_seleccionado_3ra").val();
        const requesta = {
            expediente: 9998,
            memoria: caso,
            usuario: $("#csrf_user").val(),
            mu: $("#in_xyz").val()
        }
        axios.post(`upd_anywhere`, JSON.stringify(requesta), config)
            .then(function (resultadoD) {
                if (parseInt(resultadoD.data.valida) == -100) {
                    window.location = "/account/login";
                } else {
                    get_recarga_cero();
                }

            });

        $('.close').click();
        $('#modal_tramites').fadeOut();

    });



});