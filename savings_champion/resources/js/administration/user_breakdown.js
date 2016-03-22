(function() {
  var ajax_success;

  ajax_success = function(data, textStatus, jqXHR) {
    $('#content .container-fluid').html(data);
    $('#button-id-filter').val('Filter');
  };

  $('#content').on('click', '#button-id-filter', function(event) {
    var event_target, url;
    event_target = $(event.target);
    event_target.val('Filtering');
    url = event_target.data('url');
    $.ajax(url, {
      method: 'get',
      success: ajax_success,
      data: {
        start_date: $('#id_start_date').val(),
        end_date: $('#id_end_date').val()
      },
      dataType: 'html'
    });
    event.preventDefault();
  });

}).call(this);

//# sourceMappingURL=user_breakdown.js.map
