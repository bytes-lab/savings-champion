$(document).ready(function() {

    $('.decision').each(function() {
        var $this = $(this);

        $('a.next', $this).bind('click', function() {
            var $link = $(this).attr('href');
            showPane($link);
            activeBall($(this).attr('href'));
        });
        // find the ball that should be active
        function showPane($link) {
            $($link)
                .addClass('active')
                .removeClass('hidden')
                .siblings('div')
                .removeClass('active')
                .addClass('hidden');
        }

        function activeBall(id) {
            $('a', '#decision-nav').each(function() {
                $(this).parent().removeClass('active');
            });
            $('a[href="' + id + '"]', '#decision-nav').each(function() {
                $(this).parent().addClass('active');
            });

        }
    });


    var $option = $('select[name="maturity_date_month"] option[value="0"]').text('Select month');
    var $option = $('select[name="maturity_date_year"] option[value="0"]').text('Select year');

    var $option = $('select[name="opening_date_month"] option[value="0"]').text('Select month');
    var $option = $('select[name="opening_date_year"] option[value="0"]').text('Select year');

    /* Tabs
     ================================================== */
    var tabs = $('ul.tabs');

    tabs.each(function(i) {
        //Get all tabs
        var tab = $(this).find('li a');

        tab.bind('click', function(e) {

            //Get Location of tab's content
            var link = $(this).attr('href');

            //Let go if not a hashed one
            if (link.charAt(0) == '#') {

                e.preventDefault();

                //Make Tab Active
                tab.parent('li').removeClass('active');
                $(this).parent('li').addClass('active');

                //Show Tab Content & add active class
                $(link)
                    .addClass('active')
                    .removeClass('hidden')
                    .siblings('div')
                    .removeClass('active')
                    .addClass('hidden');
            }
        });
    });


    /* Show Hide Rate Tracker Help
     ================================================== */
    $('.info .text').hide();
    var $info = $('.info .ico-omrc');
    $info.hover(function() {
        if ($(this).hasClass('active')) {
            $(this)
                .removeClass('active')
                .next('.text')
                .hide();

        } else {

            $.each($info, function() {
                if ($(this).hasClass('active')) {
                    $(this)
                        .removeClass('active')
                        .next('.text')
                        .hide();
                }
            });

            $(this)
                .addClass('active')
                .next('.text')
                .show();
        }

        return false;
    });

    /* Best Buy Tool
     ================================================== */
    if ($('#your-income').find('h2').hasClass('open') === true) {
        $('form', '.bb-tool').show();
    }

    $('.bb-tool').each(function() {
        var $this = $(this);
        var $form = $('form', $this);

        $('h2', $this).bind('click', function() {
            $(this).toggleClass('open');
            $form.toggle();
            return false;
        });

        // backend may be keeping the form open if it has been posted
        if ($('h2', $this).hasClass('open') === false) {
            $form.hide();
        }
        return false;
    });

    // Hide Errors On Keypress
    $('.ac-account').delegate('.errors input', 'keypress', function() {
        $(this).siblings('.ico-error').hide();
    });


    /* Quotes
     ================================================== */
    $('blockquote p:first').prepend('<span>&ldquo;</span>');
    $('blockquote p:last').append('<span>&rdquo;</span>');

    $('a.cta-link').click(function(e) {
        window.location.href = $(this).attr('href');
        return false;
    });

});
