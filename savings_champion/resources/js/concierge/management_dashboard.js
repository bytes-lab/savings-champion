(function() {
  var button_ajax, filter_data, update_adviser_timing, update_advisor_workload, update_source_pipeline, update_statistics;

  filter_data = function() {
    var data_object;
    data_object = {};
    if ($('#id_start_date').val() !== '') {
      data_object['start_date'] = $('#id_start_date').val();
    }
    if ($('#id_end_date').val() !== '') {
      data_object['end_date'] = $('#id_end_date').val();
    }
    if ($('#id_end_date').val() !== '') {
      data_object['referrer'] = $('#id_referrer').val();
    }
    return data_object;
  };

  update_statistics = function() {
    var data_object, data_url;
    data_url = $('#statistics').data('url');
    console.log(data_url);
    data_object = filter_data();
    $.ajax(data_url, {
      method: 'get',
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#statistics').html(html);
      },
      data: data_object
    });
  };

  update_advisor_workload = function() {
    var data_object, data_url;
    data_url = $('#adviser_workload').data('url');
    data_object = filter_data();
    console.log(data_url);
    $.ajax(data_url, {
      method: 'get',
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#adviser_workload').html(html);
      },
      complete: function() {
        $('.icon-refresh-animate').removeClass('icon-refresh-animate');
      },
      data: data_object
    });
  };

  update_source_pipeline = function() {
    var data_object, data_url;
    data_url = $('#source-pipeline').data('url');
    data_object = filter_data();
    console.log(data_url);
    $.ajax(data_url, {
      method: 'get',
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#source-pipeline').html(html);
      },
      complete: function() {
        return $('.icon-refresh-animate').removeClass('icon-refresh-animate');
      },
      data: data_object
    });
  };

  update_adviser_timing = function() {
    var data_object, data_url;
    data_url = $('#adviser-timings').data('url');
    data_object = filter_data();
    console.log(data_url);
    $.ajax(data_url, {
      method: 'get',
      dataType: 'html',
      cache: false,
      success: function(html, status, jqxhr) {
        $('#adviser-timings').html(html);
      },
      complete: function() {
        $('.icon-refresh-animate').removeClass('icon-refresh-animate');
      },
      data: data_object
    });
  };

  update_statistics();

  update_advisor_workload();

  update_source_pipeline();

  update_adviser_timing();

  button_ajax = function(element, button_text, old_class, new_class, log_text) {
    console.log(log_text);
    $(element).removeClass(old_class);
    $(element).addClass(new_class);
    $(element).val(button_text);
    update_statistics();
    update_advisor_workload();
  };

  $('body').on("click", "span.js-refresh-advisor-workload", function(event) {
    $(event.target).addClass('icon-refresh-animate');
    update_statistics();
    update_advisor_workload();
  });

  $('body').on("click", "span.js-refresh-source-pipeline", function(event) {
    $(event.target).addClass('icon-refresh-animate');
    update_statistics();
    update_source_pipeline();
  });

  $('body').on("click", "span.js-refresh-adviser-timing", function(event) {
    $(event.target).addClass('icon-refresh-animate');
    update_statistics();
    update_adviser_timing();
  });

  $('body').on('click', '#button-id-filter', function(event) {
    update_statistics();
    update_advisor_workload();
    update_source_pipeline();
    update_adviser_timing();
  });

  $('body').on('click', '.js-unsuitable-reasons', function(event) {
    var url;
    url = $(event.target).data('reasonsUrl');
    window.location = url;
  });

  $('#id_start_date').tooltip({
    title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive.'
  });

  $('#id_end_date').tooltip({
    title: 'Date should be of the form: YYYY-MM-DD. Date is inclusive'
  });

}).call(this);

//# sourceMappingURL=management_dashboard.js.map
