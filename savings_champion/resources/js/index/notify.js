(function() {
  $(document).ready(function() {
    "use strict";
    if ($.cookie("cookie_notification") !== "1") {
      $.cookie("cookie_notification", "1", {
        expires: 3
      });
    }
  });

}).call(this);

//# sourceMappingURL=notify.js.map
