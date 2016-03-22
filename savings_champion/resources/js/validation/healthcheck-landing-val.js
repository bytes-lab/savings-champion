(function() {
  $(document).ready(function() {
    $(".signup-form").validate({
      errorPlacement: function(error, element) {
        return true;
      }
    });
    $(".additional-signup-form").validate({
      errorPlacement: function(error, element) {
        return true;
      }
    });
  });

}).call(this);

//# sourceMappingURL=healthcheck-landing-val.js.map
