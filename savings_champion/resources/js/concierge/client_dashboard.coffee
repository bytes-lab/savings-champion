csrftoken = $.cookie('csrftoken');

csrfSafeMethod = (method) ->

  # these HTTP methods do not require CSRF protection
  /^(GET|HEAD|OPTIONS|TRACE)$/.test method

$.ajaxSetup
  crossDomain: false # obviates need for sameOrigin test
  cache: false
  beforeSend: (xhr, settings) ->
    xhr.setRequestHeader "X-CSRFToken", csrftoken  unless csrfSafeMethod(settings.type)
    return

client_details_success = (data, textStatus, jqXHR) ->
  $('.js-client-details').html data
  return

client_details = () ->
  data_source = $('.js-client-details')
  data_url = data_source.data 'url'
  client_id = data_source.data 'clientId'
  $.post data_url, client_id: client_id, client_details_success, 'html'
  return

client_notes_success = (data, statusText, jqXHR) ->
  $('.js-client-notes').html data
  return

client_notes = () ->
  data_source = $('.js-client-notes-form')
  data_url = data_source.attr 'action'
  $.post data_url, data_source.serialize(), client_notes_success, 'html'
  return

load_concierge_engine_success = (data, textStatus, jqXHR) ->
  $('.engine-root').html(data)
  return

load_concierge_engine = (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  $.get data_url, '', load_concierge_engine_success, 'html'
  return

save_client_details_success = (data) ->
  $('#lead-capture').html data
  return

save_client_details = (event) ->
  event_target = $(event.target)
  event_target.removeClass 'btn-success'
  event_target.addClass 'btn-info'
  event_target.val 'Saving'
  parent_form = $('#lead-capture').find 'form'
  data_url = event_target.data 'url'
  $.post data_url, parent_form.serialize() , save_client_details_success, 'html'
  return

$('body').on 'click', 'input[name="update-user-options"]', client_details
$('body').on 'click', 'input[name="update-user-notes"]', client_notes
$('body').on 'click', 'input.js-load-concierge-engine', load_concierge_engine
$('body').on 'click', 'input.js-save-client-details', save_client_details