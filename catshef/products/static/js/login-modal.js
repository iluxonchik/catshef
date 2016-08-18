/* MODAL SETTINGS */
var SAME_URL_AFTER_REG = true; // prevent redirect after successful Registration (if set to true, the page will simply reload, i.e. the user will remain on the same url)
var SAME_URL_AFTER_LOGIN = true; // prevent redirect after successful Login (if set to true, the page will simply reload, i.e. the user will remain on the same url)

/**
* Shows the modal form error div
*/
function showModalErrorDiv() {
    return $('.error').addClass('alert alert-danger');
}

function hideModalErrorDiv() {
    $('.error').removeClass('alert alert-danger').html(''); 
}

/**
* Generates Bootrstap error label
*/
function makeErrorLabel(name, msg) {
    return '<label class="control-label" for="id_' + name + '">' + msg + '</label>'
}

/**
* Sets the errors of a field
*/
function setFieldErrors(name, msg) {
    if (name === '__all__') {
        // form error
        showModalErrorDiv().html(msg);
    } else {
        // field error
        $('#' + name + '-error-div').html(msg);
    }
    console.log('setFieldErrors {"' + name + '":" ' + msg + ' "}');
}

/**
* Clears all field errors. If fields are added/removed/renamed in the future,
* 'field_names' should be altered.
*/
function clearPreviousFieldErrors() {
    // NOTE: '__all__' refers to the form levels
    var field_names = ['__all__', 'name', 'email', 'phone', 'password1', 'password2']
    field_names.forEach(function(name) {
        setFieldErrors(name, '');
    });
    hideModalErrorDiv();
}

function showRegisterForm(){
    $('.loginBox').fadeOut('fast',function(){
        $('.registerBox').fadeIn('fast');
        $('.login-footer').fadeOut('fast',function(){
            $('.register-footer').fadeIn('fast');
        });
        $('.modal-title').html('Register with');
    }); 
    $('.error').removeClass('alert alert-danger').html('');

}

function showLoginForm(){
    $('#login-modal .registerBox').fadeOut('fast',function(){
        $('.loginBox').fadeIn('fast');
        $('.register-footer').fadeOut('fast',function(){
            $('.login-footer').fadeIn('fast');    
        });
        $('.modal-title').html('Login with');
    });       
    hideModalErrorDiv();
}

function openLoginModal(){
    showLoginForm();
    setTimeout(function(){
        $('#login-modal').modal('show');    
    }, 230);
    
}

function openRegisterModal(){
    showRegisterForm();
    setTimeout(function(){
        $('#login-modal').modal('show');    
    }, 230);
    
}

function loginAjax(){
    $.post(
        '/account/login/',
        $('#modal-login-form').serialize()
        ).done(function(data, textStatus, jqXHR) {
        // TODO: notify user of successful login
        // NOTE: use available signals, this shouldn't be done here.
        if (!SAME_URL_AFTER_LOGIN) {
            if (data['location']) {
                window.location.href = data['location']
            } else {
                // if no redirect url provided, simply reload the current page
                location.reload();
            }
        } else {
            location.reload();
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        // yep, as simple as that
        shakeModal();
    });
}

function shakeModal(){
    $('#login-modal .modal-dialog').addClass('shake');
    showModalErrorDiv().html("Invalid email/password combination");
    $('input[type="password"]').val('');
    setTimeout( function(){ 
        $('#login-modal .modal-dialog').removeClass('shake'); 
    }, 1000 ); 
}

function registerAjax() {
    $.post(
        '/account/signup/',
        $('#modal-register-form').serialize()
        ).done(function(data, textStatus, jqXHR) {
        // TODO: notify user of successful login
        // NOTE: use available signals, this shouldn't be done here.
        if (!SAME_URL_AFTER_REG) {
            if (data['location']) {
                window.location.href = data['location']
            } else {
                // if no redirect url provided, simply reload the current page
                location.reload();
            }
        } else {
            location.reload();
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        var form_errors = jqXHR.responseJSON.form_errors
        var error_msgs = []

        if (form_errors) {
            clearPreviousFieldErrors();
            for (var key in form_errors) {
                field_errors = ''
                form_errors[key].forEach(function (msg) {
                    field_errors += makeErrorLabel(key, msg);
                    setFieldErrors(key, field_errors);
                });
            }
        }
    });
}
