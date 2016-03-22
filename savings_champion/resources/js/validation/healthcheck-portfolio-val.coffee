#this runs when the form validated successfully
#submit it the form

#this runs when the form validated successfully
#submit it the form
ajaxAddProductsCall = (form_id, div_id) -> # catch the form's submit event
  $.ajax # create an AJAX call...
    data: $(form_id).serialize() # get the form data
    type: $(form_id).attr("method") # GET or POST
    url: $(form_id).attr("action") # the file to call
    success: (response) -> # on success..
      $(div_id).replaceWith response # update the DIV
      return

  return
$(document).ready ->
  $.validator.setDefaults ignore: ":hidden:not(select)"
  $(".variable-product-form").validate
    submitHandler: (form) ->
      ajaxAddProductsCall ".variable-product-form", ".js-variable-product-form"
      return

  $(".fixed-product-form").validate
    submitHandler: (form) ->
      ajaxAddProductsCall ".fixed-product-form", ".js-variable-product-form"
      return

  return
