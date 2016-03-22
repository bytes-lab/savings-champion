(function() {
  var ajaxContactCall, baseGoogleTracking, bath_map, internet_explorer_eleven_windows_eight_button_inside_link_tag_fix, leeds_map, london_map;

  ajaxContactCall = function() {
    "use strict";
    var $contactform;
    $contactform = $(".contactform");
    $.ajax({
      data: $contactform.serialize(),
      type: $contactform.attr("method"),
      url: $contactform.attr("action"),
      success: function(response) {
        if (ga) {
          ga("send", "event", "Sitewide", "Contact Us Form", "Submitted");
        }
        $("#contactform").html(response);
      }
    });
  };

  baseGoogleTracking = function() {
    "use strict";
    $(".contact-us-button").click(function() {
      if (ga) {
        ga("send", "event", "Sitewide", "Contact Us Form", "Clicked");
      }
    });
    $(".twitter-click").click(function() {
      if (ga) {
        ga("send", "event", "Social", "Twitter", "Clicked");
      }
    });
    $(".facebook-click").click(function() {
      if (ga) {
        ga("send", "event", "Social", "Facebook", "Clicked");
      }
    });
    $(".register-now").click(function() {
      if (ga) {
        ga("send", "event", "Social", "Register Now", "Clicked");
      }
    });
  };

  $(document).ready(function() {
    "use strict";
    baseGoogleTracking();
    $(".contact-us-button").colorbox({
      inline: true,
      href: "#contactform"
    });
    $(".contactform").validate({
      submitHandler: function() {
        ajaxContactCall();
      },
      errorPlacement: function() {
        return true;
      }
    });
    $(".mobile-switch").click(function() {
      if ($(this).prop("data-mobile") === true) {
        $(this).text("calling from a mobile?");
        $(".js-title-number").text("0800 321 3581").hide().fadeIn("fast");
        $(this).prop("data-mobile", false);
        if (ga) {
          ga("send", "event", "Sitewide", "Number", "Switched to Landline");
        }
      } else {
        $(this).text("calling from a landline?");
        $(".js-title-number").text("0330 330 3581").hide().fadeIn("fast");
        $(this).prop("data-mobile", true);
        if (ga) {
          ga("send", "event", "Sitewide", "Number", "Switched to Mobile");
        }
      }
    });
    $(".newsletterform").validate({
      errorPlacement: function() {
        return true;
      }
    });
    $(".signup-form").validate({
      errorPlacement: function() {
        return true;
      }
    });
  });

  internet_explorer_eleven_windows_eight_button_inside_link_tag_fix = function() {
    var event_target, link, link_address;
    event_target = $(event.target);
    link = event_target.parent();
    link_address = link.attr('href');
    window.location = link_address;
  };

  $('body').on('click', 'a > input[type="button"]', internet_explorer_eleven_windows_eight_button_inside_link_tag_fix);

  $('body').on('click', '.js-index-submit', function(event) {
    var event_target, form;
    event_target = $(event.target);
    form = event_target.parent('form');
    form.submit();
  });

  if ($('#london-office-map').length) {
    london_map = new GMaps({
      div: '#london-office-map',
      lat: '51.517214',
      lng: '-0.112200'
    });
    london_map.addMarker({
      lat: '51.517214',
      lng: '-0.112200',
      title: 'London Office'
    });
  }

  if ($('#bath-office-map').length) {
    bath_map = new GMaps({
      div: '#bath-office-map',
      lat: '51.378366',
      lng: '-2.367639'
    });
    bath_map.addMarker({
      lat: '51.378366',
      lng: '-2.367639',
      title: 'Bath Office'
    });
  }

  if ($('#leeds-office-map').length) {
    leeds_map = new GMaps({
      div: '#leeds-office-map',
      lat: '53.795695',
      lng: ' -1.544702'
    });
    leeds_map.addMarker({
      lat: '53.795695',
      lng: ' -1.544702',
      title: 'Leeds Office'
    });
  }

  $('.js-callback-form').on('submit', 'form', function() {
    var event_target, formUrl, postData;
    event_target = $(event.target);
    event.preventDefault();
    formUrl = event_target.attr('action');
    postData = event_target.serialize();
    return $.ajax({
      url: formUrl,
      type: 'post',
      data: postData,
      cache: false,
      success: function(data, textStatus, jqXHR) {
        return $('.js-callback-form').html(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $('.js-callback-form').addClass('js-callback-form-hidden');
        return $('.js-callback-form-failure').removeClass('js-callback-form-hidden');
      }
    });
  });

}).call(this);

//# sourceMappingURL=base.js.map
