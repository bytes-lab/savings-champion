
ajax_success = (data, textStatus, jqXHR) ->
  $('.js-news-appearances').html data
  return

ajax_failed = ->
  return

ajax_over = ->
  $('body, html').animate
    scrollTop: 0
  , 800
  return

$('.panel').on 'click', '.js-news-filter', (event) ->
  event_target = $(event.target)
  data_url = event_target.data('url')
  $.ajax data_url,
    method: 'get'
    success: ajax_success
    error: ajax_failed
    complete: ajax_over
    dataType: 'html'
    data:
      publication_filter: event_target.data('publisherPk')
  event.preventDefault()