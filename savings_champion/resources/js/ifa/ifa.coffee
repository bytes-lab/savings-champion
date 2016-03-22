$(document).ready ->
  "use strict"
  $(".asset-value").change ->
    selected_value = $(".asset-value").children("option:selected")
    $("#id_signup_amount").val selected_value.text()
    window.location.href = selected_value.val()
    return

  $(".expand-offering").click ->
    $(".extra-text").show()
    $(".image").hide()
    false

  jQuery.validator.addMethod "phoneUK", ((phone_number, element) ->
    @optional(element) or phone_number.length > 9 and phone_number.match(/^(\(?(0|\+44)[1-9]{1}\d{1,4}?\)?\s?\d{3,4}\s?\d{3,4})$/)
  ), "Please specify a valid phone number"

  # validate the concierge form
  $(".ifa-val").validate
    rules:
      email:
        required: true
        email: true
      telephone:
        required: true
        phoneUK: true
      name:
        required: true
    messages:
      email: "Please enter a valid email address"
      telephone: "Please enter a valid telephone number"
      digits: "Please only use numbers"
      name: "Please enter your name"
  return

derp = ->
  return true