$(".index-signup").click ->
    ga "send", "event", "Signup", "Index", "Clicked"  if ga
    return

slp_signup_success = (data, textStatus, jqXHR) ->
  console.log 'success'
  return

$('body').on 'click', '#submit-id-signup-and-proceed', (event) ->
  event_target = $(event.target);
  event.preventDefault()
  form = event_target.parents 'form'
  form_data = form.serialize()
  form_url = form.attr 'action'
  $.post form_url, form_data, '', 'html'
  return

setInterval ->
  visible = $(".heading-quote:visible")
  hidden = $(".heading-quote:hidden")
  visible.fadeOut(
    done: ->
      hidden.fadeIn()
  )
  return
, 5000

$('body').on 'slide.bs.carousel', '.carousel', (event) ->
  text_element_class = $(event.relatedTarget).data('textElement')
  text_element = $(text_element_class)
  text_element.siblings('.slide-text').hide()
  text_element.show()
  slider_element = $('.carousel-tab[data-slide="' + text_element_class + '"]');
  slider_elements = $('.carousel-tab[data-slide!="' + text_element_class + '"]');
  slider_element.addClass('active');
  slider_elements.removeClass('active');

$('body').on 'focus', '#id_email', ->
  $('.carousel').carousel('pause')

getRandomInt = (min, max) ->
  Math.floor(Math.random() * (max - min)) + min

$('.bxslider-1').bxSlider({
  minSlides: 4,
  maxSlides: 16,
  slideWidth: 170,
  slideMargin: 10,
  ticker: true,
  speed: 60000
});
