(function() {
  var getRandomInt, slp_signup_success;

  $(".index-signup").click(function() {
    if (ga) {
      ga("send", "event", "Signup", "Index", "Clicked");
    }
  });

  slp_signup_success = function(data, textStatus, jqXHR) {
    console.log('success');
  };

  $('body').on('click', '#submit-id-signup-and-proceed', function(event) {
    var event_target, form, form_data, form_url;
    event_target = $(event.target);
    event.preventDefault();
    form = event_target.parents('form');
    form_data = form.serialize();
    form_url = form.attr('action');
    $.post(form_url, form_data, '', 'html');
  });

  setInterval(function() {
    var hidden, visible;
    visible = $(".heading-quote:visible");
    hidden = $(".heading-quote:hidden");
    visible.fadeOut({
      done: function() {
        return hidden.fadeIn();
      }
    });
  }, 5000);

  $('body').on('slide.bs.carousel', '.carousel', function(event) {
    var slider_element, slider_elements, text_element, text_element_class;
    text_element_class = $(event.relatedTarget).data('textElement');
    text_element = $(text_element_class);
    text_element.siblings('.slide-text').hide();
    text_element.show();
    slider_element = $('.carousel-tab[data-slide="' + text_element_class + '"]');
    slider_elements = $('.carousel-tab[data-slide!="' + text_element_class + '"]');
    slider_element.addClass('active');
    return slider_elements.removeClass('active');
  });

  $('body').on('focus', '#id_email', function() {
    return $('.carousel').carousel('pause');
  });

  getRandomInt = function(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
  };

  $('.bxslider-1').bxSlider({
    minSlides: 4,
    maxSlides: 16,
    slideWidth: 170,
    slideMargin: 10,
    ticker: true,
    speed: 60000
  });

}).call(this);

//# sourceMappingURL=index.js.map
