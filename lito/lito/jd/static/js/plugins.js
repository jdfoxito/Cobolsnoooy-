/*
Template JS: SRI -  development javascript
Author: jagonzalezj
Version: 2.0.0
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: Common Plugins Js File
*/

//Common plugins
if (document.querySelectorAll("[toast-list]") || document.querySelectorAll('[data-choices]') || document.querySelectorAll("[data-provider]")) {
  /*document.writeln("<script type='text/javascript' src='/static/js/toastify-js.js'></script>");*/
  document.writeln("<script type='text/javascript' src='/static/libs/choices.js/public/assets/scripts/choices.min.js'></script>");
  document.writeln("<script type='text/javascript' src='/static/libs/flatpickr/flatpickr.min.js'></script>");


}