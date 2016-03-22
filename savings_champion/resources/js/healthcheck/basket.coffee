$(document).ready ->
  "use strict"
  $(".give-button").click ->
    $(".name").show()
    $(".sidebar").show()
    $('html, body').animate(
      scrollTop: $(".give-button").offset().top
      200
    )
    if $("#id_advice").is(":checked") or $("#id_concierge").is(":checked")
      $("#div_id_telephone").show()
      $("#id_telephone").addClass "required"
      $("#id_telephone").show()
    else
      $("#div_id_telephone").hide()
      $("#id_telephone").hide()
      $("#id_telephone").removeClass "required"

  $(".checkbox").change ->
    if $("#id_advice").is(":checked") or $("#id_concierge").is(":checked")
      $("#div_id_telephone").show()
      $("#id_telephone").show()
      $("#id_telephone").addClass "required"
      $("#id_telephone").attr "required", true
    else
      $("#div_id_telephone").hide()
      $("#id_telephone").hide()
      $("#id_telephone").removeClass "required"
      $("#id_telephone").removeAttr "required"
