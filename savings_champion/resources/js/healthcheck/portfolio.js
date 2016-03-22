(function() {
  var ajaxOpeningCall, ajaxPortfolioCall, ajaxReminderCall, body, checkOpening, rebindInputChange, reloadPage, retrieveAccountType, retrieveProducts;

  body = $('body');

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      var getCookie;
      getCookie = function(name) {
        var cookie, cookieValue, cookies, i;
        if (document.cookie && document.cookie !== "") {
          cookies = document.cookie.split(";");
          i = 0;
          if (typeof String.prototype.trim !== "function") {
            String.prototype.trim = function() {
              return this.replace(/^\s+|\s+$/g, "");
            };
          }
          while (i < cookies.length) {
            cookie = cookies[i].trim();
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
        return xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      }
    }
  });

  checkOpening = function(optionValue) {
    "use strict";
    return $.post("/best-buys/ajax/checkopening/", {
      productID: optionValue
    }, function(data) {
      var opening_date_group;
      opening_date_group = $(".opening-date-group");
      if (data === "True") {
        opening_date_group.show();
        opening_date_group.find(".datestyle").addClass("required");
        return opening_date_group.find(".datestyle").attr("min", "1");
      } else {
        opening_date_group.find(".datestyle").removeClass("required");
        opening_date_group.find(".datestyle").removeAttr("min");
        return opening_date_group.hide();
      }
    });
  };

  retrieveProducts = function(provider, balance, parent) {
    "use strict";
    var product_select;
    product_select = $("select.productselect");
    product_select.select2();
    product_select.empty();
    product_select.select2('data', {
      id: '-1',
      text: 'Loading'
    });
    return $.get("/best-buys/ajax/retrievepersonalproducts/", {
      providerid: provider,
      balanceval: balance
    }, function(data) {
      var options;
      options = "<option value=''>Please select a product</option>";
      $.each(data, function(i) {
        return options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>";
      });
      if (data[0] !== undefined) {
        checkOpening(data[0][0]);
      }
      product_select.empty();
      product_select.append(options);
      product_select.select2("enable", true);
      return product_select.select2('data', {
        id: '0',
        text: 'Please select a product'
      });
    });
  };

  retrieveAccountType = function(provider) {
    "use strict";
    var account_type_select, edit_reminder_form;
    edit_reminder_form = $(".fixed-product-form");
    account_type_select = edit_reminder_form.find("select.account-type");
    account_type_select.empty();
    account_type_select.append("<option value=''>Loading</option>");
    return $.get("/best-buys/ajax/retrievefixedchoices/", {
      providerid: provider
    }, function(data) {
      var options;
      account_type_select.empty();
      options = "<option value=''>Please select an account type</option>";
      $.each(data, function(i) {
        return options += "<option value=''" + data[i][0] + "'>" + data[i][1] + "</option>";
      });
      return account_type_select.append(options);
    });
  };

  ajaxPortfolioCall = function(e) {
    "use strict";
    var edit_portfolio_form;
    e.preventDefault();
    edit_portfolio_form = $(".variable-product-form");
    $.ajax({
      data: edit_portfolio_form.serialize(),
      type: edit_portfolio_form.attr("method"),
      url: edit_portfolio_form.attr("action"),
      success: function(response) {
        var balance, parent_form, provider, providerselect;
        edit_portfolio_form.html(response);
        $(".variable-product-form").submit(ajaxPortfolioCall);
        providerselect = $('select.providerselect');
        provider = providerselect.val();
        parent_form = providerselect.closest(".product-form");
        balance = parent_form.find("#id_balance").val().replace(/,/g, "").replace(/£/g, "");
        retrieveProducts(provider, balance, parent_form);
      }
    });
  };

  ajaxReminderCall = function(e) {
    "use strict";
    var edit_reminder_form;
    e.preventDefault();
    edit_reminder_form = $(".fixed-product-form");
    $.ajax({
      data: edit_reminder_form.serialize(),
      type: edit_reminder_form.attr("method"),
      url: edit_reminder_form.attr("action"),
      success: function(response) {
        var provider;
        edit_reminder_form.html(response);
        $(".fixed-product-form").submit(ajaxReminderCall);
        provider = $(select.fixedproviderselect).val();
        retrieveAccountType(provider);
      }
    });
  };

  ajaxOpeningCall = function() {
    "use strict";
    var opening_date_form;
    opening_date_form = $(".opening-date-form");
    return $.ajax({
      data: opening_date_form.serialize(),
      type: opening_date_form.attr("method"),
      url: opening_date_form.attr("action"),
      success: function() {
        return $.colorbox.close();
      }
    });
  };

  reloadPage = function() {
    "use strict";
    return location.reload(true);
  };

  rebindInputChange = function() {
    "use strict";
    if (typeof $("select.providerselect").select2 === "function") {
      $("select.providerselect").select2();
    }
    if (typeof $("select.productselect").select2 === "function") {
      $("select.productselect").select2();
    }
    if (typeof $("select.fixedproviderselect").select2 === "function") {
      $("select.fixedproviderselect").select2();
    }
    return $("select.productselect").empty();
  };

  body.on('change', "select.fixedproviderselect", function(event) {
    var account_type, provider;
    provider = $(event.target).val();
    account_type = parent.nextAll("select.account-type");
    account_type.empty();
    if (provider > 0) {
      return retrieveAccountType(provider);
    } else {
      return account_type.append("<option value =''>Please enter your details</option>");
    }
  });

  body.on('change', "select.providerselect", function(event) {
    var balance, parent_form, product_select, provider;
    provider = $(event.target).val();
    parent_form = $(event.target).closest(".product-form");
    balance = parent_form.find("#id_balance").val().replace(/,/g, "").replace(/£/g, "");
    product_select = $("select.productselect");
    product_select.select2();
    product_select.empty();
    if (provider > 0 && balance > 0) {
      retrieveProducts(provider, balance, parent_form);
    } else {
      product_select.append("<option value=''>Please enter your details</option>");
    }
    return product_select.select2("val", "");
  });

  body.on('keyup', '#id_balance', function(event) {
    var balance, event_target, parent_form, product_select, provider;
    event_target = $(event.target);
    parent_form = event_target.closest(".product-form");
    provider = $("select.providerselect").val();
    balance = event_target.val().replace(/,/g, "");
    product_select = $("select.productselect");
    product_select.empty();
    if (provider > 0 && balance > 0) {
      return retrieveProducts(provider, balance, parent_form);
    } else {
      return product_select.append("<option value=''>Please enter your details</option>");
    }
  });

  body.on('change', "select.productselect", function(event) {
    var id;
    id = $(event.target).val();
    return checkOpening(id);
  });

  $(document).ready(function() {
    "use strict";
    rebindInputChange();
    retrieveProducts();
    $(".variable-product-form").submit(ajaxPortfolioCall);
    $(".fixed-product-form").submit(ajaxReminderCall);
    return $(".opening-date-form").validate({
      submitHandler: function() {
        return ajaxOpeningCall();
      }
    });
  });

  body.on('hidden.bs.modal', function(event) {
    var event_target;
    event_target = $(event.target);
    if (event_target.is($('.js-threshold-form'))) {
      return null;
    } else {
      return location.reload(true);
    }
  });

}).call(this);

//# sourceMappingURL=portfolio.js.map
