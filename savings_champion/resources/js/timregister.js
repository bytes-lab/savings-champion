$(document).ready(function() {
	$("#id_email").keyup(function(event) {
		$("#id_email2").val($("#id_email").val());
	});
	
	$("#id_password1").keyup(function(event) {
		$("#id_password2").val($("#id_password1").val());
	});
});
     
