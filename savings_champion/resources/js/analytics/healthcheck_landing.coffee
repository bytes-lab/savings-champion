$(document).ready ->
  "use strict"
  $(".healthcheck-signup").click ->
    ga "send", "event", "Signup", "Healthcheck", "Clicked"  if ga
    return

  return
