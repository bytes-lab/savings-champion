#this runs when the form validated successfully
#submit it the form
ajaxCommentCall = -> # catch the form's submit event
  "use strict"
  $.ajax # create an AJAX call...
    data: $(".comment-form").serialize() # get the form data
    type: $(".comment-form").attr("method") # GET or POST
    url: $(".comment-form").attr("action") # the file to call
    success: () -> # on success..
      ga "send", "event", "News", "Comment Form", "Submitted"  if ga
      reloadPage()
      return

  return
reloadPage = ->
  "use strict"
  location.reload true
  return
$(document).ready ->
  "use strict"
  $(".comment-form").validate
    submitHandler: () ->
      ajaxCommentCall()
      return

    errorPlacement: () ->
      true

  $(".news-concierge-form").validate errorPlacement: () ->
    true

  return

hitCallbackHandler = (url, win) ->
  if win and win.length > 0
    window.open(url, win)
  else
    window.location.href = url


$('table[class*="table"] a').click ->
  url = @getAttribute 'href'
  win = (if (typeof (@getAttribute("target") is "string")) then @getAttribute("target") else "")
  if url == 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-p/'
    ga 'send', 'event', 'Product Outbound', 'Nationwide - FlexDirect Current Account', 'paid.outbrain.com (article)', {'hitCallback': hitCallbackHandler(url,
      win)}
    @preventDefault();
  if url == 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-x/'
    ga 'send', 'event', 'Product Outbound', 'Clydesdale Bank - Current Account Direct', 'paid.outbrain.com (article)', {'hitCallback': hitCallbackHandler(url,
      win)}
    @preventDefault();
  if url == 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-m/'
    ga 'send', 'event', 'Product Outbound', 'Santander - 123 Current Account', 'paid.outbrain.com (article)', {'hitCallback': hitCallbackHandler(url,
      win)}
    @preventDefault();
  if url == 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-yd/'
    ga 'send', 'event', 'Product Outbound', 'TSB Bank - Enhance Current Account', 'paid.outbrain.com (article)', {'hitCallback': hitCallbackHandler(url,
      win)}
  if url == 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-yh/'
    ga 'send', 'event', 'Product Outbound', 'Bank of Scotland - Vantage Current Account', 'paid.outbrain.com (article)', {'hitCallback': hitCallbackHandler(url,
      win)}
  if url == 'http://savingschampion.createsend4.com/t/j-l-iyiubt-hduilday-yk/'
    ga 'send', 'event', 'Product Outbound', 'Lloyds - Vantage Current Account', 'paid.outbrain.com (article)', {'hitCallback': hitCallbackHandler(url,
      win)}
  return


$('body').on 'click', '.js-iht-guide', ->
  window.location.href = 'https://savingschampion.co.uk/ob-iht-guide/'
  return

$('body').on 'click', '.js-ob1-iht-guide', ->
  window.location.href = 'https://savingschampion.co.uk/ob1-iht-guide/'
  return