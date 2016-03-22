(function() {
  var checkOpening, rebindInputChange, retrieveProducts;

  checkOpening = function(optionValue, parent) {
    "use strict";
    return $.post("/best-buys/ajax/checkopening/", {
      productID: optionValue
    }, function(data) {
      if (data === "True") {
        $(parent).find(".opening-date-group").show();
        $(parent).find(".datestyle").addClass("required");
        return $(parent).find(".datestyle").attr("min", "1");
      } else {
        $(parent).find(".datestyle").removeClass("required");
        $(parent).find(".datestyle").removeAttr("min");
        return $(parent).find(".opening-date-group").hide();
      }
    });
  };

  retrieveProducts = function(provider, balance, parent) {
    "use strict";
    return $.get("/best-buys/ajax/retrievepersonalproducts/", {
      providerid: provider,
      balanceval: balance
    }, function(data) {
      var options;
      options = "";
      $.each(data, function(i) {
        return options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>";
      });
      if (data[0] !== undefined) {
        checkOpening(data[0][0], $(parent).nextAll(".variable-section"));
      }
      $(parent).nextAll(".variable-section").find("select.productselect").append(options);
      return $(parent).nextAll(".variable-section").find("select.productselect").select2("enable", true);
    });
  };

  rebindInputChange = function() {
    "use strict";
    $("select.providerselect").unbind("change");
    $("select.balanceinput").unbind("keyup");
    $("select.productselect").unbind("change");
    $(".switch").unbind("click");
    $("select.providerselect").change(function() {
      var balance, parent, provider;
      provider = $(this).val();
      balance = $(this).nextAll(".balanceinput").val().replace(/,/g, "");
      parent = $(this);
      $(this).nextAll(".balanceinput").attr("value", balance);
      $(parent).nextAll(".variable-section").find("select.productselect").empty();
      $(parent).nextAll(".variable-section").find("select.productselect").select2("enable", false);
      if (provider > 0 && balance > 0) {
        retrieveProducts(provider, balance, parent);
      } else {
        $(parent).nextAll(".variable-section").find("select.productselect").append("option value =\"0\">Please enter your details</option>");
      }
      return $(parent).nextAll(".variable-section").find("select.productselect").select2("val", "0");
    });
    $("select.balanceinput").keyup(function() {
      var balance, parent, provider, value;
      provider = $(this).prevAll(".providerselect").val();
      balance = $(this).val().replace(/,/g, "");
      parent = $(this);
      value = $(this).attr("value");
      if ($(parent).nextAll(".variable-section").find("select.productselect").val() < 1) {
        $(parent).nextAll(".variable-section").find("select.productselect").empty();
        $(parent).nextAll(".variable-section").find("select.productselect").select2("enable", false);
        if (provider > 0 && balance > 0) {
          retrieveProducts(provider, balance, parent);
          $(this).attr("value", balance);
        } else {
          $(parent).nextAll(".variable-section").find("select.productselect").append("option value =\"0\">Please enter your details</option>");
        }
        $(this).attr("value", balance);
        return $(parent).nextAll(".variable-section").find("select.productselect").select2("val", "0");
      }
    });
    $("select.productselect").change(function() {
      var id;
      id = $(this).val();
      return checkOpening(id, $(this).parent());
    });
    $(".switch.to-variable").click(function() {
      $(this).parent().next(".fixedindicator").val("false");
      $(this).parent().nextAll(".fixed-section").hide();
      $(this).parent().nextAll(".variable-section").show();
      $(this).parent().nextAll("#variable-rate-message").show();
      $(this).parent().nextAll("#fixed-rate-message").hide();
      $(this).addClass("selected");
      $(this).text("Variable Rate Product");
      $(this).next(".switch.to-fixed").removeClass("selected").text("Click to add Fixed Rate Product");
      return false;
    });
    return $(".switch.to-fixed").click(function() {
      $(this).parent().next(".fixedindicator").val("true");
      $(this).parent().nextAll(".variable-section").hide();
      $(this).parent().nextAll(".fixed-section").show();
      $(this).parent().nextAll("#fixed-rate-message").show();
      $(this).parent().nextAll("#variable-rate-message").hide();
      $(this).addClass("selected");
      $(this).text("Fixed Rate Product");
      $(this).prev(".switch.to-variable").removeClass("selected").text("Click to add Variable Rate Product");
      return false;
    });
  };

  $(document).ready(function() {
    "use strict";
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        var getCookie;
        getCookie = function(name) {
          var cookie, cookieValue, cookies, i;
          cookie = void 0;
          cookieValue = void 0;
          cookies = void 0;
          i = void 0;
          cookieValue = null;
          if (document.cookie && document.cookie !== "") {
            cookies = document.cookie.split(";");
            i = 0;
            while (i < cookies.length) {
              cookie = $.trim(cookies[i]);
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
    $(".add-more").click(function() {
      var account_type_options, additional, additional_form, form_count, form_fields, maturity_months, maturity_years, op_months, op_years, provider_options;
      $(".additional-form").find("select.select2-offscreen").each(function(index, element) {
        return $(element).select2("destroy");
      });
      form_count = parseInt($("[name=extra_field_count]").val());
      provider_options = $("#id_provider > option").clone();
      op_months = $("#id_opening_date_month > option").clone();
      op_years = $("#id_opening_date_year > option").clone();
      account_type_options = $("#id_account_type > option").clone();
      maturity_months = $("#id_maturity_date_month > option").clone();
      maturity_years = $("#id_maturity_date_year > option").clone();
      form_fields = [];
      additional_form = $(".additional-form");
      form_fields[0] = additional_form.find("select.providerselect");
      form_fields[1] = additional_form.find(".balanceinput");
      form_fields[2] = additional_form.find("select.productselect");
      form_fields[3] = additional_form.find(".opening_month");
      form_fields[4] = additional_form.find(".opening_year");
      form_fields[5] = additional_form.find(".accounttype");
      form_fields[6] = additional_form.find(".maturity_month");
      form_fields[7] = additional_form.find(".maturity_year");
      form_fields[8] = additional_form.find(".fixedindicator");
      $.each(form_fields, function(index, value) {
        var name;
        name = $(value).attr("name");
        $(value).attr("name", name + "_field_" + form_count);
        return $(value).attr("id", name + "_field_" + form_count);
      });
      $(form_fields[0]).append(provider_options);
      $(form_fields[3]).append(op_months);
      $(form_fields[4]).append(op_years);
      $(form_fields[5]).append(account_type_options);
      $(form_fields[6]).append(maturity_months);
      $(form_fields[7]).append(maturity_years);
      additional = additional_form.html();
      $(this).before(additional);
      $.each(form_fields, function(index, value) {
        var original;
        original = $(value).attr("original");
        $(value).empty();
        $(value).attr("name", original);
        return $(value).attr("id", original);
      });
      $("#provider_field_" + form_count).select2({
        width: "100%"
      });
      $("#product_field_" + form_count).select2({
        width: "100%"
      });
      $("#account_type_field_" + form_count).select2({
        width: "100%"
      });
      form_count = form_count + 1;
      $("[name=extra_field_count]").val(form_count);
      rebindInputChange();
      return false;
    });
    return rebindInputChange();
  });

}).call(this);

//# sourceMappingURL=signup.js.map
