(function() {
  var client_details, client_details_success, client_notes, client_notes_success, csrfSafeMethod, csrftoken, load_concierge_engine, load_concierge_engine_success, save_client_details, save_client_details_success;

  csrftoken = $.cookie('csrftoken');

  csrfSafeMethod = function(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  };

  $.ajaxSetup({
    crossDomain: false,
    cache: false,
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  client_details_success = function(data, textStatus, jqXHR) {
    $('.js-client-details').html(data);
  };

  client_details = function() {
    var client_id, data_source, data_url;
    data_source = $('.js-client-details');
    data_url = data_source.data('url');
    client_id = data_source.data('clientId');
    $.post(data_url, {
      client_id: client_id
    }, client_details_success, 'html');
  };

  client_notes_success = function(data, statusText, jqXHR) {
    $('.js-client-notes').html(data);
  };

  client_notes = function() {
    var data_source, data_url;
    data_source = $('.js-client-notes-form');
    data_url = data_source.attr('action');
    $.post(data_url, data_source.serialize(), client_notes_success, 'html');
  };

  load_concierge_engine_success = function(data, textStatus, jqXHR) {
    $('.engine-root').html(data);
  };

  load_concierge_engine = function(event) {
    var data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    $.get(data_url, '', load_concierge_engine_success, 'html');
  };

  save_client_details_success = function(data) {
    $('#lead-capture').html(data);
  };

  save_client_details = function(event) {
    var data_url, event_target, parent_form;
    event_target = $(event.target);
    event_target.removeClass('btn-success');
    event_target.addClass('btn-info');
    event_target.val('Saving');
    parent_form = $('#lead-capture').find('form');
    data_url = event_target.data('url');
    $.post(data_url, parent_form.serialize(), save_client_details_success, 'html');
  };

  $('body').on('click', 'input[name="update-user-options"]', client_details);

  $('body').on('click', 'input[name="update-user-notes"]', client_notes);

  $('body').on('click', 'input.js-load-concierge-engine', load_concierge_engine);

  $('body').on('click', 'input.js-save-client-details', save_client_details);

}).call(this);

//# sourceMappingURL=client_dashboard.js.map
