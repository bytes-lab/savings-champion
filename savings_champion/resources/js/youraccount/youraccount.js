(function() {
  'use strict';
  var ajaxPasswordCall, ajaxPersonalCall, rebindValidation, reloadPage;

  reloadPage = function() {
    location.reload(true);
  };

  $('body').on('click', '.js-edit-password-done', function() {
    $("div.edit-password").modal('hide');
  });

  ajaxPasswordCall = function() {
    $.ajax({
      data: $(".changepasswordform").serialize(),
      type: $(".changepasswordform").attr("method"),
      url: $(".changepasswordform").attr("action"),
      success: function(response) {
        if (ga) {
          ga("send", "event", "Your Account", "Password Change", "Submitted");
        }
        $(".changepasswordform").html(response);
        rebindValidation();
        $('.js-edit-password').removeClass('btn-success');
        $('.js-edit-password').addClass('btn-info');
        $('.js-edit-password').addClass('js-edit-password-done');
        $('.js-edit-password').val('Close');
        $('.js-edit-password').data('dismiss', 'modal');
        $('.js-edit-password').removeClass('js-edit-password');
      }
    });
  };

  $('body').on('click', '.js-edit-details-done', function() {
    $("div.edit-details").modal('hide');
    location.reload(true);
  });

  ajaxPersonalCall = function() {
    $.ajax({
      data: $(".personaldetailsform").serialize(),
      type: $(".personaldetailsform").attr("method"),
      url: $(".personaldetailsform").attr("action"),
      success: function(response) {
        if (ga) {
          ga("send", "event", "Your Account", "Personal Details Form", "Submitted");
        }
        $(".personaldetailsform").html(response);
        rebindValidation();
        $('.js-edit-details').removeClass('btn-success');
        $('.js-edit-details').addClass('btn-info');
        $('.js-edit-details').addClass('js-edit-details-done');
        $('.js-edit-details').val('Close');
        $('.js-edit-details').data('dismiss', 'modal');
        $('.js-edit-details').removeClass('js-edit-details');
      }
    });
  };

  rebindValidation = function() {
    $(".changepasswordform").validate({
      submitHandler: function() {
        ajaxPasswordCall();
      },
      errorPlacement: function() {
        return true;
      }
    });
    $(".personaldetailsform").validate({
      submitHandler: function() {
        ajaxPersonalCall();
      },
      errorPlacement: function() {
        return true;
      }
    });
  };

  $("div.delete-account").modal({
    show: false
  });

  $("div.edit-details").modal({
    show: false
  });

  $("div.edit-password").modal({
    show: false
  });

  $('body').on('click', 'a.delete-account', function() {
    return $("div.delete-account").modal('show');
  });

  $('body').on('click', 'a.edit-details', function() {
    return $("div.edit-details").modal('show');
  });

  $('body').on('click', 'a.edit-password', function() {
    return $("div.edit-password").modal('show');
  });

  rebindValidation();

  $('body').on('click', '.js-delete-account', function() {
    $('.delete-account-form').submit();
  });

  $('body').on('click', '.js-edit-details', function() {
    $('.personaldetailsform').submit();
  });

  $('body').on('click', '.js-edit-password', function() {
    $('.changepasswordform').submit();
  });

}).call(this);

//# sourceMappingURL=youraccount.js.map
