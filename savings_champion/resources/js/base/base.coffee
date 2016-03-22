ajaxContactCall = -> # catch the form's submit event
  "use strict"
  $contactform = $(".contactform")
  $.ajax # create an AJAX call...
    data: $contactform.serialize() # get the form data
    type: $contactform.attr("method") # GET or POST
    url: $contactform.attr("action") # the file to call
    success: (response) -> # on success..
      ga "send", "event", "Sitewide", "Contact Us Form", "Submitted"  if ga
      $("#contactform").html response # update the DIV
      return

  return
baseGoogleTracking = ->
  "use strict"
  $(".contact-us-button").click ->
    ga "send", "event", "Sitewide", "Contact Us Form", "Clicked"  if ga
    return

  $(".twitter-click").click ->
    ga "send", "event", "Social", "Twitter", "Clicked"  if ga
    return

  $(".facebook-click").click ->
    ga "send", "event", "Social", "Facebook", "Clicked"  if ga
    return

  $(".register-now").click ->
    ga "send", "event", "Social", "Register Now", "Clicked"  if ga
    return

  return
$(document).ready ->
  "use strict"
  baseGoogleTracking()
  $(".contact-us-button").colorbox
    inline: true
    href: "#contactform"

  $(".contactform").validate
    submitHandler: ->

      #this runs when the form validated successfully
      ajaxContactCall() #submit it the form
      return

    errorPlacement: ->
      true

  $(".mobile-switch").click ->
    if $(this).prop("data-mobile") is true
      $(this).text "calling from a mobile?"
      $(".js-title-number").text("0800 321 3581").hide().fadeIn "fast"
      $(this).prop "data-mobile", false
      ga "send", "event", "Sitewide", "Number", "Switched to Landline"  if ga
    else
      $(this).text "calling from a landline?"
      $(".js-title-number").text("0330 330 3581").hide().fadeIn "fast"
      $(this).prop "data-mobile", true
      ga "send", "event", "Sitewide", "Number", "Switched to Mobile"  if ga
    return

  $(".newsletterform").validate errorPlacement: ->
    true

  $(".signup-form").validate errorPlacement: ->
    true

  return

internet_explorer_eleven_windows_eight_button_inside_link_tag_fix = ->
  event_target = $(event.target)
  link = event_target.parent()
  link_address = link.attr('href')
  window.location = link_address
  return

$('body').on 'click', 'a > input[type="button"]', internet_explorer_eleven_windows_eight_button_inside_link_tag_fix

$('body').on 'click', '.js-index-submit', (event) ->
  event_target = $(event.target)
  form = event_target.parent('form')
  form.submit()
  return

if $('#london-office-map').length
  london_map = new GMaps
    div: '#london-office-map'
    lat: '51.517214',
    lng: '-0.112200'

  london_map.addMarker
    lat: '51.517214',
    lng: '-0.112200'
    title: 'London Office'

if $('#bath-office-map').length
  bath_map = new GMaps
    div: '#bath-office-map'
    lat: '51.378366',
    lng: '-2.367639'

  bath_map.addMarker
    lat: '51.378366',
    lng: '-2.367639'
    title: 'Bath Office'


if $('#leeds-office-map').length
  leeds_map = new GMaps
    div: '#leeds-office-map'
    lat: '53.795695',
    lng: ' -1.544702'

  leeds_map.addMarker
    lat: '53.795695',
    lng: ' -1.544702'
    title: 'Leeds Office'

$('.js-callback-form').on('submit', 'form', ->
  event_target = $(event.target)
  event.preventDefault()
  formUrl = event_target.attr('action')
  postData = event_target.serialize()
  $.ajax
    url: formUrl
    type: 'post'
    data: postData
    cache: false
    success: (data, textStatus, jqXHR)->
      $('.js-callback-form').html(data)

    error: (jqXHR, textStatus, errorThrown) ->
      $('.js-callback-form').addClass('js-callback-form-hidden')
      $('.js-callback-form-failure').removeClass('js-callback-form-hidden')
)