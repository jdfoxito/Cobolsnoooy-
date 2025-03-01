/*
Template JS: SRI -  development javascript
Author: jagonzalezj
WebSite: https://www.sri.gob.ec
Contact: jagonzalezj@sri.gob.ec
File: Password addon Js File
*/


// password addon
Array.from(document.querySelectorAll("form .auth-pass-inputgroup")).forEach(function (item) {
    Array.from(item.querySelectorAll(".password-addon")).forEach(function (subitem) {
            subitem.addEventListener("click", function (event) {
                let passwordInput = item.querySelector(".password-input");
                if (passwordInput.type === "password") {
                    passwordInput.type = "text";
                } else {
                    passwordInput.type = "password";
                }
            });
        });
    });

// passowrd match


function validatePassword() {
    let password = document.getElementById("password-input"),
    confirm_password = document.getElementById("confirm-password-input");    
    console.log(password.value)
    console.log(confirm_password.value)
    if (password.value.toString().trim() !== confirm_password.value.toString().trim()) {
        confirm_password.setCustomValidity("Los passwords no coinciden");
    } else {

        confirm_password.setCustomValidity("");
        //document.getElementById("password-input").value = password.value.toString().trim()
        $("#txt_pass").val(document.getElementById("password-input").value);
        $("#txt_pass_confirma").val(document.getElementById("confirm-password-input").value);
    }
}

//Password validation


let myInput = document.getElementById("confirm-password-input");
let letter = document.getElementById("pass-lower");
let capital = document.getElementById("pass-upper");
let number = document.getElementById("pass-number");
let length = document.getElementById("pass-length");

// When the user clicks on the password field, show the message box
myInput.onfocus = function () {
    document.getElementById("password-contain").style.display = "block";
};

// When the user clicks outside of the password field, hide the password-contain box
myInput.onblur = function () {
    document.getElementById("password-contain").style.display = "none";
};

// When the user starts to type something inside the password field
myInput.onkeyup = function () {
    // Validate lowercase letters
    let lowerCaseLetters = /[a-z]/g;
    if (myInput.value.match(lowerCaseLetters)) {
        letter.classList.remove("invalid");
        letter.classList.add("valid");
    } else {
        letter.classList.remove("valid");
        letter.classList.add("invalid");
    }

    // Validate capital letters
    let upperCaseLetters = /[A-Z]/g;
    if (myInput.value.match(upperCaseLetters)) {
        capital.classList.remove("invalid");
        capital.classList.add("valid");
    } else {
        capital.classList.remove("valid");
        capital.classList.add("invalid");
    }

    // Validate numbers
    let numbers = /[0-9]/g;
    if (myInput.value.match(numbers)) {
        number.classList.remove("invalid");
        number.classList.add("valid");
    } else {
        number.classList.remove("valid");
        number.classList.add("invalid");
    }

    // Validate length
    if (myInput.value.length >= 8) {
        length.classList.remove("invalid");
        length.classList.add("valid");
    } else {
        length.classList.remove("valid");
        length.classList.add("invalid");
    }

    validatePassword();

};

/*
$(document).ready(function() {
    
    $('#frm_cambio_clave').submit(function(event) {

    console.log($('#password-input').val());
    console.log($('#conifrm-password-input').val(''));
   
      
      event.preventDefault();
       $.ajax({
          type: 'POST',
          url: '/authentication/auth-pass-change-basic',
          data: $('#frm_cambio_clave').serialize(),
          data:{
            "p":$('#password-input').val(),
            "rp":$('#confirm-password-input').val()
         },

          success: function() {
            
          }
       });
    });
 });

 */