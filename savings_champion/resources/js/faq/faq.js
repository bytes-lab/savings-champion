(function() {
  $(document).ready(function() {
    "use strict";
    $(".arrow").click(function() {
      var closed;
      closed = void 0;
      closed = $(this).attr("closed");
      if (closed === true) {
        $(this).closest(".question-block").find(".answer").show();
        $(this).attr("closed", false);
        $(this).find(".closed-arrow-img").hide();
        $(this).find(".expanded-arrow-img").show();
      } else {
        $(this).closest(".question-block").find(".answer").hide();
        $(this).attr("closed", true);
        $(this).find(".expanded-arrow-img").hide();
        $(this).find(".closed-arrow-img").show();
      }
      return false;
    });
    $(".concierge-faq-signup").click(function() {
      if (ga) {
        ga("send", "event", "Concierge", "FAQ Signup", "Clicked");
      }
    });
    $(".healthcheck-faq-signup").click(function() {
      if (ga) {
        ga("send", "event", "Healthcheck", "FAQ Signup", "Clicked");
      }
    });
  });

}).call(this);

//# sourceMappingURL=faq.js.map
