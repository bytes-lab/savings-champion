reloadPage = ->
  "use strict"
  
  window.setTimout ->
    location.reload false
    null
  , 500
  null

hideProductForm = ->
  "use strict"
  $(".js-variable-product-form").modal('hide')
  $(".js-fixed-product-form").modal('hide')

isotopeFilterSetUp = ->
  "use strict"
  $(".portfolios").isotope
    layoutMode: 'straightDown'
    resizable: true
    animationEngine: "best-available"
    getSortData:
      balance: ($elem) ->
        Number $elem.find(".balance").text().replace(/[^0-9\.]+/g, "")

      provider: ($elem) ->
        $elem.find(".provider").text().replace RegExp(" ", "g"), ""

  $(".filters li").click ->
    $(this).parent().parent().find(".active").removeClass "active"
    selector = $(this).attr("data-filter")
    ga "send", "event", "Portfolio", "Filter", selector  if ga
    $(".portfolios").isotope filter: selector
    $(this).addClass "active"
    total = 0
    selector = ".product-box"  if selector is "*"
    $(selector).each ->
      total += Number($(this).find(".balance").text().replace(/[^0-9\.]+/g, ""))

    $(".portfolio-total").html "<p>Total: £" + total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + "</p>"
    false

  $(".balance-sort").click ->
    ascending = $(this).attr("asc")
    if ascending is true
      $(".portfolios").isotope
        sortBy: "balance"
        sortAscending: true

      $(this).attr "asc", "false"
    else
      $(".portfolios").isotope
        sortBy: "balance"
        sortAscending: false

      $(this).attr "asc", "true"
    false

  $(".provider-sort").click ->
    $(".portfolios").isotope
      sortBy: "provider"
      sortAscending: true

    false

  $(".reset-sort").click ->
    $(".portfolios").isotope
      sortBy: "original-order"
      sortAscending: true


    false
  return

$("body").on 'click', '.opening-date-click', ->
  $('.js-opening-date-form').modal('show')

$("body").on 'click', '.apply-now-click', ->
  $("#add-variable-products").hide()
  $("#add-fixed-products").show()
  ga "send", "event", "Portfolio", "Apply", "Clicked"  if ga

$("body").on 'click', '.updateportfolio', ->
  provider = $(this).closest(".product-box").find(".provider").text()
  product = $(this).closest(".product-box").find(".product").text()
  balance = $(this).closest(".product-box").find(".balance").text()
  balance = balance.replace(/,/g, "")
  id = $(this).closest(".product-box").find(".id-info").text()
  $(".editbalance").val balance
  $(".providerEditField").html provider
  $(".productEditField").html product
  $(".portfolioeditid").val id
  $(".js-edit-variable-product-form").modal('show')
  ga "send", "event", "Portfolio", "Variable", "Edit"  if ga


$("body").on 'click', ".print-button", ->
  ga "send", "event", "Portfolio", "Display", "Portfolio Printed"  if ga
  printContents 'portfolio-container'
  return false

$("body").on 'click', ".opening-date-click", ->
  id = $(this).closest(".product-box").find(".id-info").text()
  $("#id_portfolio_id").val id

$("body").on 'click', '.delete', ->
  $(".yes-link").attr "id", $(this).closest(".product-box").find(".id-info").text()
  maturity = $(this).closest(".product-box").find(".maturitydate").text()
  $(".yes-link").attr "is_fixed", true  if maturity
  $('.js-delete-box-modal').modal('show')

$("body").on 'click', '.yes-link', ->
  $.post "/best-buys/ajax/deleteportfolio/",
    id: $(this).attr("id")
    fixed: $(this).attr("is_fixed")
  , (data) ->
    $(".js-delete-box-modal-content").html data
    return
  ga "send", "event", "Portfolio", "Product", "Deleted"  if ga
  false

$("body").on 'click', '.updatereminder', ->
  provider = $(this).closest(".product-box").find(".provider").text()
  product = $(this).closest(".product-box").find(".account-type").text()
  balance = $(this).closest(".product-box").find(".balance").text()
  rate = $(this).closest(".product-box").find(".rate").text()
  balance = balance.replace(/,/g, "")
  id = $(this).closest(".product-box").find(".id-info").text()
  $("#reminder_balance").val balance
  $("#id_rate").val rate
  $(".providerEditField").html provider
  $(".productEditField").html product
  $("#reminder_id").val id
  $(".js-edit-fixed-product-form").modal('show')
  ga "send", "event", "Portfolio", "Fixed", "Edit"  if ga

$("body").on 'click', '.js-add-variable-product-button', ->
  $('.js-variable-product-form').modal('show')
  ga "send", "event", "Portfolio", "Variable", "New"  if ga

$("body").on 'click', '.js-add-fixed-product-button', ->
  $('.js-fixed-product-form').modal('show')
  ga "send", "event", "Portfolio", "Fixed", "New"  if ga

$("body").on 'click', '.arrow > img', (event) ->
  console.log('arrow clicked')
  event_target = $(event.target)
  product_box = event_target.closest(".product-box")
  closed = event_target.attr "closed"
  console.log(closed)
  if closed is 'true'
    console.log('Evaluated as closed')
    product_box.find(".panel-body").show()
    event_target.attr "closed", 'false'
    product_box.find('.arrow').find(".closed-arrow-img").hide()
    product_box.find('.arrow').find(".expanded-arrow-img").show()

  else
    console.log('Evaluated as not closed')
    product_box.find(".panel-body").hide()
    event_target.attr "closed", 'true'
    product_box.find('.arrow').find(".closed-arrow-img").show()
    product_box.find('.arrow').find(".expanded-arrow-img").hide()
  $(".portfolios").isotope "reLayout"
  return false

$("body").on "click", ".close-all", ->
  ga "send", "event", "Portfolio", "Display", "All minimised"  if ga
  $(".product-box > .panel-body").hide()
  $(".arrow").attr "closed", true
  $(".expanded-arrow-img").hide()
  $(".closed-arrow-img").show()
  $(".closed-balance").show()
  $(".closed-maturity-date").show()
  $(".portfolios").isotope "reLayout"
  return false

$("body").on "click", ".expand-all", ->
  ga "send", "event", "Portfolio", "Display", "All expanded"  if ga
  $(".product-box > .panel-body").show()
  $(".arrow").attr "closed", false
  $(".closed-arrow-img").hide()
  $(".expanded-arrow-img").show()
  $(".closed-balance").hide()
  $(".closed-maturity-date").hide()
  $(".portfolios").isotope "reLayout"
  return false

printContents = (id) ->
  "use strict"
  $(".portfolios").isotope('destroy');
  window.print()
  false

load_portfolio = ->
  "use strict"
  isotopeFilterSetUp()
  $('.js-threshold-form').modal('show')
  return

$(document).ready load_portfolio

handle_threshold_save = (data, textStatus, jqXHR) ->
  if data.status == 'success'
    $('.js-threshold-form').modal('hide')
  else
    $('.js-threshold-form').find('.form-group').addClass('has-error')
  return

$('body').on 'click', '.js-threshold-form-save', (event) ->
  event_target = $(event.target)
  url = event_target.data('url')
  form = $('.js-threshold-form').find('form')
  $.post(url, form.serialize(), handle_threshold_save)
  return
