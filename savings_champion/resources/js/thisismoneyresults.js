$(document).ready(function() {
	$("#id_email").attr("disabled", "disabled");
	
	$(".edit").click(function() {
		$("#id_email").removeAttr("disabled");
	});
	
	$("#id_email").keyup(function(event) {
		$("#id_email2").val($("#id_email").val());
	});
		  
        jQuery.extend(jQuery.validator.messages, {        
        maxlength: "",
        required: "",
        min: "",
        email:""
    });
    
    $("#register-form").validate({
        invalidHandler: function(e, validator) {
            var errors = validator.numberOfInvalids();
            if (errors) {
                var message = errors == 1
                    ? 'You have missed 1 field. It has been highlighted below'
                    : 'You have missed ' + errors + ' fields.  They have been highlighted below';
                $("div.error span").html(message);
                $("div.error").show();
            } else {
                $("div.error").hide();
            }
            }
    });

    $('input[name="reset"]').click(function () {
        window.location.href = "{% url 'timrate_check' %}";
    });
    var left_height = $('td.track-account').height();
    var right_height = $('td.facts-row').height();

    if ((left_height > 0) || (right_height > 0)) {
        if (left_height > right_height) {
            $('td.facts-row').height(left_height);
        } else {
            $('td.track-account').height(right_height);
        }
    }

    $('#track-this').click(function () {
        $('#track-product').submit();
    });

});