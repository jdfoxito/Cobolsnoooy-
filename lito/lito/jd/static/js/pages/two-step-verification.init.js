/*
Template JS: SRI -  development javascript
Author: jagonzalezj
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: Two step verification Init Js File
*/

// move next
function moveToNext(elem, count) {
    if (elem.value.length > 0) {
        document.getElementById("digit" + count + "-input").focus();
    }
}