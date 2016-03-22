$(document).ready(function () {
    'use strict';
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
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


    $('#id_opening_date_month').change(function () {
        var month = $('#id_opening_date_month').val();
        var year = $('#id_opening_date_year').val();
        var product = $('#id_product').val();
        var balance = $('#id_balance').val();

        if (month !== 0 && year !== 0) {
            $.post("/ajax/check_expiry/", {productID: product,
                opYear: year,
                opMonth: month}, function (data) {

                if (data.maturity_date_month !== 0) {

                }

                if (data.expired === "True") {
                    $("span.bonusHasExpired").show();
                }
                else {
                    $("span.bonusHasExpired").hide();
                }

                $.post("/ajax/get_new_rate/", {productID: product,
                    bonusExpired: data.expired}, function (newRate) {
                    $('span.your-rate').html((Number(newRate)).toFixed(2) + "%");
                    var newBalance = Number(balance * newRate + Number(balance));
                    var newExtra = Number($('span.unmodifiedTotalBalance').html()) - newBalance;
                    $('span.balanceValue').html("£" + delimitNumbers(newBalance.toFixed(2)));
                    $('span.extraBalanceText').html("£" + delimitNumbers(newExtra.toFixed(2)));
                });
            });
        }
    });

    $('#id_opening_date_year').change(function () {

        var month = $('#id_opening_date_month').val();
        var year = $('#id_opening_date_year').val();
        var product = $('#id_product').val();
        var balance = $('#id_balance').val();

        if (month !== 0 && year !== 0) {
            $.post("/ajax/check_expiry/", {productID: product,
                opYear: year,
                opMonth: month}, function (data) {

                if (data.maturity_date_year !== 0) {

                }

                if (data === "True") {
                    $("span.bonusHasExpired").show();
                }
                else {
                    $("span.bonusHasExpired").hide();
                }

                $.post("/ajax/get_new_rate/", {productID: product,
                    bonusExpired: data}, function (newRate) {
                    $('span.your-rate').html((Number(newRate)).toFixed(2) + "%");
                    var newBalance = Number(balance * newRate + Number(balance));
                    var newExtra = Number($('span.unmodifiedTotalBalance').html()) - newBalance;
                    $('span.balanceValue').html("£" + delimitNumbers(newBalance.toFixed(2)));
                    $('span.extraBalanceText').html("£" + delimitNumbers(newExtra.toFixed(2)));
                });
            });
        }
    });
});

function delimitNumbers(str) {
    'use strict';
    return (str + "").replace(/\b(\d+)((\.\d+)*)\b/g, function (a, b, c) {
        return (b.charAt(0) > 0 && !(c || ".").lastIndexOf(".") ? b.replace(/(\d)(?=(\d{3})+$)/g, "$1,") : b) + c;
    });
}