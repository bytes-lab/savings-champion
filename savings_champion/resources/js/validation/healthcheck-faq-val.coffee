$(document).ready ->
  $(".signup-form").validate errorPlacement: (error, element) ->
    true
  return