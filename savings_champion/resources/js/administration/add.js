(function() {
  var ajaxOpeningCall, ajaxPortfolioCall, ajaxReminderCall, checkOpening, rebindInputChange, reloadPage, retrieveAccountType, retrieveProducts;

  rebindInputChange = function() {
    "use strict";
    var $fixed_provider_select, $product_select, $provider_select;
    $product_select = $("select.productselect");
    $provider_select = $("select.providerselect");
    $fixed_provider_select = $("select.fixedproviderselect");
    $provider_select.select2({
      width: "100%"
    });
    $product_select.select2({
      width: "100%"
    });
    $fixed_provider_select.select2({
      width: "100%"
    });
    $product_select.empty();
    $provider_select.on("change", function() {
      var balance, parent, product_select, provider;
      provider = $(this).select2().val();
      balance = $(this).closest(".product-form").find(".balanceinput").val().replace(/,/g, "");
      parent = $(this);
      product_select = $(this).closest(".product-form").find("select.productselect");
      product_select.empty();
      product_select.append("<option value=\"0\">Please enter your details</option>");
      product_select.select2("val", "0");
      if (provider > 0 && balance > 0) {
        product_select.select2("enable", false);
        retrieveProducts(provider, balance, parent);
      }
    });
    $(".balanceinput").on("keyup", function() {
      var balance, parent, product_select, provider;
      provider = $(this).closest(".product-form").find(".providerselect").select2("val");
      balance = $(this).val().replace(/,/g, "");
      parent = $(this);
      product_select = $(this).closest(".product-form").find("select.productselect");
      product_select.empty();
      product_select.append("<option value=\"0\">Please enter your details</option>");
      product_select.select2("val", "0");
      if (provider > 0 && balance > 0) {
        product_select.select2("enable", false);
        retrieveProducts(provider, balance, parent);
        product_select.select2("val", "0");
      }
    });
    $provider_select.change(function() {
      var id;
      id = $(this).val();
      checkOpening(id);
    });
    $fixed_provider_select.change(function() {
      var account_type, parent, provider;
      provider = $(this).val();
      parent = $(this);
      account_type = $(this).closest(".product-form").find("select.account-type");
      account_type.empty();
      if (provider > 0) {
        retrieveAccountType(provider, parent);
      } else {
        account_type.append("<option value =\"0\">Please enter your details</option>");
      }
    });
  };

  retrieveProducts = function(provider, balance, parent) {
    "use strict";
    $.get("/best-buys/ajax/retrievepersonalproducts/", {
      providerid: provider,
      balanceval: balance
    }, function(data) {
      var options, product_select;
      options = "\"<option value=\"0\">Please enter your details</option>";
      $.each(data, function(i) {
        options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>";
      });
      if (typeof data[0] !== "undefined") {
        checkOpening(data[0][0]);
      }
      product_select = parent.closest(".product-form").find("select.productselect");
      product_select.append(options);
      product_select.select2("enable", true);
    });
  };

  retrieveAccountType = function(provider, parent) {
    "use strict";
    $.get("/best-buys/ajax/retrievefixedchoices/", {
      providerid: provider
    }, function(data) {
      var options;
      options = "";
      $.each(data, function(i) {
        options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>";
      });
      parent.closest(".product-form").find("select.account-type").append(options);
    });
  };

  checkOpening = function(optionValue) {
    "use strict";
    $.post("/best-buys/ajax/checkopening/", {
      productID: optionValue
    }, function(data) {
      var opening_date_group;
      opening_date_group = $(".opening-date-group");
      if (data === "True") {
        opening_date_group.show();
        opening_date_group.find(".datestyle").addClass("required");
        opening_date_group.find(".datestyle").attr("min", "1");
      } else {
        opening_date_group.find(".datestyle").removeClass("required");
        opening_date_group.find(".datestyle").removeAttr("min");
        opening_date_group.hide();
      }
    });
  };

  ajaxPortfolioCall = function() {
    "use strict";
    var edit_portfolio_form;
    edit_portfolio_form = $("#editportfolioform");
    $.ajax({
      data: edit_portfolio_form.serialize(),
      type: edit_portfolio_form.attr("method"),
      url: edit_portfolio_form.attr("action"),
      success: function(response) {
        $("#editportfolioform").html(response);
        $("#add-variable-products").colorbox.resize();
      }
    });
  };

  ajaxReminderCall = function() {
    "use strict";
    var edit_reminder_form;
    edit_reminder_form = $("#editreminderform");
    $.ajax({
      data: edit_reminder_form.serialize(),
      type: edit_reminder_form.attr("method"),
      url: edit_reminder_form.attr("action"),
      success: function(response) {
        edit_reminder_form.html(response);
        $("#add-fixed-products").colorbox.resize();
      }
    });
  };

  ajaxOpeningCall = function() {
    "use strict";
    var opening_date_form;
    opening_date_form = $(".opening-date-form");
    $.ajax({
      data: opening_date_form.serialize(),
      type: opening_date_form.attr("method"),
      url: opening_date_form.attr("action"),
      success: function(response) {
        $.colorbox.close();
      }
    });
  };

  reloadPage = function() {
    "use strict";
    location.reload(true);
  };

  $(document).ready(function() {
    "use strict";
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
    $(".add-products-button").click(function() {
      $("#add-fixed-products").hide();
      $("#add-variable-products").show();
    });
    $(".fixed-click").click(function() {
      $("#add-variable-products").hide();
      $("#add-fixed-products").show();
    });
    rebindInputChange();
    $("select.providerselect").change(function() {
      window.console.log("Provider changes");
    });
    $(".balanceinput").on("keyup", function() {
      window.console.log("Balance changes");
    });
    $("select.productselect").change(function() {
      window.console.log("Product changes");
    });
  });

}).call(this);

//# sourceMappingURL=add.js.map
