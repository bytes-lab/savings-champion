$(document).ready ->
  $(".activate-form").validate errorPlacement: (error, element) ->
    true
  return