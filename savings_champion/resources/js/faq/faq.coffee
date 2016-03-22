$(document).ready ->
  "use strict"
  $(".arrow").click ->
    closed = undefined
    closed = $(this).attr("closed")
    if closed is true
      $(this).closest(".question-block").find(".answer").show()
      $(this).attr "closed", false
      $(this).find(".closed-arrow-img").hide()
      $(this).find(".expanded-arrow-img").show()
    else
      $(this).closest(".question-block").find(".answer").hide()
      $(this).attr "closed", true
      $(this).find(".expanded-arrow-img").hide()
      $(this).find(".closed-arrow-img").show()
    false

  $(".concierge-faq-signup").click ->
    ga "send", "event", "Concierge", "FAQ Signup", "Clicked"  if ga
    return

  $(".healthcheck-faq-signup").click ->
    ga "send", "event", "Healthcheck", "FAQ Signup", "Clicked"  if ga
    return

  return