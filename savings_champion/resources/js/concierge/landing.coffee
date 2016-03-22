# using jQuery
getCookie = (name) ->
  if document.cookie and document.cookie isnt ""
    cookies = document.cookie.split(";")
    i = 0

    while i < cookies.length
      cookie = jQuery.trim(cookies[i])

      # Does this cookie string begin with the name we want?
      if cookie.substring(0, name.length + 1) is (name + "=")
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      i++
  cookieValue

csrfSafeMethod = (method) ->

  # these HTTP methods do not require CSRF protection
  /^(GET|HEAD|OPTIONS|TRACE)$/.test method
csrftoken = getCookie("csrftoken")
$.ajaxSetup beforeSend: (xhr, settings) ->
  xhr.setRequestHeader "X-CSRFToken", csrftoken  if not csrfSafeMethod(settings.type) and not @crossDomain
  return

if ($(".js-form-part").length > 0)
  formset = $(".js-form-part").djangoFormset(
    deleteButtonText: '<span class="glyphicon glyphicon-remove"></span> Remove account'
  );
  $('body').on 'click', '.add-pool', (event) ->
    formset.addForm();
    return

$('body').on 'click', '.js-tool-index', (event) ->
  event_target = $(event.target)
  form = event_target.siblings('form')
  event_target.removeClass('btn-info')
  event_target.addClass('btn-danger')
  event_target.val('Saving...')
  form.submit()
  return

$('body').on 'click', '.js-stage-one', (event) ->
  event_target = $(event.target)
  form = event_target.siblings('form')
  event_target.removeClass('btn-info')
  event_target.addClass('btn-danger')
  event_target.val('Saving...')
  form.submit()
  return

$('body').on('shown.bs.tab', 'a[data-toggle="tab"]', (e) ->
  current_tab = $(e.target)
  previous_tab = $(e.relatedTarget)
  accountType = current_tab.data('accountType')
  if accountType in ['personal', 'business', 'charity']
    $('.js-concierge-tool').show()
    $('.js-concierge-tool-unavailable').hide()
  else
    $('.js-concierge-tool').hide()
    $('.js-concierge-tool-unavailable').show()
  return
)

task_update = (data, textStatus, jqXHR) ->
  if(typeof data == "object")
    setTimeout(ajax_task_check, 2000)

  else
    $('.loading').replaceWith(data)
  return

task_failed = (data, textStatus, jqXHR) ->
  return

ajax_task_check = ->
  if ($(".loading").length = 0)
    return
  loading_div = $(".loading")
  url = loading_div.data('url')
  worst_case_task_id = loading_div.data('worstCaseTaskId')
  best_case_task_id = loading_div.data('bestCaseTaskId')
  $.ajax(
    url,
    'data':
      'worst_engine_output_task_id': worst_case_task_id,
      'best_engine_output_task_id': best_case_task_id,
    'method': 'post',
    'success': task_update,
    'error': task_failed
  )
  return

if ($(".loading").length > 0)
  ajax_task_check()
