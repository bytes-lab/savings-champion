ajax_success = (data, textStatus, jqXHR) ->
  $('#content .container-fluid').html data
  $('#button-id-filter').val 'Filter'
  return

$('#content').on 'click', '#button-id-filter', (event) ->
  event_target = $ event.target
  event_target.val 'Filtering'
  url = event_target.data 'url'
  $.ajax url,
    method: 'get'
    success: ajax_success
    data:
      start_date: $('#id_start_date').val()
      end_date: $('#id_end_date').val()
    dataType: 'html'
  event.preventDefault()
  return