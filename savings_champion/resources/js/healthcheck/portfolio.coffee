body = $('body')

$.ajaxSetup beforeSend: (xhr, settings) ->
  getCookie = (name) ->
    if document.cookie and document.cookie isnt ""
      cookies = document.cookie.split(";")
      i = 0
      if typeof String::trim isnt "function"
        String::trim = ->
          @replace /^\s+|\s+$/g, ""
      while i < cookies.length
        cookie = cookies[i].trim()

        # Does this cookie string begin with the name we want?
        if cookie.substring(0, name.length + 1) is (name + "=")
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        i++
    cookieValue

  # Only send the token to relative URLs i.e. locally.
  xhr.setRequestHeader "X-CSRFToken", getCookie("csrftoken")  unless /^http:.*/.test(settings.url) or /^https:.*/.test(settings.url)

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

retrieveProducts = (provider, balance, parent) ->
  "use strict"
  product_select = $("select.productselect")
  product_select.select2()
  product_select.empty()
  product_select.select2 'data',
    id: '-1'
    text: 'Loading'
  $.get "/best-buys/ajax/retrievepersonalproducts/",
    providerid: provider
    balanceval: balance
  , (data) ->
    options = "<option value=''>Please select a product</option>"
    $.each data, (i) ->
      options += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>"

    checkOpening data[0][0]  if data[0] isnt `undefined`
    product_select.empty()
    product_select.append options
    product_select.select2 "enable", true
    product_select.select2 'data',
      id: '0'
      text: 'Please select a product'

retrieveAccountType = (provider) ->
  "use strict"
  edit_reminder_form = $(".fixed-product-form")
  account_type_select = edit_reminder_form.find("select.account-type")
  account_type_select.empty()
  account_type_select.append "<option value=''>Loading</option>"
  $.get "/best-buys/ajax/retrievefixedchoices/",
    providerid: provider
  , (data) ->
    account_type_select.empty()
    options = "<option value=''>Please select an account type</option>"
    $.each data, (i) ->
      options += "<option value=''" + data[i][0] + "'>" + data[i][1] + "</option>"
    account_type_select.append options

ajaxPortfolioCall = (e)-> # catch the form's submit event
  "use strict"
  e.preventDefault()
  edit_portfolio_form = $(".variable-product-form")
  $.ajax # create an AJAX call...
    data: edit_portfolio_form.serialize() # get the form data
    type: edit_portfolio_form.attr("method") # GET or POST
    url: edit_portfolio_form.attr("action") # the file to call
    success: (response) -> # on success..
      edit_portfolio_form.html response # update the DIV
      $(".variable-product-form").submit(ajaxPortfolioCall)
      providerselect = $('select.providerselect')
      provider = providerselect.val()
      parent_form = providerselect.closest(".product-form")
      balance = parent_form.find("#id_balance").val().replace(/,/g, "").replace(/£/g, "")
      retrieveProducts(provider, balance, parent_form)
      return
  return

ajaxReminderCall = (e)-> # catch the form's submit event
  "use strict"
  e.preventDefault()
  edit_reminder_form = $(".fixed-product-form")
  $.ajax # create an AJAX call...
    data: edit_reminder_form.serialize() # get the form data
    type: edit_reminder_form.attr("method") # GET or POST
    url: edit_reminder_form.attr("action") # the file to call
    success: (response) -> # on success..
      edit_reminder_form.html response # update the DIV
      $(".fixed-product-form").submit(ajaxReminderCall)
      provider = $(select.fixedproviderselect).val()
      retrieveAccountType provider
      return
  return

ajaxOpeningCall = -> # catch the form's submit event
  "use strict"
  opening_date_form = $(".opening-date-form")
  $.ajax # create an AJAX call...
    data: opening_date_form.serialize() # get the form data
    type: opening_date_form.attr("method") # GET or POST
    url: opening_date_form.attr("action") # the file to call
    success: -> # on success..
      $.colorbox.close() # update the DIV

reloadPage = ->
  "use strict"
  location.reload true

rebindInputChange = ->
  "use strict"
  if typeof $("select.providerselect").select2 == "function"
    $("select.providerselect").select2()
  if typeof $("select.productselect").select2 == "function"
    $("select.productselect").select2()
  if typeof $("select.fixedproviderselect").select2 == "function"
    $("select.fixedproviderselect").select2()
  $("select.productselect").empty()

body.on 'change', "select.fixedproviderselect", (event)->
  provider = $(event.target).val()
  account_type = parent.nextAll("select.account-type")
  account_type.empty()
  if provider > 0
    retrieveAccountType provider
  else
    account_type.append "<option value =''>Please enter your details</option>"

body.on 'change', "select.providerselect", (event) ->
  provider = $(event.target).val()
  parent_form = $(event.target).closest(".product-form")
  balance = parent_form.find("#id_balance").val().replace(/,/g, "").replace(/£/g, "")
  product_select = $("select.productselect")
  product_select.select2()
  product_select.empty()
  if provider > 0 and balance > 0
    retrieveProducts provider, balance, parent_form
  else
    product_select.append "<option value=''>Please enter your details</option>"
  product_select.select2 "val", ""

body.on 'keyup', '#id_balance', (event) ->
  event_target = $(event.target)
  parent_form = event_target.closest(".product-form")
  provider = $("select.providerselect").val()
  balance = event_target.val().replace(/,/g, "")
  product_select = $("select.productselect")
  product_select.empty()
  if provider > 0 and balance > 0
    retrieveProducts provider, balance, parent_form
  else
    product_select.append "<option value=''>Please enter your details</option>"

body.on 'change', "select.productselect", (event) ->
  id = $(event.target).val()
  checkOpening id

$(document).ready ->
  "use strict"
  rebindInputChange()
  retrieveProducts()
  $(".variable-product-form").submit(ajaxPortfolioCall)
  $(".fixed-product-form").submit(ajaxReminderCall)
#  $(".variable-product-form").validate
#    submitHandler: ->
#      #this runs when the form validated successfully
#      ajaxPortfolioCall() #submit it the form
#
#  $(".fixed-product-form").validate
#    submitHandler: ->
#      #this runs when the form validated successfully
#      ajaxReminderCall() #submit it the form

  $(".opening-date-form").validate
    submitHandler: ->
      #this runs when the form validated successfully
      ajaxOpeningCall() #submit it the form

body.on 'hidden.bs.modal', (event)->
  event_target = $(event.target)
  if event_target.is($('.js-threshold-form')) then null else location.reload true
