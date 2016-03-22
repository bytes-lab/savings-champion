unless typeof String::startsWith is "function"
  String::startsWith = (str) ->
    @.lastIndexOf(str, 0) is 0

getCookie = (name) ->
  cookieValue = null
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
csrftoken = getCookie("csrftoken")

csrfSafeMethod = (method) ->

  # these HTTP methods do not require CSRF protection
  /^(GET|HEAD|OPTIONS|TRACE)$/.test method

$.ajaxSetup
  crossDomain: false # obviates need for sameOrigin test
  beforeSend: (xhr, settings) ->
    xhr.setRequestHeader "X-CSRFToken", csrftoken  unless csrfSafeMethod(settings.type)
    return


update_statistics = ->
  $.ajax $('#statistics').data('url'),
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#statistics').html(html)
      return

update_personal = ->
  $.ajax $('#personal_leads').data('url'),
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#personal_leads').html(html)
      return
    complete: ->
      $('.icon-refresh-animate').removeClass('icon-refresh-animate')
      return

update_unclaimed = (url) ->
  if not url
    url = $('#unclaimed_leads').data('url')
  $.ajax url,
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#unclaimed_leads').html(html)
      return
    complete: ->
      $('.icon-refresh-animate').removeClass('icon-refresh-animate')
      return

update_recent = (url) ->
  if not url
    url = $('#recent_leads').data('url')
  $.ajax url,
    dataType: 'html'
    cache: false
    success: (html, status, jqxhr) ->
      $('#recent_leads').html(html)
      return
    complete: ->
      $('.icon-refresh-animate').removeClass('icon-refresh-animate')
      return


random_timeout = (refresh) ->
  Math.round(Math.random() * (refresh - 500)) + 500

update_recent()

update_personal()

update_statistics()

update_unclaimed()

window.setTimeout ->
  update_statistics()
, random_timeout 3000

window.setTimeout ->
  update_unclaimed()
, random_timeout 30000

claim_success = (element) ->
  console.log 'Claim success'
  $(element).removeClass 'btn-success'
  $(element).val 'Claimed'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

claim_failed = (element) ->
  console.log 'Claim failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Can\'t Claim'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

contacted_success = (element) ->
  console.log 'Contacted success'
  $(element).removeClass 'btn-success'
  $(element).val 'Contacted'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

contacted_failed = (element) ->
  console.log 'Contacted failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

fake_success = (element) ->
  console.log 'Fake success'
  $(element).removeClass 'btn-success'
  $(element).val 'Marked Fake'
  $('.js-fake-client').modal 'hide'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

fake_failed = (element) ->
  console.log 'Fake failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

fact_find_success = (element) ->
  console.log 'Fact Find success'
  $(element).removeClass 'btn-success'
  $(element).val 'Facts Found'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

fact_find_failed = (element) ->
  console.log 'Fact Find failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

illustrated_success = (element) ->
  console.log 'Illustrated success'
  $(element).removeClass 'btn-success'
  $(element).val 'Illustrated'
  $('.js-illustrate-client').modal 'hide'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

illustrated_failed = (element) ->
  console.log 'Illustrated failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

signed_success = (element) ->
  console.log 'Signed success'
  $(element).removeClass 'btn-success'
  $(element).val 'Signed'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

signed_failed = (element) ->
  console.log 'Signed failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

unsuitable_success = (element) ->
  console.log 'Unsuitable success'
  $(element).removeClass 'btn-danger'
  $(element).addClass 'btn-info'
  $(element).val 'Unsuitable'
  $('.js-unsuitable-client').modal 'hide'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

unsuitable_failed = (element) ->
  console.log 'Unsuitable failed'
  $(element).removeClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

no_contact_success = (element) ->
  console.log 'Not Contacted success'
  $(element).removeClass 'btn-success'
  $(element).val 'Not Contacted'
  $('.js-no-contact-modal').modal 'hide'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

no_contact_failed = (element) ->
  console.log 'Not Contacted failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

add_client_success = (element) ->
  console.log 'Add Client success'
  $('.js-add-client-alert').addClass 'alert alert-success'
  $('.js-add-client-alert').html 'Client Added'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

add_client_failed = (element) ->
  console.log 'Add Client failed'
  $('.js-add-client-alert').addClass 'alert alert-danger'
  $('.js-add-client-alert').html 'There was an issue adding this client, maybe they already exist?'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

recommended_success = (element) ->
  console.log 'Recommendations success'
  $(element).removeClass 'btn-success'
  $(element).val 'Recommended'
  $('div.js-recommend-client').modal 'hide'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

recommended_failed = (element) ->
  console.log 'Recommendations failed'
  $(element).removeClass 'btn-success'
  $(element).addClass 'btn-danger'
  $(element).val 'Error'
  update_statistics()
  update_personal()
  update_unclaimed()
  update_recent()
  return

$('table').on "click", "input.js-claim-enquiry", (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data('claimEnquiry')
  console.log 'Claiming Enquiry ' + enquiry_url
  $.ajax enquiry_url,
    method: 'post'
    statusCode:
      404: ->
        claim_failed event_target
      204: ->
        claim_success event_target
      409: ->
        claim_failed event_target
    dataType: 'text'
  return

$('table').on 'click', 'input.js-contacted', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data('contacted')
  console.log 'Contacted Enquiry ' + enquiry_url
  $.ajax enquiry_url,
    statusCode:
      404: ->
        contacted_failed event_target
      204: ->
        contacted_success event_target
      409: ->
        contacted_failed event_target
    dataType: 'text'
  return

$('table').on 'click', 'input.js-no-contact', (event) ->
  event_target = $(event.target)
  enquiry_url = event_target.data('noContact')
  console.log 'Not Contacted Enquiry ' + enquiry_url
  $.ajax enquiry_url,
    statusCode:
      404: ->
        no_contact_failed event_target
      204: ->
        no_contact_success event_target
      409: ->
        no_contact_failed event_target
    dataType: 'text'
  return

$('table').on 'click', 'input.js-no-contact-email', (event) ->
  event_target = $(event.target)
  url = event_target.data('noContact')
  $('.js-no-contact-confirm').data 'noContact', url
  $('.js-no-contact-modal').modal 'show'
  return

$('body').on 'click', '.js-no-contact-confirm', (event) ->
  event_target = $(event.target)
  url = event_target.data('noContact')
  $.ajax url,
    data: $('.js-no-contact-form').serialize()
    type: 'POST'
    statusCode:
      404: ->
        no_contact_failed event_target
      204: ->
        no_contact_success event_target
      409: ->
        no_contact_failed event_target
    dataType: 'text'
  return

$('table').on 'click', 'input.js-fake-enquiry', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data 'fakeEnquiry'
  $('.js-confirm-fake-client').data 'fakeEnquiry', enquiry_url
  $('.js-fake-client').modal 'show'
  return


$('body').on 'click', '.js-confirm-fake-client', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data('fakeEnquiry')
  console.log 'Fake Enquiry ' + enquiry_url
  $.ajax enquiry_url,
    type: 'POST'
    data: $('.js-fake-form').serialize()
    statusCode:
      404: ->
        fake_failed event_target
      204: ->
        fake_success event_target
      409: ->
        fake_failed event_target
    dataType: 'text'
  return

$('table').on 'click', 'input.js-fact-find', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data('factFind')
  console.log 'Fact Find ' + enquiry_url
  $.ajax enquiry_url,
    statusCode:
      404: ->
        fact_find_failed event_target
      204: ->
        fact_find_success event_target
      409: ->
        fact_find_failed event_target
    dataType: 'text'
  return

$('body').on 'click', 'button.js-illustration-form', (event) ->
  event_target = $(event.target)
  enquiry_url = event_target.data 'illustration'
  form = $('.js-illustrated-form')
  $.ajax enquiry_url,
    data: form.serialize()
    type: 'POST'
    statusCode:
      404: ->
        illustrated_failed event_target
      204: ->
        illustrated_success event_target
      409: ->
        illustrated_failed event_target
    dataType: 'text'
  return

$('table').on 'click', 'input.js-illustrated', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data 'illustrated'
  console.log enquiry_url
  $('button.js-illustration-form').data 'illustration', enquiry_url
  $('.js-illustrate-client').modal 'show'
  return

$('table').on 'click', 'input.js-recommended', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data 'recommended'
  console.log enquiry_url
  $('button.js-recommend-client').data 'recommended', enquiry_url
  $('div.js-recommend-client').modal 'show'
  return


$('body').on 'click', 'button.js-recommend-client', (event) ->
  event_target = $(event.target)
  enquiry_url = $('button.js-recommend-client').data 'recommended'
  console.log 'Recommended ' + enquiry_url
  form = $('form.js-recommended-form')
  $.ajax enquiry_url,
    data: form.serialize()
    type: 'POST'
    statusCode:
      404: ->
        recommended_failed event_target
      204: ->
        recommended_success event_target
      409: ->
        recommended_failed event_target
    dataType: 'text'
  return

sign_ajax = (event_target, enquiry_url, value, fee) ->
  $('.modal.signed').modal('hide')
  $.ajax enquiry_url,
    method: 'post'
    statusCode:
      404: ->
        signed_failed event_target
      204: ->
        signed_success event_target
      409: ->
        signed_failed event_target
    dataType: 'text'
    data:
      portfolio_value: value
      fee: fee

$('.modal').on 'click', '.js-signed-form', (event)->
  event_target = $(event.target)
  portfolio_value = $('#id_portfolio_value').val()
  fee = $('#id_fee').val()
  $('#id_fee').val('')
  $('#id_portfolio_value').val('')
  url = event_target.data('signed')
  console.log 'Signed ' + url
  sign_ajax event_target, url, portfolio_value, fee

$('table').on 'click', 'input.js-signed', (event) ->
  event_target = $(event.target)
  url = event_target.data('signed')
  $('.js-signed-form').data('signed', url)
  $('.modal.signed').modal()
  return

$('table').on 'click', 'input.js-unsuitable', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data 'unsuitable'
  $('.js-confirm-unsuitable-client').data 'unsuitable', enquiry_url
  $('.js-unsuitable-client').modal 'show'
  return

$('body').on 'click', '.js-confirm-unsuitable-client', (event) ->
  event_target = $(event.target)
  enquiry_url = $(event_target).data 'unsuitable'
  console.log 'Unsuitable ' + enquiry_url
  form = $('.js-unsuitable-client').find 'form'
  $.ajax enquiry_url,
    type: 'POST',
    data: form.serialize()
    statusCode:
      404: ->
        unsuitable_failed event_target
      204: ->
        unsuitable_success event_target
      409: ->
        unsuitable_failed event_target
    dataType: 'text'
  return

$('div.panel').on 'click', 'span.js-refresh-recent', (event) ->
  $(event.target).addClass('icon-refresh-animate')
  $('.js-recent-search').val('')
  update_statistics()
  update_recent()
  return

$('div.panel').on 'click', 'span.js-refresh-unclaimed', (event) ->
  $(event.target).addClass('icon-refresh-animate')
  update_statistics()
  update_unclaimed()
  return

$('div.panel').on 'click', 'span.js-refresh-personal', (event) ->
  $(event.target).addClass('icon-refresh-animate')
  update_statistics()
  update_personal()
  return

$('div.panel').on 'click', '.js-add-personal', (event) ->
  $('.modal.add-client').modal()

$('.modal.add-client').on 'click', '.js-add-client-form', (event) ->
  form = $('div.add-client form')
  event_target = $(event.target)
  enquiry_url = $(event_target).data('addClient')
  $.ajax enquiry_url,
    method: 'post'
    statusCode:
      404: ->
        add_client_failed event_target
      204: ->
        add_client_success event_target
      409: ->
        add_client_failed event_target
    dataType: 'text'
    data: form.serialize()

strip_search_tag = (string, search_tag) ->
  encodeURIComponent string.slice(search_tag.length, string.length)

$('.panel').on 'change', '.js-recent-search', (event) ->
  event_target = $(event.target)
  search_term = event_target.val()
  if search_term.startsWith('name:')
    search_url = event_target.data('baseUrl') + 'name/' + strip_search_tag(search_term, 'name:') + '/'
  else if search_term.startsWith('email:')
    search_url = event_target.data('baseUrl') + 'email/' + strip_search_tag(search_term, 'email:') + '/'
  else if search_term.startsWith('phone:')
    search_url = event_target.data('baseUrl') + 'phone/' + strip_search_tag(search_term, 'phone:') + '/'
  else
    return
  update_recent search_url

$('.js-recent-search').tooltip
  title: 'Prefix your search with either "name:", "email:", or "phone:" and press enter to start search. Refresh will remove search.'

update_user_options_success = (data, textStatus, jqXHR) ->
#  console.log(data);
  $('.user-options').html(data)
  return

$('body').on 'click', 'input[name="update-user-options"]', (event) ->
  event_target = $(event.target)
  data_url = event_target.data 'url'
  data_source = event_target.closest 'form'
  #  console.log data_url
  $.post data_url, $(data_source).serialize(), update_user_options_success, 'html'
  return