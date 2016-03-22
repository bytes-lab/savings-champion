filter_data = ->
  data_object = {}
  if $('#id_start_date').val() != ''
    data_object['start_date'] = $('#id_start_date').val()
  if $('#id_end_date').val() != ''
    data_object['end_date'] = $('#id_end_date').val()
  if $('#id_end_date').val() != ''
    data_object['referrer'] = $('#id_referrer').val()
  data_object

update_statistics = ->
  data_url = $('#statistics').data('url')
  console.log data_url
  data_object = filter_data()
  $.ajax data_url,
    method: 'get'
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#statistics').html(html)
      return
    data: data_object
  return

update_advisor_workload = ->
  data_url = $('#adviser_workload').data('url')
  data_object = filter_data()
  console.log data_url
  $.ajax data_url,
    method: 'get'
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#adviser_workload').html(html)
      return
    complete: ->
      $('.icon-refresh-animate').removeClass('icon-refresh-animate')
      return
    data: data_object
  return

update_source_pipeline = ->
  data_url = $('#source-pipeline').data('url')
  data_object = filter_data()
  console.log data_url
  $.ajax data_url,
    method: 'get'
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#source-pipeline').html(html)
      return
    complete: ->
      $('.icon-refresh-animate').removeClass('icon-refresh-animate')
    data: data_object
  return

update_adviser_timing = ->
  data_url = $('#adviser-timings').data('url')
  data_object = filter_data()
  console.log data_url
  $.ajax data_url,
    method: 'get'
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#adviser-timings').html(html)
      return
    complete: ->
      $('.icon-refresh-animate').removeClass('icon-refresh-animate')
      return
    data: data_object
  return


update_statistics()
update_advisor_workload()
update_source_pipeline()
update_adviser_timing()


button_ajax = (element, button_text, old_class, new_class, log_text) ->
  console.log log_text
  $(element).removeClass old_class
  $(element).addClass new_class
  $(element).val button_text
  update_statistics()
  update_advisor_workload()
  return

$('body').on "click", "span.js-refresh-advisor-workload", (event) ->
  $(event.target).addClass('icon-refresh-animate')
  update_statistics()
  update_advisor_workload()
  return

$('body').on "click", "span.js-refresh-source-pipeline", (event) ->
  $(event.target).addClass('icon-refresh-animate')
  update_statistics()
  update_source_pipeline()
  return

$('body').on "click", "span.js-refresh-adviser-timing", (event) ->
  $(event.target).addClass('icon-refresh-animate')
  update_statistics()
  update_adviser_timing()
  return

$('body').on 'click', '#button-id-filter', (event) ->
  update_statistics()
  update_advisor_workload()
  update_source_pipeline()
  update_adviser_timing()
  return

$('body').on 'click', '.js-unsuitable-reasons', (event) ->
  url = $(event.target).data 'reasonsUrl'
  window.location = url
  return

$('#id_start_date').tooltip
  title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive.'
$('#id_end_date').tooltip
  title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive'