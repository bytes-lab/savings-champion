(function() {
  $(document).ready(function() {
    "use strict";
    $(".arrow").click(function() {
      if (ga) {
        ga("send", "event", "News", "Pagination", "Changed");
      }
    });
    $(".rss").click(function() {
      if (ga) {
        ga("send", "event", "News", "RSS", "Clicked");
      }
    });
    $(".signup-form").submit(function() {
      if (ga) {
        ga("send", "News", "Sidebar", "Signup");
      }
      return true;
    });
  });

}).call(this);

//# sourceMappingURL=news_index.js.map
