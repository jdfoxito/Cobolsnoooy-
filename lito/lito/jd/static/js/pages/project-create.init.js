/*
Template JS: SRI -  development javascript
Author: jagonzalezj
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: Project create init js
*/

// ckeditor
var ckeditorClassic = document.querySelector('#ckeditor-classic');
if (ckeditorClassic) {
    ClassicEditor
        .create(document.querySelector('#ckeditor-classic'))
        .then(function (editor) {
            editor.ui.view.editable.element.style.height = '200px';
        })
        .catch(function (error) {
            console.error(error);
        });
}

// Dropzone
var dropzonePreviewNode = document.querySelector("#dropzone-preview-list");
if (dropzonePreviewNode) {
    dropzonePreviewNode.id = "";
    var previewTemplate = dropzonePreviewNode.parentNode.innerHTML;
    dropzonePreviewNode.parentNode.removeChild(dropzonePreviewNode);
    var dropzone = new Dropzone(".dropzone", {
        url: 'https://httpbin.org/post',
        method: "post",
        previewTemplate: previewTemplate,
        previewsContainer: "#dropzone-preview",
    });

}