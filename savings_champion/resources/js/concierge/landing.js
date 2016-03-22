(function() {
  var ajax_task_check, csrfSafeMethod, csrftoken, formset, getCookie, task_failed, task_update;

  getCookie = function(name) {
    var cookie, cookieValue, cookies, i;
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

  csrfSafeMethod = function(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  };

  csrftoken = getCookie("csrftoken");

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  if ($(".js-form-part").length > 0) {
    formset = $(".js-form-part").djangoFormset({
      deleteButtonText: '<span class="glyphicon glyphicon-remove"></span> Remove account'
    });
    $('body').on('click', '.add-pool', function(event) {
      formset.addForm();
    });
  }

  $('body').on('click', '.js-tool-index', function(event) {
    var event_target, form;
    event_target = $(event.target);
    form = event_target.siblings('form');
    event_target.removeClass('btn-info');
    event_target.addClass('btn-danger');
    event_target.val('Saving...');
    form.submit();
  });

  $('body').on('click', '.js-stage-one', function(event) {
    var event_target, form;
    event_target = $(event.target);
    form = event_target.siblings('form');
    event_target.removeClass('btn-info');
    event_target.addClass('btn-danger');
    event_target.val('Saving...');
    form.submit();
  });

  $('body').on('shown.bs.tab', 'a[data-toggle="tab"]', function(e) {
    var accountType, current_tab, previous_tab;
    current_tab = $(e.target);
    previous_tab = $(e.relatedTarget);
    accountType = current_tab.data('accountType');
    if (accountType === 'personal' || accountType === 'business' || accountType === 'charity') {
      $('.js-concierge-tool').show();
      $('.js-concierge-tool-unavailable').hide();
    } else {
      $('.js-concierge-tool').hide();
      $('.js-concierge-tool-unavailable').show();
    }
  });

  task_update = function(data, textStatus, jqXHR) {
    if (typeof data === "object") {
      setTimeout(ajax_task_check, 2000);
    } else {
      $('.loading').replaceWith(data);
    }
  };

  task_failed = function(data, textStatus, jqXHR) {};

  ajax_task_check = function() {
    var best_case_task_id, loading_div, url, worst_case_task_id;
    if (($(".loading").length = 0)) {
      return;
    }
    loading_div = $(".loading");
    url = loading_div.data('url');
    worst_case_task_id = loading_div.data('worstCaseTaskId');
    best_case_task_id = loading_div.data('bestCaseTaskId');
    $.ajax(url, {
      'data': {
        'worst_engine_output_task_id': worst_case_task_id,
        'best_engine_output_task_id': best_case_task_id
      },
      'method': 'post',
      'success': task_update,
      'error': task_failed
    });
  };

  if ($(".loading").length > 0) {
    ajax_task_check();
  }

}).call(this);

//# sourceMappingURL=landing.js.map
