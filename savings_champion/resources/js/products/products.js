(function() {
  var continue_to_provider, join_spl_and_continue;

  $.validator.setDefaults({
    highlight: function(element) {
      $(element).closest(".form-group").addClass("has-error");
    },
    unhighlight: function(element) {
      $(element).closest(".form-group").removeClass("has-error");
    },
    errorElement: "span",
    errorClass: "help-block",
    errorPlacement: function(error, element) {
      if (element.parent(".input-group").length) {
        error.insertAfter(element.parent());
      } else {
        error.insertAfter(element);
      }
    }
  });

  join_spl_and_continue = function(form, event) {
    var form_data, form_url;
    event.preventDefault();
    form = $('.js-spl');
    form_url = form.attr('action');
    form_data = form.serialize();
    $.post(form_url, form_data, continue_to_provider, 'html');
    return false;
  };

  continue_to_provider = function() {
    var product, provider_url;
    provider_url = $('.js-provider-url').data('url');
    product = $('.js-provider-url').data('product');
    if (ga) {
      ga("send", "event", "Savings Priority List", product + "_Skipped");
    }
    window.location = provider_url;
  };

  $('body').on('click', '.js-to-provider', continue_to_provider);

  $('.js-spl').submit(function(e) {
    e.preventDefault();
  }).validate({
    submitHandler: join_spl_and_continue,
    rules: {
      name: "required",
      email: {
        required: true,
        email: true
      }
    }
  });

}).call(this);

//# sourceMappingURL=products.js.map
