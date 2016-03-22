(function() {
  var add_existing_product, add_pool_success, body, csrfSafeMethod, csrftoken, delete_existing_product, delete_existing_product_success, get_existing_products, get_pools, manage_user_success, remove_allowed_product_success, remove_product_success, remove_required_product_success, request_products_list, restore_removed_product_success, retrieve_products, run_concierge_engine, run_concierge_engine_best_case, selectElementContents, submit_required_product, success_get_existing_products, update_concierge_output, update_existing_products, update_existing_products_html, update_pool_success, update_products_dropdown, update_products_list, update_removed_products, update_removed_products_success, update_required_products, update_required_products_success, update_user_options_success;

  body = $('body');

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

  $('form').on('submit', function() {
    event.preventDefault();
  });

  manage_user_success = function(data, textStatus, jqXHR) {
    $('.engine-root').html(data);
  };

  body.on('click', 'input[name="manage-user"]', function(event) {
    var data_source, data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    data_source = event_target.closest('form');
    $.post(data_url, $(data_source).serialize(), manage_user_success, 'html');
  });

  update_user_options_success = function(data, textStatus, jqXHR) {
    $('.user-options').html(data);
  };

  body.on('click', 'input[name="update-user-options"]', function(event) {
    var data_source, data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    data_source = event_target.closest('form');
    $.post(data_url, $(data_source).serialize(), update_user_options_success, 'html');
  });

  add_pool_success = function(data, textStatus, jqXHR) {
    $('.js-user-pools').html(data);
  };

  body.on('click', 'input[name="add-pool"]', function(event) {
    var data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    $.post(data_url, '', add_pool_success, 'html');
  });

  update_pool_success = function(data, textStatus, jqXHR) {
    $('.js-user-pools').html(data);
  };

  body.on('click', 'input[name="save-pool-changes"]', function(event) {
    var data_source, data_url, event_target;
    event_target = $(event.target);
    data_source = event_target.siblings('form');
    data_url = event_target.data('action');
    $.post(data_url, $(data_source).serialize(), update_pool_success, 'html');
    return false;
  });

  update_concierge_output = function(data, textStatus, jqXHR) {
    $('.js-engine-output').html(data);
    get_pools();
    get_existing_products();
  };

  run_concierge_engine = function() {
    var data_url, event_target;
    event_target = $('input.js-concierge-engine-run');
    event_target.removeClass('btn-success');
    event_target.addClass('btn-info');
    event_target.val('Running');
    data_url = $('.js-engine-output').data('url');
    $.post(data_url, '', update_concierge_output, 'html');
  };

  run_concierge_engine_best_case = function() {
    var data_url, event_target;
    event_target = $('input.js-concierge-engine-run-best-case');
    event_target.removeClass('btn-danger');
    event_target.addClass('btn-info');
    event_target.val('Running');
    data_url = $('.js-engine-output').data('urlBestCase');
    $.post(data_url, '', update_concierge_output, 'html');
  };

  body.on('click', 'input.js-concierge-engine-run', run_concierge_engine);

  body.on('click', 'input.js-concierge-engine-run-best-case', run_concierge_engine_best_case);

  remove_product_success = function(data, textStatus, jqXHR) {
    update_required_products();
    run_concierge_engine();
    $('.js-removed-accounts').html(data);
  };

  body.on('click', 'input.js-remove-product', function(event) {
    var concierge_user, data_url, event_target, master_product;
    event_target = $(event.target);
    data_url = event_target.data('url');
    master_product = event_target.data('masterProduct');
    concierge_user = event_target.data('conciergeUser');
    event_target.removeClass('btn-danger');
    event_target.addClass('btn-info');
    event_target.val('Removed');
    $.post(data_url, {
      'master_product': master_product,
      'concierge_user': concierge_user
    }, remove_product_success, 'html');
  });

  restore_removed_product_success = function(data, textStatus, jqXHR) {
    $('.js-removed-accounts').html(data);
  };

  body.on('click', 'input.js-allow-removed-product', function(event) {
    var concierge_user, data_url, event_target, product;
    event_target = $(event.target);
    data_url = event_target.data('url');
    product = event_target.data('removedProduct');
    concierge_user = event_target.data('conciergeUser');
    event_target.removeClass('btn-success');
    event_target.addClass('btn-info');
    event_target.val('Restored');
    $.post(data_url, {
      'removed_product': product,
      'concierge_user': concierge_user
    }, restore_removed_product_success, 'html');
  });

  remove_allowed_product_success = function(data, textStatus, jqXHR) {
    $('.js-allowed-accounts').html(data);
  };

  body.on('click', 'input.js-allow-product', function(event) {
    var concierge_user, data_url, event_target, product, restriction;
    event_target = $(event.target);
    data_url = event_target.data('url');
    product = event_target.data('masterProduct');
    concierge_user = event_target.data('conciergeUser');
    restriction = event_target.data('restriction');
    event_target.removeClass('btn-success');
    event_target.addClass('btn-info');
    event_target.val('Allowed');
    $.post(data_url, {
      'product': product,
      'concierge_user': concierge_user,
      'restriction': restriction
    }, remove_allowed_product_success, 'html');
  });

  body.on('click', 'input.js-remove-allowed-account', function(event) {
    var allowed_product, concierge_user, data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    allowed_product = event_target.data('allowedProduct');
    concierge_user = event_target.data('conciergeUser');
    event_target.removeClass('btn-danger');
    event_target.addClass('btn-info');
    event_target.val('Disallowed');
    $.post(data_url, {
      'allowed_product': allowed_product,
      'concierge_user': concierge_user
    }, remove_allowed_product_success, 'html');
  });

  body.on('click', 'input.js-required-product', function(event) {
    var balance, concierge_user, event_target, master_product, url;
    event_target = $(event.target);
    url = event_target.data('url');
    concierge_user = event_target.data('conciergeUser');
    master_product = event_target.data('masterProduct');
    balance = event_target.data('productBalance');
    event_target.removeClass('btn-success');
    event_target.addClass('btn-info');
    event_target.val('Pinned');
    $.post(url, {
      'concierge_user': concierge_user,
      'master_product': master_product,
      'balance': balance
    }, remove_required_product_success, 'html');
  });

  remove_required_product_success = function(data, textStatus, jqXHR) {
    update_removed_products();
    $('.js-required-accounts').html(data);
  };

  body.on('click', 'input.js-remove-required-account', function(event) {
    var concierge_user, event_target, master_product, url;
    event_target = $(event.target);
    url = event_target.data('url');
    concierge_user = event_target.data('conciergeUser');
    master_product = event_target.data('product');
    $.post(url, {
      'concierge_user': concierge_user,
      'product': master_product
    }, remove_required_product_success, 'html');
  });

  update_required_products_success = function(data, textStatus, jqXHR) {
    $('div.js-require-product-popup-modal').modal('hide');
    body.removeClass('modal-open');
    $('.modal-backdrop.fade.in').removeClass('modal-backdrop');
    $('.js-required-accounts').html(data);
  };

  update_required_products = function() {
    var concierge_user, data_url;
    data_url = $('.js-required-accounts').data('url');
    concierge_user = $('.js-required-accounts').data('conciergeUser');
    $.get(data_url, {
      'concierge_user': concierge_user
    }, update_required_products_success, 'html');
  };

  update_removed_products_success = function(data, textStatus, jqXHR) {
    $('.js-removed-accounts').html(data);
  };

  update_removed_products = function() {
    var concierge_user, data_url;
    data_url = $('.js-removed-accounts').data('url');
    concierge_user = $('.js-removed-accounts').data('conciergeUser');
    $.get(data_url, {
      'concierge_user': concierge_user
    }, update_removed_products_success, 'html');
  };

  body.on('click', '.js-toggle-engine-log', function() {
    $('.js-engine-log').toggle();
  });

  body.on('click', 'button.js-require-product-popup', function() {
    $('div.js-require-product-popup-modal').modal('show');
  });

  update_products_list = function(data, textStatus, jqXHR) {
    var i, len, option_tag, product;
    $('#id_products').empty();
    for (i = 0, len = data.length; i < len; i++) {
      product = data[i];
      option_tag = $('<option>');
      option_tag.val(product[0]);
      option_tag.text(product[1]);
      $('#id_products').append(option_tag);
    }
  };

  request_products_list = function(event) {
    var data_url, event_target, provider_id;
    event_target = $(event.target);
    data_url = event_target.data('url');
    provider_id = event_target.val();
    $.get(data_url, event_target.serialize(), update_products_list, 'json');
  };

  body.on('change', '#id_provider', request_products_list);

  submit_required_product = function(event) {
    var data_url, event_target, modal_form;
    event_target = $(event.target);
    data_url = event_target.data('url');
    modal_form = $('div.js-require-product-popup-modal').find('form');
    Pace.ignore(function() {
      $.post(data_url, modal_form.serialize(), update_required_products_success, 'html');
    });
  };

  body.on('click', 'button.js-require-product-popup-submit', submit_required_product);

  delete_existing_product_success = function(data, textStatus, jqXHR) {
    $('.js-existing-products').html(data);
  };

  delete_existing_product = function(event) {
    var data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    $.post(data_url, '', delete_existing_product_success, 'html');
  };

  body.on('click', '.js-delete-existing-product', delete_existing_product);

  add_existing_product = function(event) {
    $('.js-existing-product-popup-modal').modal('show');
  };

  body.on('click', '.js-add-existing-product-popup', add_existing_product);

  update_products_dropdown = function(data, textStatus, jqXHR) {
    var i, len, option_tag, product;
    $('.js-add-existing-products-form #id_product').empty();
    for (i = 0, len = data.length; i < len; i++) {
      product = data[i];
      option_tag = $('<option>');
      option_tag.val(product[0]);
      option_tag.text(product[1]);
      $('.js-add-existing-products-form #id_product').append(option_tag);
    }
  };

  retrieve_products = function(event) {
    var data_url, event_target;
    event_target = $(event.target);
    data_url = event_target.data('url');
    $.get(data_url, {
      'provider': event_target.val()
    }, update_products_dropdown, 'json');
  };

  body.on('change', '.js-add-existing-products-form #id_provider', retrieve_products);

  update_existing_products_html = function(data, textStatus, jqXHR) {
    $('.js-existing-products').html(data);
  };

  update_existing_products = function(event) {
    var data_concierge_user_id, data_url, event_target, form_data, forms;
    event_target = $(event.target);
    forms = $('.js-add-existing-products-form');
    data_url = forms.attr('action');
    data_concierge_user_id = event_target.data('concierge_user_id');
    form_data = forms.serialize();
    $('.js-existing-product-popup-modal').modal('hide');
    $.post(data_url, form_data, update_existing_products_html, 'html');
  };

  body.on('click', '.js-add-existing-product', update_existing_products);

  get_pools = function() {
    var data_url;
    data_url = $('.js-user-pools').data('url');
    $.get(data_url, '', update_pool_success, 'html');
  };

  success_get_existing_products = function(data, textStatus, jqXHR) {
    $('.js-existing-products').html(data);
  };

  get_existing_products = function() {
    var concierge_user_id, data_url;
    data_url = $('.js-existing-products').data('url');
    concierge_user_id = $('.js-existing-products').data('conciergeUserId');
    $.get(data_url, {
      'concierge_user_id': concierge_user_id
    }, success_get_existing_products, 'html');
  };

  selectElementContents = function(el) {
    var e, error, range, sel;
    body = document.body;
    if (document.createRange && window.getSelection) {
      range = document.createRange();
      sel = window.getSelection();
      sel.removeAllRanges();
      try {
        range.selectNodeContents(el);
        sel.addRange(range);
      } catch (error) {
        e = error;
        range.selectNode(el);
        sel.addRange(range);
      }
    } else if (body.createTextRange) {
      range = body.createTextRange();
      range.moveToElementText(el);
      range.select();
    }
    return false;
  };

  body.on('click', '.js-copy-excluded-products', function() {
    var select_target;
    select_target = document.getElementsByClassName('js-excluded-products-table');
    if (select_target.length > 0) {
      selectElementContents(select_target[0]);
    }
    return false;
  });

}).call(this);

//# sourceMappingURL=engine.js.map
