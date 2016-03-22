(function() {
  var date_filter, mark_as_paid_success;

  mark_as_paid_success = function() {
    return location.reload(true);
  };

  date_filter = function() {
    return $('form').serialize();
  };

  $('body').on('click', '.js-referrals-mark-as-paid', function(event) {
    var event_target, url;
    event_target = $(event.target);
    url = event_target.data('url');
    event_target.removeClass('btn-success');
    event_target.addClass('btn-info');
    event_target.val('Marking');
    $.ajax({
      url: url,
      success: mark_as_paid_success
    });
  });

  $('#id_start_date').tooltip({
    title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive.'
  });

  $('#id_end_date').tooltip({
    title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive'
  });

}).call(this);

//# sourceMappingURL=user_referrals.js.map
