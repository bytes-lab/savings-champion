$(document).ready(function(){

	/* Ie Select Box Cut of fix
	================================================== */
	$("form").delegate('select','focus blur', function(e) {
		if (e.type == 'focusin') {
				$(this).addClass('ie-focus');
			}
			else {
				$(this).removeClass('ie-focus');
			}
	});

});
