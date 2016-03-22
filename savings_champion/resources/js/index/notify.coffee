$(document).ready ->
  "use strict"
  if $.cookie("cookie_notification") isnt "1"
    $.cookie "cookie_notification", "1",
      expires: 3

  return