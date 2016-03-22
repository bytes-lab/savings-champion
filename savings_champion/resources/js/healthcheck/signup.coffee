checkOpening = (optionValue, parent) ->
  "use strict"
  $.post "/best-buys/ajax/checkopening/",
    productID: optionValue
  , (data) ->
    if data is "True"
      $(parent).find(".opening-date-group").show()
      $(parent).find(".datestyle").addClass "required"
      $(parent).find(".datestyle").attr "min", "1"
    else
      $(parent).find(".datestyle").removeClass "required"
      $(parent).find(".datestyle").removeAttr "min"
      $(parent).find(".opening-date-group").hide()

retrieveProducts = (provider, balance, parent) ->
  "use strict"
  $.get "/best-buys/ajax/retrievepersonalproducts/",
    providerid: provider
    balanceval: balance
  , (data) ->
    options = ""
    $.each data, (i) ->
      options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>"
    checkOpening data[0][0], $(parent).nextAll(".variable-section")  if data[0] isnt `undefined`
    $(parent).nextAll(".variable-section").find("select.productselect").append options
    $(parent).nextAll(".variable-section").find("select.productselect").select2 "enable", true



rebindInputChange = ->
  "use strict"

  # Document.ready can't handle the additional fields
  $("select.providerselect").unbind "change"
  $("select.balanceinput").unbind "keyup"
  $("select.productselect").unbind "change"
  $(".switch").unbind "click"
  $("select.providerselect").change ->
    provider = $(this).val()
    balance = $(this).nextAll(".balanceinput").val().replace(/,/g, "")
    parent = $(this)
    $(this).nextAll(".balanceinput").attr "value", balance
    $(parent).nextAll(".variable-section").find("select.productselect").empty()
    $(parent).nextAll(".variable-section").find("select.productselect").select2 "enable", false
    if provider > 0 and balance > 0
      retrieveProducts provider, balance, parent
    else
      $(parent).nextAll(".variable-section").find("select.productselect").append "option value =\"0\">Please enter your details</option>"
    $(parent).nextAll(".variable-section").find("select.productselect").select2 "val", "0"

  $("select.balanceinput").keyup ->
    provider = $(this).prevAll(".providerselect").val()
    balance = $(this).val().replace(/,/g, "")
    parent = $(this)
    value = $(this).attr("value")
    if $(parent).nextAll(".variable-section").find("select.productselect").val() < 1
      $(parent).nextAll(".variable-section").find("select.productselect").empty()
      $(parent).nextAll(".variable-section").find("select.productselect").select2 "enable", false
      if provider > 0 and balance > 0
        retrieveProducts provider, balance, parent
        $(this).attr "value", balance
      else
        $(parent).nextAll(".variable-section").find("select.productselect").append "option value =\"0\">Please enter your details</option>"
      $(this).attr "value", balance
      $(parent).nextAll(".variable-section").find("select.productselect").select2 "val", "0"

  $("select.productselect").change ->
    id = $(this).val()
    checkOpening id, $(this).parent()

  $(".switch.to-variable").click ->
    $(this).parent().next(".fixedindicator").val "false"
    $(this).parent().nextAll(".fixed-section").hide()
    $(this).parent().nextAll(".variable-section").show()
    $(this).parent().nextAll("#variable-rate-message").show()
    $(this).parent().nextAll("#fixed-rate-message").hide()
    $(this).addClass "selected"
    $(this).text "Variable Rate Product"
    $(this).next(".switch.to-fixed").removeClass("selected").text "Click to add Fixed Rate Product"
    false

  $(".switch.to-fixed").click ->
    $(this).parent().next(".fixedindicator").val "true"
    $(this).parent().nextAll(".variable-section").hide()
    $(this).parent().nextAll(".fixed-section").show()
    $(this).parent().nextAll("#fixed-rate-message").show()
    $(this).parent().nextAll("#variable-rate-message").hide()
    $(this).addClass "selected"
    $(this).text "Fixed Rate Product"
    $(this).prev(".switch.to-variable").removeClass("selected").text "Click to add Variable Rate Product"
    false

$(document).ready ->
  "use strict"
  $.ajaxSetup beforeSend: (xhr, settings) ->
    getCookie = (name) ->
      cookie = undefined
      cookieValue = undefined
      cookies = undefined
      i = undefined
      cookieValue = null
      if document.cookie and document.cookie isnt ""
        cookies = document.cookie.split(";")
        i = 0
        while i < cookies.length
          cookie = $.trim(cookies[i])

          # Does this cookie string begin with the name we want?
          if cookie.substring(0, name.length + 1) is (name + "=")
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          i++
      cookieValue

    # Only send the token to relative URLs i.e. locally.
    xhr.setRequestHeader "X-CSRFToken", getCookie("csrftoken")  unless /^http:.*/.test(settings.url) or /^https:.*/.test(settings.url)

  $(".add-more").click ->
    $(".additional-form").find("select.select2-offscreen").each (index, element) ->
      $(element).select2 "destroy"

    form_count = parseInt($("[name=extra_field_count]").val())
    provider_options = $("#id_provider > option").clone()
    op_months = $("#id_opening_date_month > option").clone()
    op_years = $("#id_opening_date_year > option").clone()
    account_type_options = $("#id_account_type > option").clone()
    maturity_months = $("#id_maturity_date_month > option").clone()
    maturity_years = $("#id_maturity_date_year > option").clone()
    form_fields = []
    additional_form = $(".additional-form")
    form_fields[0] = additional_form.find("select.providerselect")
    form_fields[1] = additional_form.find(".balanceinput")
    form_fields[2] = additional_form.find("select.productselect")
    form_fields[3] = additional_form.find(".opening_month")
    form_fields[4] = additional_form.find(".opening_year")
    form_fields[5] = additional_form.find(".accounttype")
    form_fields[6] = additional_form.find(".maturity_month")
    form_fields[7] = additional_form.find(".maturity_year")
    form_fields[8] = additional_form.find(".fixedindicator")
    $.each form_fields, (index, value) ->
      name = $(value).attr("name")
      $(value).attr "name", name + "_field_" + form_count
      $(value).attr "id", name + "_field_" + form_count

    $(form_fields[0]).append provider_options
    $(form_fields[3]).append op_months
    $(form_fields[4]).append op_years
    $(form_fields[5]).append account_type_options
    $(form_fields[6]).append maturity_months
    $(form_fields[7]).append maturity_years
    additional = additional_form.html()
    $(this).before additional

    #Put the form fields back to original before chosen
    $.each form_fields, (index, value) ->
      original = $(value).attr("original")
      $(value).empty()
      $(value).attr "name", original
      $(value).attr "id", original

    $("#provider_field_" + form_count).select2 width: "100%"
    $("#product_field_" + form_count).select2 width: "100%"
    $("#account_type_field_" + form_count).select2 width: "100%"
    form_count = form_count + 1
    $("[name=extra_field_count]").val form_count
    rebindInputChange()
    false

  rebindInputChange()