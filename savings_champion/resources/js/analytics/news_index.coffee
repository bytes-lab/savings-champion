$(document).ready ->
  "use strict"
  $(".arrow").click ->
    ga "send", "event", "News", "Pagination", "Changed"  if ga
    return

  $(".rss").click ->
    ga "send", "event", "News", "RSS", "Clicked"  if ga
    return

  $(".signup-form").submit ->
    ga "send", "News", "Sidebar", "Signup"  if ga
    true

  return
