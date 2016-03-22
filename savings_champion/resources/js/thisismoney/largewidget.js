$(document).ready(function() {
    'use strict';
    $('.tabblock').click(function(event) {
        $('#tabContainer').find('.tabblock').each(function() {
            $(this).removeClass('active');
        });

        $(this).addClass('active');

        var str = $(this).text();
        if (str.toLowerCase().indexOf('tracker') >= 0) {
            location.reload();

        }
        $.ajax({ // create an AJAX call...
            type: 'GET',
            url: $(this).attr('action'), // the file to call
            success: function(response) { // on success..
                $('#contentContainer').html(response); // update the DIV
                if (str.toLowerCase().indexOf('concierge') >= 0) {
                    validateConcierge();
                }
                if (str.toLowerCase().indexOf('rate alerts') >= 0) {
                    googleTracking();
                }
            }
        });
    });
});


function validateConcierge() {
    'use strict';
    jQuery.validator.addMethod('phoneUK', function(phone_number, element) {
            return this.optional(element) || phone_number.length > 9 &&
                phone_number.match(/^(\(?(0|\+44)[1-9]{1}\d{1,4}?\)?\s?\d{3,4}\s?\d{3,4})$/);
        }, 'Please specify a valid phone number'
    );

    $('#conciergeform').validate({
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
            email: 'Please enter a valid email address',
            telephone: 'Please enter a valid telephone number',
            digits: 'Please only use numbers',
            name: 'Please enter your name'
        }
    });

}

function googleTracking() {
    'use strict';
    $('.newsletterlink').click(function() {
        if (ga) {
            ga('send', 'event', 'Newsletter', 'This is Money', 'Signup');
        }
    });

    $('.ratealertslink').click(function() {
        if (ga) {
            ga('send', 'event', 'Rate Alerts', 'This is Money', 'Signup');
        }
    });
}

$(function () {
    // this cannot be within the script file unless we create a plugin and pass the json to it

    var info_type = 1, error_type = 2;

    var frb_msg = "<p>The rate on your account won’t change until maturity. Enter your balance and maturity date and we will remind you before your bond matures";

    var valid_balance_msg = "<h2>Invalid Balance</h2><p>Please enter a valid balance</p>";

    var no_accounts_msg = "<h2>No accounts found</h2><p>We have been unable to find a matching account based on your search criteria. If you cannot find your savings account, please send an email to <a href=\"mailto:info@savingschampion.co.uk\">info@savingschampion.co.uk</a> and we will look into it for you.</p>";

    var unknown_acc_msg = "<p>If you’re unsure of your account name call your provider to check. Alternatively call us on 0800 321 3582.</p>";

    var unknown_type_msg = "<p>If you’re unsure of your savings type call your provider to check. Alternatively call us on 0800 321 3582.</p>";

    $('select[name="provider"]', '#ac-account-form').change(function () {
        var $this = $(this);

        if ($this.val()) {
            var $type_select = $('select[name="account_type"]');

            var $allowed_options;

            $.get("/ajax/get_bestbuys/", {'provider': $this.val()}, function (data) {
                var val = $type_select.find('option:selected').val();
                $type_select.find('option').remove();
                $(data).each(function (index) {
                    $type_select.append($('<option>', { value: $(this)[0] }).text($(this)[1]));
                });

                $type_select.prepend($('<option>', { value: '' }).text('Savings Type'));
                $type_select.append($('<option>', { value: '0' }).text('Don\'t know'));
                $type_select.val('');
            });


        }

        return false;
    });


    $('select[name="provider"]', '#ac-account-form').change(function () {
        if ($(this).val() != '') {
            //
            completeToStep(1);

            removeMessage($('li#provider'));

            var provider = $(this).val();

            // provider is completed on completion, must ensure the next tab is active
            $('li[name="account-type"]').addClass('active');

            if ($('select[name="account_type"]', '#ac-account-form').val() != '') {

                var account_type = $(this).val();

                if (hasBalance($('input[name="balance"]', '#ac-account-form'))) {

                    var balance = $('input[name="balance"]', '#ac-account-form').val();

                    updateAccounts();
                }

            }

        }
    });
    // check if all three have a value
    $('select[name="account_name"]', '#ac-account-form').live('change', function () {
        if ($(this).val() != '0') {
            $('#tracker-content').children('.response-message').remove();
            $('#result-button').show();
        }
    });

    $('input[name="balance"]').keypress(function (event) {
        return event.keyCode != 13;
    });

    /**
     * Depending on how this changes - we may want to show/hide the maturity date fields.
     * We look at some JSON fields which contain the ids which are maturity based
     */
    $('select[name="account_type"]', '#ac-account-form').change(function () {
        if ($(this).val() != '') {
            //
            completeToStep(2);

            if ($(this).val() != '0') {
                $('#tracker-content').children('.response-message').remove();
                $('#result-button').show();
            } else {
                $('#result-button').hide();
            }
            var account_type = $(this).val();
            $('li[name="balance"]').addClass('active');

            var found = false;

            if (account_type == 14 || account_type == 15) {
                found = true;
            }

            // TODO toggle several things
            if (found == true) {
                setMessage($('li#type'), info_type, frb_msg);
                $('#id_balance').focus();

                var $month_select = $('#id_maturity_date_month');
                var $year_select = $('#id_maturity_date_year');
                $month_select.find('option[value=0]').remove().end();
                $year_select.find('option[value=0]').remove().end();

                $month_select.prepend($('<option>', { value: '0' }).text('Month'));
                $year_select.prepend($('<option>', { value: '0' }).text('Year'));


                $('li#email').find('div.text').html("Your email address will be used to start the registration of your fixed rate products with Rate Tracker");

                $("#result-button").attr("src", "/static/img/reminder-results.png");
                $('#maturity_date_group').show();


                $('#account_name_group').hide();
            } else {
                removeMessage($('li#type'));

                if ($(this).val() == '0') {
                    setMessage($(this).parents('li'), info_type, unknown_type_msg);
                } else {

                }

                $('#maturity_date_group').hide();
                $('li#email').find('div.text').html("Needed to get your results, and to register with Rate Tracker, so you'll know if your savings rate changes and where to get the best rate. You can unsubscribe at any point.");
                $("#result-button").attr("src", "/static/img/rateresults.png");
                $('#account_name_group').show();
            }

            if ($('select[name="provider"]', '#ac-account-form').val() != '') {

                var provider = $(this).val();

                if (hasBalance($('input[name="balance"]', '#ac-account-form'))) {
                    removeMessage($('li#balance'));
                    var balance = $('input[name="balance"]', '#ac-account-form').val();
                    $('li[name="balance"], li[name="account-name"]').addClass('active');
                    updateAccounts();
                }
            }
        }
    });

    $('select[name="product"]', '#ac-account-form').live('click', function (e) {
        if (($(this).val() != '') && ($(this).val() != '0')) {
            $('#result-button').show();
            return false;
        }
    });

    $('input[name="balance"]', '#ac-account-form').keyup(function (e) {
        var $li_element = $('li#balance');
        $(this).val($(this).val().replace(/,/g, ''));
        if (hasBalance($('input[name="balance"]', '#ac-account-form'))) {
            //
            completeToStep(3);

            removeMessage($li_element);
            var balance = $('input[name="balance"]', '#ac-account-form').val();

            if ($('select[name="provider"]', '#ac-account-form').val() != '') {
                var provider = $(this).val();

                if ($('select[name="account_type"]', '#ac-account-form').val() != '') {
                    var account_type = $(this).val();


                    updateAccounts();

                }
            }
        } else {
            setMessage($li_element, error_type, valid_balance_msg);
        }
        return false;
    });


    function hasBalance($element) {
        var value = $element.val();
        var pattern = /\d{1,3}(,\d{3})*(\.\d{2})?$/;

        if ((value != '') && (value != '0.00')) {
            return value.match(pattern);
        }
        return false;
    }

    function updateAccounts() {
        var post_data = $('#ac-account-form').serialize();

        var $account_select = $('#id_product');
        if ($account_select.is(':visible') == false) {
            return false;
        }

        var $type_select = $('#id_account_type');
        if ($type_select.val() == '' || $type_select.val() == '0') {
            return false;
        }

        $.get("/ajax/products/", post_data, function (data) {
            $account_select.find('option').remove();

            var $li_element = $('#account_name_group');
            if ((data) && (data.length > 0)) {

                var val = '<option value="">Account Name</option>';

                $.each(data, function (index, item) {
                    val += ('<option value="' + item[0] + '">' + item[1] + '</option>');
                })
                $('#id_product').replaceWith('<select id="id_product" name="product" class="required number">' + val + '<option value="0">Don\'t know</option></select>');

                $('#result-button').show();

                removeMessage($li_element);
            } else {

                changeMessage($li_element, info_type, no_accounts_msg);
                $('#id_product').replaceWith('<select id="id_product" name="product" class="required number">' + '<option value="0">No Accounts</option></select>');
                $('#result-button').hide();
            }

            // ensure the submit button is shown and the response messages are clear?
            $('#tracker-content').children('.response-message').remove();

            return false;
        });

    }


    $('input[name="reset"]').click(function () {
        $('#ac-account-form')[0].reset();
        $('#result-button').show();
        $('#maturity_date_group').hide();
        $('#account_name_group').show();

        removeMessage($('ol.ac-account li'))
        completeToStep(0);
        return false;
    });

    /**
     *
     */
    function completeToStep(step) {
        $('ul#steps li').each(function (index, item) {
            var $a = $(item).find('a');

            if (index < step) {
                if (!$a.hasClass('complete')) {
                    $a.addClass('complete').removeClass('active');
                }
            } else if (index == step) {
                $a.addClass('active').removeClass('complete');
            } else {
                $a.removeClass('complete').removeClass('active');
            }
        });

        // there is a fork around step 3,
        if (step >= 3) {
            step = 6;
        }
        $('.ac-account li').each(function (index, item) {
            if (index <= step) {
                if (!$(item).hasClass('active')) {
                    $(item).addClass('active');
                }
            }
        });
    }

    $("#id_product").live('change', function () {
        var $this = $(this);
        var value = $this.val();
        if (value == "0") {
            $('#result-button').hide();
            setMessage($this.parents('li'), info_type, unknown_acc_msg);
        } else {
            removeMessage($this.parents('li'));
        }
    });


    function removeMessage($li_element) {
        $li_element.removeClass('message').removeClass('errors');
        $li_element.find('a.ico-omrc').removeClass('active');
        $li_element.find('div.text').stop().hide();
    }


    function setMessage($li_element, message_type, msg) {
        $li_element.removeClass('message').removeClass('errors');

        $('ol.ac-account li').find('div.text').stop().hide();

        if (message_type == info_type) {
            $li_element.addClass('message');
        } else {
            $li_element.addClass('errors');
        }
        $li_element.find('div.text').html(msg).fadeIn(500).delay(3000).fadeOut(500);
        $li_element.find('a.ico').addClass('active');

    }

    function changeMessage($li_element, message_type, msg) {
        $li_element.removeClass('message').removeClass('errors');

        $('ol.ac-account li').find('div.text').stop().hide();

        if (message_type == info_type) {
            $li_element.addClass('message');
        } else {
            $li_element.addClass('errors');
        }

        $li_element.find('div.text').html(msg);
    }


});