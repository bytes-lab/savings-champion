(function() {
  var derp;

  $(document).ready(function() {
    "use strict";
    $(".asset-value").change(function() {
      var selected_value;
      selected_value = $(".asset-value").children("option:selected");
      $("#id_signup_amount").val(selected_value.text());
      window.location.href = selected_value.val();
    });
    $(".expand-offering").click(function() {
      $(".extra-text").show();
      $(".image").hide();
      return false;
    });
    jQuery.validator.addMethod("phoneUK", (function(phone_number, element) {
      return this.optional(element) || phone_number.length > 9 && phone_number.match(/^(\(?(0|\+44)[1-9]{1}\d{1,4}?\)?\s?\d{3,4}\s?\d{3,4})$/);
    }), "Please specify a valid phone number");
    $(".ifa-val").validate({
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

  derp = function() {
    return true;
  };

}).call(this);

//# sourceMappingURL=ifa.js.map
