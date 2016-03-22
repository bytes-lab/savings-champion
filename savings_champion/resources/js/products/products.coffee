$.validator.setDefaults
  highlight: (element) ->
    $(element).closest(".form-group").addClass "has-error"
    return

  unhighlight: (element) ->
    $(element).closest(".form-group").removeClass "has-error"
    return

  errorElement: "span"
  errorClass: "help-block"
  errorPlacement: (error, element) ->
    if element.parent(".input-group").length
      error.insertAfter element.parent()
    else
      error.insertAfter element
    return

join_spl_and_continue = (form, event) ->
  event.preventDefault()
  form = $('.js-spl')
  form_url = form.attr 'action'
  form_data = form.serialize()
  $.post form_url, form_data, continue_to_provider, 'html'
  return false

continue_to_provider = ->
  provider_url = $('.js-provider-url').data 'url'
  product = $('.js-provider-url').data 'product'
  ga "send", "event", "Savings Priority List", product + "_Skipped" if ga
  window.location = provider_url;
  return

$('body').on 'click', '.js-to-provider', continue_to_provider

$('.js-spl').submit((e) ->
  e.preventDefault()
  return
).validate({
  submitHandler: join_spl_and_continue,
  rules: {
    name: "required",
    email: {
      required: true,
      email: true
    }
  }
})