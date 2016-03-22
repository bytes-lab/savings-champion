$(document).ready ->
  $(".concierge-form").validate errorPlacement: (error, element) ->
    true
  return
