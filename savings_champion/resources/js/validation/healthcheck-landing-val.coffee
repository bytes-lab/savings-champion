$(document).ready ->
  $(".signup-form").validate errorPlacement: (error, element) ->
    true

  $(".additional-signup-form").validate errorPlacement: (error, element) ->
    true

  return
