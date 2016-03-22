mark_as_paid_success = ->
  location.reload(true)

date_filter = () ->
  $('form').serialize()

$('body').on 'click', '.js-referrals-mark-as-paid', (event) ->
  event_target = $(event.target)
  url = event_target.data('url')
  event_target.removeClass('btn-success')
  event_target.addClass('btn-info')
  event_target.val('Marking')
  $.ajax
    url: url
    success: mark_as_paid_success
  return

$('#id_start_date').tooltip
  title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive.'
$('#id_end_date').tooltip
  title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive'



