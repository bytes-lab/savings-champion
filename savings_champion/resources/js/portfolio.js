$(document).ready(function () {
    $("#printAllPortfolio").click(function () {
        $("#portfolioPrintContainer").printElement({printMode: 'popup', overrideElementCSS: ['/static/css/printPortfolio.css'] });
    });

    $(".inline").click(function () {
        //For the portfolio table (not reminders!)
        var balance = $(this).parent().find('.balanceFormValue').text();
        balance = balance.replace(/,/g, '');

        $('#id_id').val($(this).parent().parent().find('.portfolioId').text());
        $('#id_balance').val(balance);
        $('.providerEditField').html($(this).parent().parent().find('.providerName').text());
        $('.productEditField').html($(this).parent().parent().find('.productName').text());
    });

    $(".reminderinline").click(function () {
        //For the remindertable
        var balance = $(this).parent().find('.balanceFormValue').text();
        balance = balance.replace(/,/g, '');
        $('#reminder_id').val($(this).parent().parent().find('.portfolioId').text());
        $('#reminder_balance').val(balance);
        $('.providerEditField').html($(this).parent().parent().find('.providerName').text());
        $('.productEditField').html($(this).parent().parent().find('.productName').text());
    });

    $(".inline").colorbox({inline: true, height: "850px", onClosed: reloadPage});
    $(".reminderinline").colorbox({inline: true, height: "850px", onClosed: reloadPage});

    function reloadPage() {
        location.reload(true);
    }

    $("#editportfolioform").validate({
        submitHandler: function (form) {
            //this runs when the form validated successfully
            ajaxPortfolioCall(); //submit it the form
        }

    });

    $("#editreminderform").validate({
        submitHandler: function (form) {
            //this runs when the form validated successfully
            ajaxReminderCall(); //submit it the form
        }

    });


    $.validator.addMethod('commaNumber', function (value) {
        var balance = value.replace(/,/g, '');
        return /^-?(?:\d+|\d{1,3}(?:,\d{3})+)?(?:\.\d+)?$/.test(balance);
        //return /\d{1,3}(,\d{3})*(\.\d{2})?$/.test(value);
    }, '');

    $.validator.addMethod('minComma', function (value) {
        var balance = value.replace(/,/g, '');
        return balance >= 1;


    }, '');

    function ajaxPortfolioCall() { // catch the form's submit event
        $.ajax({ // create an AJAX call...
            data: $('#editportfolioform').serialize(), // get the form data
            type: $('#editportfolioform').attr('method'), // GET or POST
            url: $('#editportfolioform').attr('action'), // the file to call
            success: function (response) { // on success..
                $('#editportfolioform').html(response); // update the DIV
            }
        });
    };

    function ajaxReminderCall() { // catch the form's submit event
        $.ajax({ // create an AJAX call...
            data: $('#editreminderform').serialize(), // get the form data
            type: $('#editreminderform').attr('method'), // GET or POST
            url: $('#editreminderform').attr('action'), // the file to call
            success: function (response) { // on success..
                $('#editreminderform').html(response); // update the DIV
            }
        });
    };


});
     
