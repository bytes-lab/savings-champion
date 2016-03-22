(function() {
  var handle_threshold_save, hideProductForm, isotopeFilterSetUp, load_portfolio, printContents, reloadPage;

  reloadPage = function() {
    "use strict";
    window.setTimout(function() {
      location.reload(false);
      return null;
    }, 500);
    return null;
  };

  hideProductForm = function() {
    "use strict";
    $(".js-variable-product-form").modal('hide');
    return $(".js-fixed-product-form").modal('hide');
  };

  isotopeFilterSetUp = function() {
    "use strict";
    $(".portfolios").isotope({
      layoutMode: 'straightDown',
      resizable: true,
      animationEngine: "best-available",
      getSortData: {
        balance: function($elem) {
          return Number($elem.find(".balance").text().replace(/[^0-9\.]+/g, ""));
        },
        provider: function($elem) {
          return $elem.find(".provider").text().replace(RegExp(" ", "g"), "");
        }
      }
    });
    $(".filters li").click(function() {
      var selector, total;
      $(this).parent().parent().find(".active").removeClass("active");
      selector = $(this).attr("data-filter");
      if (ga) {
        ga("send", "event", "Portfolio", "Filter", selector);
      }
      $(".portfolios").isotope({
        filter: selector
      });
      $(this).addClass("active");
      total = 0;
      if (selector === "*") {
        selector = ".product-box";
      }
      $(selector).each(function() {
        return total += Number($(this).find(".balance").text().replace(/[^0-9\.]+/g, ""));
      });
      $(".portfolio-total").html("<p>Total: £" + total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + "</p>");
      return false;
    });
    $(".balance-sort").click(function() {
      var ascending;
      ascending = $(this).attr("asc");
      if (ascending === true) {
        $(".portfolios").isotope({
          sortBy: "balance",
          sortAscending: true
        });
        $(this).attr("asc", "false");
      } else {
        $(".portfolios").isotope({
          sortBy: "balance",
          sortAscending: false
        });
        $(this).attr("asc", "true");
      }
      return false;
    });
    $(".provider-sort").click(function() {
      $(".portfolios").isotope({
        sortBy: "provider",
        sortAscending: true
      });
      return false;
    });
    $(".reset-sort").click(function() {
      $(".portfolios").isotope({
        sortBy: "original-order",
        sortAscending: true
      });
      return false;
    });
  };

  $("body").on('click', '.opening-date-click', function() {
    return $('.js-opening-date-form').modal('show');
  });

  $("body").on('click', '.apply-now-click', function() {
    $("#add-variable-products").hide();
    $("#add-fixed-products").show();
    if (ga) {
      return ga("send", "event", "Portfolio", "Apply", "Clicked");
    }
  });

  $("body").on('click', '.updateportfolio', function() {
    var balance, id, product, provider;
    provider = $(this).closest(".product-box").find(".provider").text();
    product = $(this).closest(".product-box").find(".product").text();
    balance = $(this).closest(".product-box").find(".balance").text();
    balance = balance.replace(/,/g, "");
    id = $(this).closest(".product-box").find(".id-info").text();
    $(".editbalance").val(balance);
    $(".providerEditField").html(provider);
    $(".productEditField").html(product);
    $(".portfolioeditid").val(id);
    $(".js-edit-variable-product-form").modal('show');
    if (ga) {
      return ga("send", "event", "Portfolio", "Variable", "Edit");
    }
  });

  $("body").on('click', ".print-button", function() {
    if (ga) {
      ga("send", "event", "Portfolio", "Display", "Portfolio Printed");
    }
    printContents('portfolio-container');
    return false;
  });

  $("body").on('click', ".opening-date-click", function() {
    var id;
    id = $(this).closest(".product-box").find(".id-info").text();
    return $("#id_portfolio_id").val(id);
  });

  $("body").on('click', '.delete', function() {
    var maturity;
    $(".yes-link").attr("id", $(this).closest(".product-box").find(".id-info").text());
    maturity = $(this).closest(".product-box").find(".maturitydate").text();
    if (maturity) {
      $(".yes-link").attr("is_fixed", true);
    }
    return $('.js-delete-box-modal').modal('show');
  });

  $("body").on('click', '.yes-link', function() {
    $.post("/best-buys/ajax/deleteportfolio/", {
      id: $(this).attr("id"),
      fixed: $(this).attr("is_fixed")
    }, function(data) {
      $(".js-delete-box-modal-content").html(data);
    });
    if (ga) {
      ga("send", "event", "Portfolio", "Product", "Deleted");
    }
    return false;
  });

  $("body").on('click', '.updatereminder', function() {
    var balance, id, product, provider, rate;
    provider = $(this).closest(".product-box").find(".provider").text();
    product = $(this).closest(".product-box").find(".account-type").text();
    balance = $(this).closest(".product-box").find(".balance").text();
    rate = $(this).closest(".product-box").find(".rate").text();
    balance = balance.replace(/,/g, "");
    id = $(this).closest(".product-box").find(".id-info").text();
    $("#reminder_balance").val(balance);
    $("#id_rate").val(rate);
    $(".providerEditField").html(provider);
    $(".productEditField").html(product);
    $("#reminder_id").val(id);
    $(".js-edit-fixed-product-form").modal('show');
    if (ga) {
      return ga("send", "event", "Portfolio", "Fixed", "Edit");
    }
  });

  $("body").on('click', '.js-add-variable-product-button', function() {
    $('.js-variable-product-form').modal('show');
    if (ga) {
      return ga("send", "event", "Portfolio", "Variable", "New");
    }
  });

  $("body").on('click', '.js-add-fixed-product-button', function() {
    $('.js-fixed-product-form').modal('show');
    if (ga) {
      return ga("send", "event", "Portfolio", "Fixed", "New");
    }
  });

  $("body").on('click', '.arrow > img', function(event) {
    var closed, event_target, product_box;
    console.log('arrow clicked');
    event_target = $(event.target);
    product_box = event_target.closest(".product-box");
    closed = event_target.attr("closed");
    console.log(closed);
    if (closed === 'true') {
      console.log('Evaluated as closed');
      product_box.find(".panel-body").show();
      event_target.attr("closed", 'false');
      product_box.find('.arrow').find(".closed-arrow-img").hide();
      product_box.find('.arrow').find(".expanded-arrow-img").show();
    } else {
      console.log('Evaluated as not closed');
      product_box.find(".panel-body").hide();
      event_target.attr("closed", 'true');
      product_box.find('.arrow').find(".closed-arrow-img").show();
      product_box.find('.arrow').find(".expanded-arrow-img").hide();
    }
    $(".portfolios").isotope("reLayout");
    return false;
  });

  $("body").on("click", ".close-all", function() {
    if (ga) {
      ga("send", "event", "Portfolio", "Display", "All minimised");
    }
    $(".product-box > .panel-body").hide();
    $(".arrow").attr("closed", true);
    $(".expanded-arrow-img").hide();
    $(".closed-arrow-img").show();
    $(".closed-balance").show();
    $(".closed-maturity-date").show();
    $(".portfolios").isotope("reLayout");
    return false;
  });

  $("body").on("click", ".expand-all", function() {
    if (ga) {
      ga("send", "event", "Portfolio", "Display", "All expanded");
    }
    $(".product-box > .panel-body").show();
    $(".arrow").attr("closed", false);
    $(".closed-arrow-img").hide();
    $(".expanded-arrow-img").show();
    $(".closed-balance").hide();
    $(".closed-maturity-date").hide();
    $(".portfolios").isotope("reLayout");
    return false;
  });

  printContents = function(id) {
    "use strict";
    $(".portfolios").isotope('destroy');
    window.print();
    return false;
  };

  load_portfolio = function() {
    "use strict";
    isotopeFilterSetUp();
    $('.js-threshold-form').modal('show');
  };

  $(document).ready(load_portfolio);

  handle_threshold_save = function(data, textStatus, jqXHR) {
    if (data.status === 'success') {
      $('.js-threshold-form').modal('hide');
    } else {
      $('.js-threshold-form').find('.form-group').addClass('has-error');
    }
  };

  $('body').on('click', '.js-threshold-form-save', function(event) {
    var event_target, form, url;
    event_target = $(event.target);
    url = event_target.data('url');
    form = $('.js-threshold-form').find('form');
    $.post(url, form.serialize(), handle_threshold_save);
  });

}).call(this);

//# sourceMappingURL=load_portfolio.js.map
