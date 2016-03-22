(function() {
  var ajaxAddProductsCall;

  ajaxAddProductsCall = function(form_id, div_id) {
    $.ajax({
      data: $(form_id).serialize(),
      type: $(form_id).attr("method"),
      url: $(form_id).attr("action"),
      success: function(response) {
        $(div_id).replaceWith(response);
      }
    });
  };

  $(document).ready(function() {
    $.validator.setDefaults({
      ignore: ":hidden:not(select)"
    });
    $(".variable-product-form").validate({
      submitHandler: function(form) {
        ajaxAddProductsCall(".variable-product-form", ".js-variable-product-form");
      }
    });
    $(".fixed-product-form").validate({
      submitHandler: function(form) {
        ajaxAddProductsCall(".fixed-product-form", ".js-variable-product-form");
      }
    });
  });

}).call(this);

//# sourceMappingURL=healthcheck-portfolio-val.js.map
