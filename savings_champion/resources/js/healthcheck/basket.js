(function() {
  $(document).ready(function() {
    "use strict";
    $(".give-button").click(function() {
      $(".name").show();
      $(".sidebar").show();
      $('html, body').animate({
        scrollTop: $(".give-button").offset().top
      }, 200);
      if ($("#id_advice").is(":checked") || $("#id_concierge").is(":checked")) {
        $("#div_id_telephone").show();
        $("#id_telephone").addClass("required");
        return $("#id_telephone").show();
      } else {
        $("#div_id_telephone").hide();
        $("#id_telephone").hide();
        return $("#id_telephone").removeClass("required");
      }
    });
    return $(".checkbox").change(function() {
      if ($("#id_advice").is(":checked") || $("#id_concierge").is(":checked")) {
        $("#div_id_telephone").show();
        $("#id_telephone").show();
        $("#id_telephone").addClass("required");
        return $("#id_telephone").attr("required", true);
      } else {
        $("#div_id_telephone").hide();
        $("#id_telephone").hide();
        $("#id_telephone").removeClass("required");
        return $("#id_telephone").removeAttr("required");
      }
    });
  });

}).call(this);

//# sourceMappingURL=basket.js.map
