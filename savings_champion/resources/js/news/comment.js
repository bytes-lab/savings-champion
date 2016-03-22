(function() {
  var ajaxCommentCall, hitCallbackHandler, reloadPage;

  ajaxCommentCall = function() {
    "use strict";
    $.ajax({
      data: $(".comment-form").serialize(),
      type: $(".comment-form").attr("method"),
      url: $(".comment-form").attr("action"),
      success: function() {
        if (ga) {
          ga("send", "event", "News", "Comment Form", "Submitted");
        }
        reloadPage();
      }
    });
  };

  reloadPage = function() {
    "use strict";
    location.reload(true);
  };

  $(document).ready(function() {
    "use strict";
    $(".comment-form").validate({
      submitHandler: function() {
        ajaxCommentCall();
      },
      errorPlacement: function() {
        return true;
      }
    });
    $(".news-concierge-form").validate({
      errorPlacement: function() {
        return true;
      }
    });
  });

  hitCallbackHandler = function(url, win) {
    if (win && win.length > 0) {
      return window.open(url, win);
    } else {
      return window.location.href = url;
    }
  };

  $('table[class*="table"] a').click(function() {
    var url, win;
    url = this.getAttribute('href');
    win = (typeof (this.getAttribute("target") === "string") ? this.getAttribute("target") : "");
    if (url === 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-p/') {
      ga('send', 'event', 'Product Outbound', 'Nationwide - FlexDirect Current Account', 'paid.outbrain.com (article)', {
        'hitCallback': hitCallbackHandler(url, win)
      });
      this.preventDefault();
    }
    if (url === 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-x/') {
      ga('send', 'event', 'Product Outbound', 'Clydesdale Bank - Current Account Direct', 'paid.outbrain.com (article)', {
        'hitCallback': hitCallbackHandler(url, win)
      });
      this.preventDefault();
    }
    if (url === 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-m/') {
      ga('send', 'event', 'Product Outbound', 'Santander - 123 Current Account', 'paid.outbrain.com (article)', {
        'hitCallback': hitCallbackHandler(url, win)
      });
      this.preventDefault();
    }
    if (url === 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-yd/') {
      ga('send', 'event', 'Product Outbound', 'TSB Bank - Enhance Current Account', 'paid.outbrain.com (article)', {
        'hitCallback': hitCallbackHandler(url, win)
      });
    }
    if (url === 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-yh/') {
      ga('send', 'event', 'Product Outbound', 'Bank of Scotland - Vantage Current Account', 'paid.outbrain.com (article)', {
        'hitCallback': hitCallbackHandler(url, win)
      });
    }
    if (url === 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-yk/') {
      ga('send', 'event', 'Product Outbound', 'Lloyds - Vantage Current Account', 'paid.outbrain.com (article)', {
        'hitCallback': hitCallbackHandler(url, win)
      });
    }
  });

  $('body').on('click', '.js-iht-guide', function() {
    window.location.href = 'https://savingschampion.co.uk/ob-iht-guide/';
  });

  $('body').on('click', '.js-ob1-iht-guide', function() {
    window.location.href = 'https://savingschampion.co.uk/ob1-iht-guide/';
  });

}).call(this);

//# sourceMappingURL=comment.js.map
