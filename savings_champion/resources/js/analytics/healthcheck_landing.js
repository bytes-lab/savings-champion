(function() {
  $(document).ready(function() {
    "use strict";
    $(".healthcheck-signup").click(function() {
      if (ga) {
        ga("send", "event", "Signup", "Healthcheck", "Clicked");
      }
    });
  });

}).call(this);

//# sourceMappingURL=healthcheck_landing.js.map
