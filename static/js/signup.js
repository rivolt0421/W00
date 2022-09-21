console.log('hi2');

$(function () {
  let $alert = $('#alertpwconfirm');
  let $pw = $('#password');
  let $pwConfirm = $('#password-confirm');
  let $email = $('#email-address');
  let $userName = $('#name');

  $("[type='submit']").click(function () {
    pw = $pw.val();
    pwConfirm = $pwConfirm.val();

    if ($alert.hasClass('hidden') && pw.length * pwConfirm.length && pw !== pwConfirm) {
      setTimeout(function () {
        $alert.removeClass('hidden').removeClass('hide').addClass('show');
      }, 40);
    }
  });
  $('body').click(function () {
    if ($alert.hasClass('show')) {
      setTimeout(function () {
        $alert.removeClass('show').addClass('hidden');
      }, 40);
    }
  });
  //   $("[type='submit']").focusout(function () {
  //     if ($alert.hasClass('show')) {
  //       $alert.addClass('hide').removeClass('show');
  //       setTimeout(function () {
  //         $alert.addClass('hidden');
  //       }, 40);
  //     }
  //   });
});
