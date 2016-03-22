(function() {
  $(document).ready(function() {
    $.validator.addMethod("commaNumber", (function(value) {
      var balance;
      balance = value.replace(/,/g, "");
      return /^-?(?:\d+|\d{1,3}(?:,\d{3})+)?(?:\.\d+)?$/.test(balance);
    }), "");
    $(".account-form").validate({
      errorPlacement: function(error, element) {
        return true;
      }
    });
  });

}).call(this);

//# sourceMappingURL=healthcheck-signup-val.js.map
