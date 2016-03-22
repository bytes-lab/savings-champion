$(document).ready ->
  $.validator.addMethod "commaNumber", ((value) ->
    balance = value.replace(/,/g, "")
    /^-?(?:\d+|\d{1,3}(?:,\d{3})+)?(?:\.\d+)?$/.test balance
  ), ""
  $(".account-form").validate errorPlacement: (error, element) ->
    true

  return
