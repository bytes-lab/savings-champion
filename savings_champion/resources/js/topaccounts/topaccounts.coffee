printContents = (id) ->
  "use strict"
  window.print()

# Does this cookie string begin with the name we want?

# Only send the token to relative URLs i.e. locally.

#this runs when the form validated successfully
#submit it the form
ajaxEmailReminderCall = -> # catch the form's submit event
  "use strict"
  email_instructions_form = $(".email-instructions-form")
  $.ajax # create an AJAX call...
    data: email_instructions_form.serialize() # get the form data
    type: email_instructions_form.attr("method") # GET or POST
    url: email_instructions_form.attr("action") # the file to call
    success: -> # on success..
      window.location.href = $(".no-reminder").attr("href")
      return

  return
toaster = (event) ->
  "use strict"
  if event is "in"
    $("#bestbuy-modal").modal "show"  if $.cookie("bestbuy-emails-modal") isnt "shown"
  else $("#bestbuy-modal").modal "hide"  if event is "out"
  return
#STOP default action
isElementInViewport = (el) ->
  "use strict"
  rect = undefined
  try
    rect = el.getBoundingClientRect()
  catch e
    return false
  #or $(window).height()
  rect.top >= 0 and rect.left >= 0 and rect.bottom <= (window.innerHeight or document.documentElement.clientHeight) and rect.right <= (window.innerWidth or document.documentElement.clientWidth) #or $(window).width()
elementVisibilityMayChange = (el) ->
  "use strict"
  ->
    if isElementInViewport(el)
      toaster "in"
    else
      toaster "out"
    return
$(document).ready ->
  "use strict"
  apply_link = $(".apply-link")
  apply_link.click ->
    product = undefined
    provider = undefined
    provider = $(this).attr("provider")
    product = $(this).attr("product")
    ga "send", "event", "BestBuys", provider, product  if ga
    return

  apply_link = apply_link.not(".authenticated")
  apply_link.click ->
    product = undefined
    provider = undefined
    $(".no-reminder").attr "href", $(this).attr("href")
    provider = $(this).attr("provider")
    product = $(this).attr("product")
    return

  apply_link.colorbox
    inline: true
    href: "#apply-box"

  $.ajaxSetup beforeSend: (xhr, settings) ->
    getCookie = (name) ->
      cookieValue = null
      if document.cookie and document.cookie isnt ""
        cookies = document.cookie.split(";")
        i = 0

        while i < cookies.length
          cookie = jQuery.trim(cookies[i])
          if cookie.substring(0, name.length + 1) is (name + "=")
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          i++
      cookieValue
    xhr.setRequestHeader "X-CSRFToken", getCookie("csrftoken")  unless /^http:.*/.test(settings.url) or /^https:.*/.test(settings.url)
    return

  $(".email-instructions-form").validate
    submitHandler: ->
      ajaxEmailReminderCall()
      return

    errorPlacement: ->
      true

  $(".whatis").click ->
    $(this).closest(".td-heading").find(".explanation").toggle()
    false

  $(".print-button").click ->
    ga "send", "event", "BestBuys", "Display", "BestBuy Printed"  if ga
    printContents ".product-section"
    return

  return

$(".js-best-buy-signup-toaster-container").hover toaster("in"), toaster("out")
$(".js-weekly-rate-alerts").on 'submit', (e) ->
  "use strict"
  postData = $(this).serialize()
  formURL = $(this).attr "action"
  $.ajax
    url: formURL
    type: 'post'
    data: postData
    cache: false
    dataType: 'text'
    success: ->
      $(".js-highlight-error").hide()
      $(".js-weekly-bestbuy-trigger").html "<div class=\"alert alert-success\"><p>Thank you, you've been added to our best buy emails. <a href=\"/concierge/\">See what else we do?</a></p></div>"
      toaster "out"
      $(window).unbind "resize scroll", handler
      $(".js-best-buy-signup-toaster-container").unbind "mouseenter mouseleave", toaster
      $.cookie "bestbuy-emails-modal", "shown"

    error: (jqXHR, status, err) ->
      $(".js-highlight-error").show()

  e.preventDefault()

el = document.getElementsByClassName("apply")[0]
handler = elementVisibilityMayChange(el)

#jQuery
$(window).load ->
  "use strict"
  $(window).on "resize scroll", handler  if $(".js-weekly-bestbuy-trigger").is(":visible")
  return

$(window).on "hidden.bs.modal", ->
  "use strict"
  $(window).unbind "resize scroll", handler
  $(".js-best-buy-signup-toaster-container").unbind "mouseenter mouseleave", toaster
  return

$(".modal-footer > input.btn-danger").click ->
  "use strict"
  ga "send", "event", "BestBuys", "Modal", "Closed"  if ga
  $.cookie "bestbuy-emails-modal", "shown",
    expires: 1

  return

$(".modal-header > button.close").click ->
  "use strict"
  ga "send", "event", "BestBuys", "Modal", "Closed"  if ga
  $.cookie "bestbuy-emails-modal", "shown",
    expires: 1

  return

$('body').on 'click', '.js-high-interest-current-accounts-5-percent', ->
  ga "send", "event", "BestBuys", "High Interest Banner", "Clicked"  if ga
  return

$('body').on 'click', '.js-show-full-table', (event) ->
  event_target = $(event.target)
  event_target.hide()
  event_target.siblings().show()
  return

$('body').on 'click', '.js-hide-full-table', (event) ->
  event_target = $(event.target)
  event_target.hide()
  event_target.siblings().show()
  return

$('body').on 'show.bs.collapse', (event) ->
  event_target = $(event.target)
  event_target.find('.js-show-full-table').hide()
  event_target.find('.js-hide-full-table').show()
  return

$('body').on 'hide.bs.collapse', (event) ->
  event_target = $(event.target)
  event_target.find('.js-show-full-table').show()
  event_target.find('.js-hide-full-table').hide()
  return