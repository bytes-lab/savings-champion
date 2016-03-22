body = $('body')
csrftoken = $.cookie('csrftoken')

csrfSafeMethod = (method) ->

  # these HTTP methods do not require CSRF protection
  /^(GET|HEAD|OPTIONS|TRACE)$/.test method

$.ajaxSetup
  crossDomain: false # obviates need for sameOrigin test
  cache: false
  beforeSend: (xhr, settings) ->
    xhr.setRequestHeader "X-CSRFToken", csrftoken  unless csrfSafeMethod(settings.type)
    return

$('form').on 'submit', ->
  event.preventDefault()
  return

manage_user_success = (data, textStatus, jqXHR) ->
#  console.log(data);
  $('.engine-root').html(data)
  return

body.on 'click', 'input[name="manage-user"]', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  data_source = event_target.closest 'form'
#  console.log data_url
  $.post data_url, $(data_source).serialize(), manage_user_success, 'html'
  return

update_user_options_success = (data, textStatus, jqXHR) ->
#  console.log(data);
  $('.user-options').html(data)
  return

body.on 'click', 'input[name="update-user-options"]', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  data_source = event_target.closest 'form'
#  console.log data_url
  $.post data_url, $(data_source).serialize(), update_user_options_success, 'html'
  return

add_pool_success = (data, textStatus, jqXHR) ->
#  console.log(data);
  $('.js-user-pools').html(data)
  return

body.on 'click', 'input[name="add-pool"]', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  $.post data_url, '', add_pool_success, 'html'
  return

update_pool_success = (data, textStatus, jqXHR) ->
#  console.log(data);
  $('.js-user-pools').html(data)
  return

body.on 'click', 'input[name="save-pool-changes"]', (event) ->
  event_target = $(event.target)
  data_source = event_target.siblings 'form'
  data_url = event_target.data 'action'
  $.post data_url, $(data_source).serialize(), update_pool_success, 'html'
  return false

update_concierge_output = (data, textStatus, jqXHR) ->
#  console.log(data);
  $('.js-engine-output').html(data)
  get_pools()
  get_existing_products()
  return

run_concierge_engine = () ->
  event_target = $('input.js-concierge-engine-run')
  event_target.removeClass('btn-success')
  event_target.addClass('btn-info')
  event_target.val('Running')
  data_url = $('.js-engine-output').data 'url'
  $.post data_url, '', update_concierge_output, 'html'
  return


run_concierge_engine_best_case = () ->
  event_target = $('input.js-concierge-engine-run-best-case')
  event_target.removeClass('btn-danger')
  event_target.addClass('btn-info')
  event_target.val('Running')
  data_url = $('.js-engine-output').data 'urlBestCase'
  $.post data_url, '', update_concierge_output, 'html'
  return

body.on 'click', 'input.js-concierge-engine-run', run_concierge_engine
body.on 'click', 'input.js-concierge-engine-run-best-case', run_concierge_engine_best_case

remove_product_success = (data, textStatus, jqXHR) ->
  update_required_products()
  run_concierge_engine()
  $('.js-removed-accounts').html data
  return

body.on 'click', 'input.js-remove-product', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  master_product = event_target.data 'masterProduct'
  concierge_user = event_target.data 'conciergeUser'
  event_target.removeClass 'btn-danger'
  event_target.addClass 'btn-info'
  event_target.val 'Removed'
  $.post data_url,
    'master_product': master_product
    'concierge_user': concierge_user
  ,remove_product_success, 'html'
  return

restore_removed_product_success = (data, textStatus, jqXHR) ->
  $('.js-removed-accounts').html data
  return

body.on 'click', 'input.js-allow-removed-product', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  product = event_target.data 'removedProduct'
  concierge_user = event_target.data 'conciergeUser'
  event_target.removeClass 'btn-success'
  event_target.addClass 'btn-info'
  event_target.val 'Restored'
  $.post data_url,
    'removed_product': product
    'concierge_user': concierge_user
  , restore_removed_product_success, 'html'
  return

remove_allowed_product_success = (data, textStatus, jqXHR) ->
  $('.js-allowed-accounts').html data
  return

body.on 'click', 'input.js-allow-product', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  product = event_target.data 'masterProduct'
  concierge_user = event_target.data 'conciergeUser'
  restriction = event_target.data 'restriction'
  event_target.removeClass 'btn-success'
  event_target.addClass 'btn-info'
  event_target.val 'Allowed'
  $.post data_url,
    'product': product
    'concierge_user': concierge_user
    'restriction': restriction
  , remove_allowed_product_success, 'html'
  return

body.on 'click', 'input.js-remove-allowed-account', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  allowed_product = event_target.data 'allowedProduct'
  concierge_user = event_target.data 'conciergeUser'
  event_target.removeClass 'btn-danger'
  event_target.addClass 'btn-info'
  event_target.val 'Disallowed'
  $.post data_url,
    'allowed_product': allowed_product
    'concierge_user': concierge_user
  , remove_allowed_product_success, 'html'
  return


body.on 'click', 'input.js-required-product', (event) ->
  event_target = $(event.target)
  url = event_target.data 'url'
  concierge_user = event_target.data 'conciergeUser'
  master_product = event_target.data 'masterProduct'
  balance = event_target.data 'productBalance'
  event_target.removeClass 'btn-success'
  event_target.addClass 'btn-info'
  event_target.val 'Pinned'
  $.post url,
    'concierge_user': concierge_user
    'master_product': master_product
    'balance':balance
  , remove_required_product_success, 'html'
  return

remove_required_product_success = (data, textStatus, jqXHR) ->
  update_removed_products()
  $('.js-required-accounts').html data
  return

body.on 'click', 'input.js-remove-required-account', (event) ->
  event_target = $(event.target)
  url = event_target.data 'url'
  concierge_user = event_target.data 'conciergeUser'
  master_product = event_target.data 'product'
  $.post url,
    'concierge_user': concierge_user
    'product': master_product
  , remove_required_product_success, 'html'
  return

update_required_products_success = (data, textStatus, jqXHR) ->
  $('div.js-require-product-popup-modal').modal('hide')
  body.removeClass('modal-open')
  $('.modal-backdrop.fade.in').removeClass('modal-backdrop')
  $('.js-required-accounts').html data

  return

update_required_products = ->
  data_url = $('.js-required-accounts').data 'url'
  concierge_user = $('.js-required-accounts').data 'conciergeUser'
  $.get data_url,
    'concierge_user': concierge_user
  , update_required_products_success, 'html'
  return

update_removed_products_success = (data, textStatus, jqXHR) ->
  $('.js-removed-accounts').html data
  return

update_removed_products = ->
  data_url = $('.js-removed-accounts').data 'url'
  concierge_user = $('.js-removed-accounts').data 'conciergeUser'
  $.get data_url,
    'concierge_user': concierge_user
    , update_removed_products_success, 'html'
  return

body.on 'click', '.js-toggle-engine-log', ->
  $('.js-engine-log').toggle()
  return

body.on 'click', 'button.js-require-product-popup', ->
  $('div.js-require-product-popup-modal').modal 'show'
  return

update_products_list = (data, textStatus, jqXHR) ->
#  console.log(data)
  $('#id_products').empty()
  for product in data
    option_tag = $('<option>')
    option_tag.val(product[0])
    option_tag.text(product[1])
    $('#id_products').append(option_tag)
  return

request_products_list = (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  provider_id = event_target.val()
  $.get data_url, event_target.serialize(), update_products_list, 'json'
  return

body.on 'change', '#id_provider', request_products_list

submit_required_product = (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  modal_form = $('div.js-require-product-popup-modal').find('form')
  Pace.ignore ->
    $.post data_url, modal_form.serialize(), update_required_products_success, 'html'
    return
  return

body.on 'click', 'button.js-require-product-popup-submit', submit_required_product

delete_existing_product_success = (data, textStatus, jqXHR) ->
  $('.js-existing-products').html data
  return

delete_existing_product = (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  $.post data_url, '', delete_existing_product_success, 'html'
  return

body.on 'click', '.js-delete-existing-product', delete_existing_product

add_existing_product = (event) ->
  $('.js-existing-product-popup-modal').modal 'show'
  return

body.on 'click', '.js-add-existing-product-popup', add_existing_product

update_products_dropdown = (data, textStatus, jqXHR) ->
  $('.js-add-existing-products-form #id_product').empty()
  for product in data
    option_tag = $('<option>')
    option_tag.val(product[0])
    option_tag.text(product[1])
    $('.js-add-existing-products-form #id_product').append(option_tag)
  return

retrieve_products = (event) ->
  event_target = $(event.target)
  data_url = event_target.data('url')
  $.get data_url,
    'provider': event_target.val()
  , update_products_dropdown, 'json'
  return

body.on 'change', '.js-add-existing-products-form #id_provider', retrieve_products

update_existing_products_html = (data, textStatus, jqXHR) ->
  $('.js-existing-products').html data
  return

update_existing_products = (event) ->
  event_target = $(event.target)
  forms = $('.js-add-existing-products-form')
  data_url = forms.attr('action')
  data_concierge_user_id = event_target.data('concierge_user_id')
  form_data = forms.serialize()
  $('.js-existing-product-popup-modal').modal 'hide'
  $.post data_url,
    form_data
  , update_existing_products_html, 'html'
  return

body.on 'click', '.js-add-existing-product', update_existing_products

get_pools = ->
  data_url = $('.js-user-pools').data('url')
  $.get data_url, '', update_pool_success, 'html'
  return

success_get_existing_products = (data, textStatus, jqXHR)->
  $('.js-existing-products').html data
  return

get_existing_products = ->
  data_url = $('.js-existing-products').data('url')
  concierge_user_id = $('.js-existing-products').data('conciergeUserId')
  $.get data_url,
    'concierge_user_id': concierge_user_id
  , success_get_existing_products, 'html'
  return

selectElementContents = (el) ->
  body = document.body
  if document.createRange and window.getSelection
    range = document.createRange()
    sel = window.getSelection()
    sel.removeAllRanges()
    try
      range.selectNodeContents el
      sel.addRange range
    catch e
      range.selectNode el
      sel.addRange range
  else if body.createTextRange
    range = body.createTextRange()
    range.moveToElementText el
    range.select()
  false

body.on 'click', '.js-copy-excluded-products', ->
  select_target = document.getElementsByClassName 'js-excluded-products-table'
  if select_target.length > 0
    selectElementContents(select_target[0])
  return false

