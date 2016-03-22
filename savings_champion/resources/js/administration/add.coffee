# Does this cookie string begin with the name we want?

# Only send the token to relative URLs i.e. locally.
rebindInputChange = ->
  "use strict"
  $product_select = $("select.productselect")
  $provider_select = $("select.providerselect")
  $fixed_provider_select = $("select.fixedproviderselect")
  $provider_select.select2 width: "100%"
  $product_select.select2 width: "100%"
  $fixed_provider_select.select2 width: "100%"
  $product_select.empty()

  # Document.ready can't handle the additional fields
  $provider_select.on "change", ->
    provider = $(this).select2().val()
    balance = $(this).closest(".product-form").find(".balanceinput").val().replace(/,/g, "")
    parent = $(this)
    product_select = $(this).closest(".product-form").find("select.productselect")
    product_select.empty()
    product_select.append "<option value=\"0\">Please enter your details</option>"
    product_select.select2 "val", "0"
    if provider > 0 and balance > 0
      product_select.select2 "enable", false
      retrieveProducts provider, balance, parent
    return

  $(".balanceinput").on "keyup", ->
    provider = $(this).closest(".product-form").find(".providerselect").select2("val")
    balance = $(this).val().replace(/,/g, "")
    parent = $(this)
    product_select = $(this).closest(".product-form").find("select.productselect")
    product_select.empty()
    product_select.append "<option value=\"0\">Please enter your details</option>"
    product_select.select2 "val", "0"
    if provider > 0 and balance > 0
      product_select.select2 "enable", false
      retrieveProducts provider, balance, parent
      product_select.select2 "val", "0"
    return

  $provider_select.change ->
    id = $(this).val()
    checkOpening id
    return

  $fixed_provider_select.change ->
    provider = $(this).val()
    parent = $(this)
    account_type = $(this).closest(".product-form").find("select.account-type")
    account_type.empty()
    if provider > 0
      retrieveAccountType provider, parent
    else
      account_type.append "<option value =\"0\">Please enter your details</option>"
    return

  return
retrieveProducts = (provider, balance, parent) ->
  "use strict"
  $.get "/best-buys/ajax/retrievepersonalproducts/",
    providerid: provider
    balanceval: balance
  , (data) ->
    options = "\"<option value=\"0\">Please enter your details</option>"
    $.each data, (i) ->
      options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>"
      return

    checkOpening data[0][0]  if typeof (data[0]) isnt "undefined"
    product_select = parent.closest(".product-form").find("select.productselect")
    product_select.append options
    product_select.select2 "enable", true
    return

  return
retrieveAccountType = (provider, parent) ->
  "use strict"
  $.get "/best-buys/ajax/retrievefixedchoices/",
    providerid: provider
  , (data) ->
    options = ""
    $.each data, (i) ->
      options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>"
      return

    parent.closest(".product-form").find("select.account-type").append options
    return

  return
checkOpening = (optionValue) ->
  "use strict"
  $.post "/best-buys/ajax/checkopening/",
    productID: optionValue
  , (data) ->
    opening_date_group = $(".opening-date-group")
    if data is "True"
      opening_date_group.show()
      opening_date_group.find(".datestyle").addClass "required"
      opening_date_group.find(".datestyle").attr "min", "1"
    else
      opening_date_group.find(".datestyle").removeClass "required"
      opening_date_group.find(".datestyle").removeAttr "min"
      opening_date_group.hide()
    return

  return
ajaxPortfolioCall = -> # catch the form's submit event
  "use strict"
  edit_portfolio_form = $("#editportfolioform")
  $.ajax # create an AJAX call...
    data: edit_portfolio_form.serialize() # get the form data
    type: edit_portfolio_form.attr("method") # GET or POST
    url: edit_portfolio_form.attr("action") # the file to call
    success: (response) -> # on success..
      $("#editportfolioform").html response # update the DIV
      $("#add-variable-products").colorbox.resize()
      return

  return
ajaxReminderCall = -> # catch the form's submit event
  "use strict"
  edit_reminder_form = $("#editreminderform")
  $.ajax # create an AJAX call...
    data: edit_reminder_form.serialize() # get the form data
    type: edit_reminder_form.attr("method") # GET or POST
    url: edit_reminder_form.attr("action") # the file to call
    success: (response) -> # on success..
      edit_reminder_form.html response # update the DIV
      $("#add-fixed-products").colorbox.resize()
      return

  return
ajaxOpeningCall = -> # catch the form's submit event
  "use strict"
  opening_date_form = $(".opening-date-form")
  $.ajax # create an AJAX call...
    data: opening_date_form.serialize() # get the form data
    type: opening_date_form.attr("method") # GET or POST
    url: opening_date_form.attr("action") # the file to call
    success: (response) -> # on success..
      $.colorbox.close() # update the DIV
      return

  return
reloadPage = ->
  "use strict"
  location.reload true
  return
$(document).ready ->
  "use strict"
  $.ajaxSetup beforeSend: (xhr, settings) ->
    getCookie = (name) ->
      cookieValue = null
      if document.cookie and document.cookie isnt ""
        cookies = document.cookie.split(";")
        i = 0

        while i < cookies.length
          cookie = jQuery.trim(cookies[i])
          if cookie.substring(0, name.length + 1) is (name + "=")
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          i++
      cookieValue
    xhr.setRequestHeader "X-CSRFToken", getCookie("csrftoken")  unless /^http:.*/.test(settings.url) or /^https:.*/.test(settings.url)
    return

  $(".add-products-button").click ->
    $("#add-fixed-products").hide()
    $("#add-variable-products").show()
    return

  $(".fixed-click").click ->
    $("#add-variable-products").hide()
    $("#add-fixed-products").show()
    return

  rebindInputChange()
  $("select.providerselect").change ->
    window.console.log "Provider changes"
    return

  $(".balanceinput").on "keyup", ->
    window.console.log "Balance changes"
    return

  $("select.productselect").change ->
    window.console.log "Product changes"
    return

  return
