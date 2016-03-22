function update_mailto() {
    'use strict';
    var mailto = 'mailto:?subject=' + encodeURIComponent($('#id_subject').val()) + '&cc=' +
        encodeURIComponent($('#id_email_addresses').val()) + '&body=' + encodeURIComponent($('#id_body').val());
    $('input[name=update]').click(function () {window.location.href = mailto;});
}
$('.form-control').on('change', function () {
    'use strict';
    update_mailto();
});