(function() {
  var add_client_failed, add_client_success, claim_failed, claim_success, contacted_failed, contacted_success, csrfSafeMethod, csrftoken, fact_find_failed, fact_find_success, fake_failed, fake_success, getCookie, illustrated_failed, illustrated_success, no_contact_failed, no_contact_success, random_timeout, recommended_failed, recommended_success, sign_ajax, signed_failed, signed_success, strip_search_tag, unsuitable_failed, unsuitable_success, update_personal, update_recent, update_statistics, update_unclaimed, update_user_options_success;

  if (typeof String.prototype.startsWith !== "function") {
    String.prototype.startsWith = function(str) {
      return this.lastIndexOf(str, 0) === 0;
    };
  }

  getCookie = function(name) {
    var cookie, cookieValue, cookies, i;
    cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      cookies = document.cookie.split(";");
      i = 0;
      while (i < cookies.length) {
        cookie = jQuery.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
        i++;
      }
    }
    return cookieValue;
  };

  csrftoken = getCookie("csrftoken");

  csrfSafeMethod = function(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  };

  $.ajaxSetup({
    crossDomain: false,
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  update_statistics = function() {
    return $.ajax($('#statistics').data('url'), {
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#statistics').html(html);
      }
    });
  };

  update_personal = function() {
    return $.ajax($('#personal_leads').data('url'), {
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#personal_leads').html(html);
      },
      complete: function() {
        $('.icon-refresh-animate').removeClass('icon-refresh-animate');
      }
    });
  };

  update_unclaimed = function(url) {
    if (!url) {
      url = $('#unclaimed_leads').data('url');
    }
    return $.ajax(url, {
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#unclaimed_leads').html(html);
      },
      complete: function() {
        $('.icon-refresh-animate').removeClass('icon-refresh-animate');
      }
    });
  };

  update_recent = function(url) {
    if (!url) {
      url = $('#recent_leads').data('url');
    }
    return $.ajax(url, {
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#recent_leads').html(html);
      },
      complete: function() {
        $('.icon-refresh-animate').removeClass('icon-refresh-animate');
      }
    });
  };

  random_timeout = function(refresh) {
    return Math.round(Math.random() * (refresh - 500)) + 500;
  };

  update_recent();

  update_personal();

  update_statistics();

  update_unclaimed();

  window.setTimeout(function() {
    return update_statistics();
  }, random_timeout(3000));

  window.setTimeout(function() {
    return update_unclaimed();
  }, random_timeout(30000));

  claim_success = function(element) {
    console.log('Claim success');
    $(element).removeClass('btn-success');
    $(element).val('Claimed');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  claim_failed = function(element) {
    console.log('Claim failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Can\'t Claim');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  contacted_success = function(element) {
    console.log('Contacted success');
    $(element).removeClass('btn-success');
    $(element).val('Contacted');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  contacted_failed = function(element) {
    console.log('Contacted failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  fake_success = function(element) {
    console.log('Fake success');
    $(element).removeClass('btn-success');
    $(element).val('Marked Fake');
    $('.js-fake-client').modal('hide');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  fake_failed = function(element) {
    console.log('Fake failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  fact_find_success = function(element) {
    console.log('Fact Find success');
    $(element).removeClass('btn-success');
    $(element).val('Facts Found');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  fact_find_failed = function(element) {
    console.log('Fact Find failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  illustrated_success = function(element) {
    console.log('Illustrated success');
    $(element).removeClass('btn-success');
    $(element).val('Illustrated');
    $('.js-illustrate-client').modal('hide');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  illustrated_failed = function(element) {
    console.log('Illustrated failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  signed_success = function(element) {
    console.log('Signed success');
    $(element).removeClass('btn-success');
    $(element).val('Signed');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  signed_failed = function(element) {
    console.log('Signed failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  unsuitable_success = function(element) {
    console.log('Unsuitable success');
    $(element).removeClass('btn-danger');
    $(element).addClass('btn-info');
    $(element).val('Unsuitable');
    $('.js-unsuitable-client').modal('hide');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  unsuitable_failed = function(element) {
    console.log('Unsuitable failed');
    $(element).removeClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  no_contact_success = function(element) {
    console.log('Not Contacted success');
    $(element).removeClass('btn-success');
    $(element).val('Not Contacted');
    $('.js-no-contact-modal').modal('hide');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  no_contact_failed = function(element) {
    console.log('Not Contacted failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  add_client_success = function(element) {
    console.log('Add Client success');
    $('.js-add-client-alert').addClass('alert alert-success');
    $('.js-add-client-alert').html('Client Added');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  add_client_failed = function(element) {
    console.log('Add Client failed');
    $('.js-add-client-alert').addClass('alert alert-danger');
    $('.js-add-client-alert').html('There was an issue adding this client, maybe they already exist?');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  recommended_success = function(element) {
    console.log('Recommendations success');
    $(element).removeClass('btn-success');
    $(element).val('Recommended');
    $('div.js-recommend-client').modal('hide');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  recommended_failed = function(element) {
    console.log('Recommendations failed');
    $(element).removeClass('btn-success');
    $(element).addClass('btn-danger');
    $(element).val('Error');
    update_statistics();
    update_personal();
    update_unclaimed();
    update_recent();
  };

  $('table').on("click", "input.js-claim-enquiry", function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('claimEnquiry');
    console.log('Claiming Enquiry ' + enquiry_url);
    $.ajax(enquiry_url, {
      method: 'post',
      statusCode: {
        404: function() {
          return claim_failed(event_target);
        },
        204: function() {
          return claim_success(event_target);
        },
        409: function() {
          return claim_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('table').on('click', 'input.js-contacted', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('contacted');
    console.log('Contacted Enquiry ' + enquiry_url);
    $.ajax(enquiry_url, {
      statusCode: {
        404: function() {
          return contacted_failed(event_target);
        },
        204: function() {
          return contacted_success(event_target);
        },
        409: function() {
          return contacted_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('table').on('click', 'input.js-no-contact', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = event_target.data('noContact');
    console.log('Not Contacted Enquiry ' + enquiry_url);
    $.ajax(enquiry_url, {
      statusCode: {
        404: function() {
          return no_contact_failed(event_target);
        },
        204: function() {
          return no_contact_success(event_target);
        },
        409: function() {
          return no_contact_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('table').on('click', 'input.js-no-contact-email', function(event) {
    var event_target, url;
    event_target = $(event.target);
    url = event_target.data('noContact');
    $('.js-no-contact-confirm').data('noContact', url);
    $('.js-no-contact-modal').modal('show');
  });

  $('body').on('click', '.js-no-contact-confirm', function(event) {
    var event_target, url;
    event_target = $(event.target);
    url = event_target.data('noContact');
    $.ajax(url, {
      data: $('.js-no-contact-form').serialize(),
      type: 'POST',
      statusCode: {
        404: function() {
          return no_contact_failed(event_target);
        },
        204: function() {
          return no_contact_success(event_target);
        },
        409: function() {
          return no_contact_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('table').on('click', 'input.js-fake-enquiry', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('fakeEnquiry');
    $('.js-confirm-fake-client').data('fakeEnquiry', enquiry_url);
    $('.js-fake-client').modal('show');
  });

  $('body').on('click', '.js-confirm-fake-client', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('fakeEnquiry');
    console.log('Fake Enquiry ' + enquiry_url);
    $.ajax(enquiry_url, {
      type: 'POST',
      data: $('.js-fake-form').serialize(),
      statusCode: {
        404: function() {
          return fake_failed(event_target);
        },
        204: function() {
          return fake_success(event_target);
        },
        409: function() {
          return fake_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('table').on('click', 'input.js-fact-find', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('factFind');
    console.log('Fact Find ' + enquiry_url);
    $.ajax(enquiry_url, {
      statusCode: {
        404: function() {
          return fact_find_failed(event_target);
        },
        204: function() {
          return fact_find_success(event_target);
        },
        409: function() {
          return fact_find_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('body').on('click', 'button.js-illustration-form', function(event) {
    var enquiry_url, event_target, form;
    event_target = $(event.target);
    enquiry_url = event_target.data('illustration');
    form = $('.js-illustrated-form');
    $.ajax(enquiry_url, {
      data: form.serialize(),
      type: 'POST',
      statusCode: {
        404: function() {
          return illustrated_failed(event_target);
        },
        204: function() {
          return illustrated_success(event_target);
        },
        409: function() {
          return illustrated_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('table').on('click', 'input.js-illustrated', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('illustrated');
    console.log(enquiry_url);
    $('button.js-illustration-form').data('illustration', enquiry_url);
    $('.js-illustrate-client').modal('show');
  });

  $('table').on('click', 'input.js-recommended', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('recommended');
    console.log(enquiry_url);
    $('button.js-recommend-client').data('recommended', enquiry_url);
    $('div.js-recommend-client').modal('show');
  });

  $('body').on('click', 'button.js-recommend-client', function(event) {
    var enquiry_url, event_target, form;
    event_target = $(event.target);
    enquiry_url = $('button.js-recommend-client').data('recommended');
    console.log('Recommended ' + enquiry_url);
    form = $('form.js-recommended-form');
    $.ajax(enquiry_url, {
      data: form.serialize(),
      type: 'POST',
      statusCode: {
        404: function() {
          return recommended_failed(event_target);
        },
        204: function() {
          return recommended_success(event_target);
        },
        409: function() {
          return recommended_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  sign_ajax = function(event_target, enquiry_url, value, fee) {
    $('.modal.signed').modal('hide');
    return $.ajax(enquiry_url, {
      method: 'post',
      statusCode: {
        404: function() {
          return signed_failed(event_target);
        },
        204: function() {
          return signed_success(event_target);
        },
        409: function() {
          return signed_failed(event_target);
        }
      },
      dataType: 'text',
      data: {
        portfolio_value: value,
        fee: fee
      }
    });
  };

  $('.modal').on('click', '.js-signed-form', function(event) {
    var event_target, fee, portfolio_value, url;
    event_target = $(event.target);
    portfolio_value = $('#id_portfolio_value').val();
    fee = $('#id_fee').val();
    $('#id_fee').val('');
    $('#id_portfolio_value').val('');
    url = event_target.data('signed');
    console.log('Signed ' + url);
    return sign_ajax(event_target, url, portfolio_value, fee);
  });

  $('table').on('click', 'input.js-signed', function(event) {
    var event_target, url;
    event_target = $(event.target);
    url = event_target.data('signed');
    $('.js-signed-form').data('signed', url);
    $('.modal.signed').modal();
  });

  $('table').on('click', 'input.js-unsuitable', function(event) {
    var enquiry_url, event_target;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('unsuitable');
    $('.js-confirm-unsuitable-client').data('unsuitable', enquiry_url);
    $('.js-unsuitable-client').modal('show');
  });

  $('body').on('click', '.js-confirm-unsuitable-client', function(event) {
    var enquiry_url, event_target, form;
    event_target = $(event.target);
    enquiry_url = $(event_target).data('unsuitable');
    console.log('Unsuitable ' + enquiry_url);
    form = $('.js-unsuitable-client').find('form');
    $.ajax(enquiry_url, {
      type: 'POST',
      data: form.serialize(),
      statusCode: {
        404: function() {
          return unsuitable_failed(event_target);
        },
        204: function() {
          return unsuitable_success(event_target);
        },
        409: function() {
          return unsuitable_failed(event_target);
        }
      },
      dataType: 'text'
    });
  });

  $('div.panel').on('click', 'span.js-refresh-recent', function(event) {
    $(event.target).addClass('icon-refresh-animate');
    $('.js-recent-search').val('');
    update_statistics();
    update_recent();
  });

  $('div.panel').on('click', 'span.js-refresh-unclaimed', function(event) {
    $(event.target).addClass('icon-refresh-animate');
    update_statistics();
    update_unclaimed();
  });

  $('div.panel').on('click', 'span.js-refresh-personal', function(event) {
    $(event.target).addClass('icon-refresh-animate');
    update_statistics();
    update_personal();
  });

  $('div.panel').on('click', '.js-add-personal', function(event) {
    return $('.modal.add-client').modal();
  });

  $('.modal.add-client').on('click', '.js-add-client-form', function(event) {
    var enquiry_url, event_target, form;
    form = $('div.add-client form');
    event_target = $(event.target);
    enquiry_url = $(event_target).data('addClient');
    return $.ajax(enquiry_url, {
      method: 'post',
      statusCode: {
        404: function() {
          return add_client_failed(event_target);
        },
        204: function() {
          return add_client_success(event_target);
        },
        409: function() {
          return add_client_failed(event_target);
        }
      },
      dataType: 'text',
      data: form.serialize()
    });
  });

  strip_search_tag = function(string, search_tag) {
    return encodeURIComponent(string.slice(search_tag.length, string.length));
  };

  $('.panel').on('change', '.js-recent-search', function(event) {
    var event_target, search_term, search_url;
    event_target = $(event.target);
    search_term = event_target.val();
    if (search_term.startsWith('name:')) {
      search_url = event_target.data('baseUrl') + 'name/' + strip_search_tag(search_term, 'name:') + '/';
    } else if (search_term.startsWith('email:')) {
      search_url = event_target.data('baseUrl') + 'email/' + strip_search_tag(search_term, 'email:') + '/';
    } else if (search_term.startsWith('phone:')) {
      search_url = event_target.data('baseUrl') + 'phone/' + strip_search_tag(search_term, 'phone:') + '/';
    } else {
      return;
    }
    return update_recent(search_url);
  });

  $('.js-recent-search').tooltip({
    title: 'Prefix your search with either "name:", "email:", or "phone:" and press enter to start search. Refresh will remove search.'
  });

  update_user_options_success = function(data, textStatus, jqXHR) {
    $('.user-options').html(data);
  };

  $('body').on('click', 'input[name="update-user-options"]', function(event) {
    var data_source, data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    data_source = event_target.closest('form');
    $.post(data_url, $(data_source).serialize(), update_user_options_success, 'html');
  });

}).call(this);

//# sourceMappingURL=adviser_dashboard.js.map
