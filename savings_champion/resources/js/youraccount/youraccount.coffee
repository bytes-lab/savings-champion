'use strict'

reloadPage = ->
  location.reload true
  return

$('body').on 'click', '.js-edit-password-done', ->
  $("div.edit-password").modal 'hide'
  return

ajaxPasswordCall = -> # catch the form's submit event
  $.ajax # create an AJAX call...
    data: $(".changepasswordform").serialize() # get the form data
    type: $(".changepasswordform").attr("method") # GET or POST
    url: $(".changepasswordform").attr("action") # the file to call
    success: (response) -> # on success..
      ga "send", "event", "Your Account", "Password Change", "Submitted"  if ga
      $(".changepasswordform").html response # update the DIV
      rebindValidation()
      $('.js-edit-password').removeClass 'btn-success'
      $('.js-edit-password').addClass 'btn-info'
      $('.js-edit-password').addClass 'js-edit-password-done'
      $('.js-edit-password').val 'Close'
      $('.js-edit-password').data 'dismiss', 'modal'
      $('.js-edit-password').removeClass 'js-edit-password'
      return
  return

$('body').on 'click', '.js-edit-details-done', ->
  $("div.edit-details").modal 'hide'
  location.reload(true)
  return

ajaxPersonalCall = -> # catch the form's submit event
  $.ajax # create an AJAX call...
    data: $(".personaldetailsform").serialize() # get the form data
    type: $(".personaldetailsform").attr("method") # GET or POST
    url: $(".personaldetailsform").attr("action") # the file to call
    success: (response) -> # on success..
      ga "send", "event", "Your Account", "Personal Details Form", "Submitted"  if ga
      $(".personaldetailsform").html response # update the DIV
      rebindValidation()
      $('.js-edit-details').removeClass 'btn-success'
      $('.js-edit-details').addClass 'btn-info'
      $('.js-edit-details').addClass 'js-edit-details-done'
      $('.js-edit-details').val 'Close'
      $('.js-edit-details').data 'dismiss', 'modal'
      $('.js-edit-details').removeClass 'js-edit-details'
      return
  return

rebindValidation = ->
  $(".changepasswordform").validate
    submitHandler: ->

      #this runs when the form validated successfully
      ajaxPasswordCall() #submit it the form
      return

    errorPlacement: ->
      true

  $(".personaldetailsform").validate
    submitHandler: ->

      #this runs when the form validated successfully
      ajaxPersonalCall() #submit it the form
      return

    errorPlacement: ->
      true
  return

$("div.delete-account").modal
  show: false

$("div.edit-details").modal
  show: false

$("div.edit-password").modal
  show: false

$('body').on 'click', 'a.delete-account', ->
  $("div.delete-account").modal 'show'

$('body').on 'click', 'a.edit-details', ->
  $("div.edit-details").modal 'show'

$('body').on 'click', 'a.edit-password', ->
  $("div.edit-password").modal 'show'

rebindValidation()

$('body').on 'click', '.js-delete-account', ->
  $('.delete-account-form').submit()
  return

$('body').on 'click', '.js-edit-details', ->
  $('.personaldetailsform').submit()
  return

$('body').on 'click', '.js-edit-password', ->
  $('.changepasswordform').submit()
  return

