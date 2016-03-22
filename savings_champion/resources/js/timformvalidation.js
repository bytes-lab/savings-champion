$(document).ready(function () {
    jQuery.extend(jQuery.validator.messages, {
        maxlength: jQuery.validator.format("{0} characters maximum please"),
        required: "",
        min: "",
        email: {
            remote: "You have already subscribed"

        }
    });

    jQuery.validator.setDefaults({
        errorPlacement: function (error, element) {
            if (element.attr("id") == 'id_email') { // match your element's id
                if (error.html() == "A user exists with this email") {
                    error.appendTo(element.parent()); // this line willchange depends on your form layout
                }
            }
            else {

            }
        }
    });

    $.validator.addMethod('commaNumber', function (value) {
        return /\d{1,3}(,\d{3})*(\.\d{2})?$/.test(value);
    }, '');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    $("#ac-account-form").validate({
        rules: {
            email: {
                required: true,
                email: true,
                remote: {
                    url: "/ajax/check_email/",
                    type: "post"
                }
            }
        },

        messages: {
            email: {remote: "A user exists with this email"}
        }
    });

    $('#ac-account-form').submit(function () {
        formbalance = $('#id_balance').val();
        formbalance = formbalance.replace(/,/g, '');
        formbalance = formbalance.replace(/£/g, '');
        $('#id_balance').val(formbalance);
        return true; // submit the form
    });
    /*$('input#id_balance').change(function(){
     var num = parseFloat($(this).val());
     var cleanNum = num.toFixed(2);
     $(this).val(cleanNum);
     $('select[name="account_type"]', '#ac-account-form').change();

     });	*/
});
