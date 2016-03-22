(function() {
  var ajaxEmailReminderCall, el, elementVisibilityMayChange, handler, isElementInViewport, printContents, toaster;

  printContents = function(id) {
    "use strict";
    return window.print();
  };

  ajaxEmailReminderCall = function() {
    "use strict";
    var email_instructions_form;
    email_instructions_form = $(".email-instructions-form");
    $.ajax({
      data: email_instructions_form.serialize(),
      type: email_instructions_form.attr("method"),
      url: email_instructions_form.attr("action"),
      success: function() {
        window.location.href = $(".no-reminder").attr("href");
      }
    });
  };

  toaster = function(event) {
    "use strict";
    if (event === "in") {
      if ($.cookie("bestbuy-emails-modal") !== "shown") {
        $("#bestbuy-modal").modal("show");
      }
    } else {
      if (event === "out") {
        $("#bestbuy-modal").modal("hide");
      }
    }
  };

  isElementInViewport = function(el) {
    "use strict";
    var e, error, rect;
    rect = void 0;
    try {
      rect = el.getBoundingClientRect();
    } catch (error) {
      e = error;
      return false;
    }
    return rect.top >= 0 && rect.left >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && rect.right <= (window.innerWidth || document.documentElement.clientWidth);
  };

  elementVisibilityMayChange = function(el) {
    "use strict";
    return function() {
      if (isElementInViewport(el)) {
        toaster("in");
      } else {
        toaster("out");
      }
    };
  };

  $(document).ready(function() {
    "use strict";
    var apply_link;
    apply_link = $(".apply-link");
    apply_link.click(function() {
      var product, provider;
      product = void 0;
      provider = void 0;
      provider = $(this).attr("provider");
      product = $(this).attr("product");
      if (ga) {
        ga("send", "event", "BestBuys", provider, product);
      }
    });
    apply_link = apply_link.not(".authenticated");
    apply_link.click(function() {
      var product, provider;
      product = void 0;
      provider = void 0;
      $(".no-reminder").attr("href", $(this).attr("href"));
      provider = $(this).attr("provider");
      product = $(this).attr("product");
    });
    apply_link.colorbox({
      inline: true,
      href: "#apply-box"
    });
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        var getCookie;
        getCookie = function(name) {
          var cookie, cookieValue, cookies, i;
          cookieValue = null;
          if (document.cookie && document.cookie !== "") {
            cookies = document.cookie.split(";");
            i = 0;
            while (i < cookies.length) {
              cookie = jQuery.trim(cookies[i]);
              if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
              }
              i++;
            }
          }
          return cookieValue;
        };
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        }
      }
    });
    $(".email-instructions-form").validate({
      submitHandler: function() {
        ajaxEmailReminderCall();
      },
      errorPlacement: function() {
        return true;
      }
    });
    $(".whatis").click(function() {
      $(this).closest(".td-heading").find(".explanation").toggle();
      return false;
    });
    $(".print-button").click(function() {
      if (ga) {
        ga("send", "event", "BestBuys", "Display", "BestBuy Printed");
      }
      printContents(".product-section");
    });
  });

  $(".js-best-buy-signup-toaster-container").hover(toaster("in"), toaster("out"));

  $(".js-weekly-rate-alerts").on('submit', function(e) {
    "use strict";
    var formURL, postData;
    postData = $(this).serialize();
    formURL = $(this).attr("action");
    $.ajax({
      url: formURL,
      type: 'post',
      data: postData,
      cache: false,
      dataType: 'text',
      success: function() {
        $(".js-highlight-error").hide();
        $(".js-weekly-bestbuy-trigger").html("<div class=\"alert alert-success\"><p>Thank you, you've been added to our best buy emails. <a href=\"/concierge/\">See what else we do?</a></p></div>");
        toaster("out");
        $(window).unbind("resize scroll", handler);
        $(".js-best-buy-signup-toaster-container").unbind("mouseenter mouseleave", toaster);
        return $.cookie("bestbuy-emails-modal", "shown");
      },
      error: function(jqXHR, status, err) {
        return $(".js-highlight-error").show();
      }
    });
    return e.preventDefault();
  });

  el = document.getElementsByClassName("apply")[0];

  handler = elementVisibilityMayChange(el);

  $(window).load(function() {
    "use strict";
    if ($(".js-weekly-bestbuy-trigger").is(":visible")) {
      $(window).on("resize scroll", handler);
    }
  });

  $(window).on("hidden.bs.modal", function() {
    "use strict";
    $(window).unbind("resize scroll", handler);
    $(".js-best-buy-signup-toaster-container").unbind("mouseenter mouseleave", toaster);
  });

  $(".modal-footer > input.btn-danger").click(function() {
    "use strict";
    if (ga) {
      ga("send", "event", "BestBuys", "Modal", "Closed");
    }
    $.cookie("bestbuy-emails-modal", "shown", {
      expires: 1
    });
  });

  $(".modal-header > button.close").click(function() {
    "use strict";
    if (ga) {
      ga("send", "event", "BestBuys", "Modal", "Closed");
    }
    $.cookie("bestbuy-emails-modal", "shown", {
      expires: 1
    });
  });

  $('body').on('click', '.js-high-interest-current-accounts-5-percent', function() {
    if (ga) {
      ga("send", "event", "BestBuys", "High Interest Banner", "Clicked");
    }
  });

  $('body').on('click', '.js-show-full-table', function(event) {
    var event_target;
    event_target = $(event.target);
    event_target.hide();
    event_target.siblings().show();
  });

  $('body').on('click', '.js-hide-full-table', function(event) {
    var event_target;
    event_target = $(event.target);
    event_target.hide();
    event_target.siblings().show();
  });

  $('body').on('show.bs.collapse', function(event) {
    var event_target;
    event_target = $(event.target);
    event_target.find('.js-show-full-table').hide();
    event_target.find('.js-hide-full-table').show();
  });

  $('body').on('hide.bs.collapse', function(event) {
    var event_target;
    event_target = $(event.target);
    event_target.find('.js-show-full-table').show();
    event_target.find('.js-hide-full-table').hide();
  });

}).call(this);

//# sourceMappingURL=topaccounts.js.map
