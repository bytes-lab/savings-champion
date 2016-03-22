$(document).ready(function () {
    'use strict';
    $('div.expandable p').expander();
    $(".inline").colorbox({inline: true, height: "850px"});

    $(".callbackbutton").click(function () {
        $(".callback-form").show();
    });


    jQuery.validator.addMethod('phoneUK', function (phone_number, element) {
            return this.optional(element) || phone_number.length > 9 &&
                phone_number.match(/^(\(?(0|\+44)[1-9]{1}\d{1,4}?\)?\s?\d{3,4}\s?\d{3,4})$/);
        }, 'Please specify a valid phone number'
    );
    // validate the concierge form
    $(".concierge-form form").validate({
        rules: {
            email: {
                required: true,
                email: true
            },
            telephone: {
                required: true,
                phoneUK: true
            },
            name: {
                required: true
            }
        },
        messages: {
            email: "Please enter a valid email address",
            telephone: "Please enter a valid telephone number",
            digits: "Please only use numbers",
            name: "Please enter your name"
        }
    });

    $("#id_telephone").keyup(function (event) {
        $(".altContainer").show();
    });

    $("#callbackform").validate({
        rules: {
            email: {
                required: true,
                email: true
            },
            telephone: {
                required: true,
                phoneUK: true
            },
            name: {
                required: true
            }
        },
        messages: {
            email: "Please enter a valid email address",
            telephone: "Please enter a valid telephone number",
            digits: "Please only use numbers",
            name: "Please enter your name"
        }
    });
});