$(function () {
  let $alert = $('#alertpwconfirm');

  $('body').click(function () {
    if ($alert.hasClass('show')) {
      setTimeout(function () {
        $alert.removeClass('show').addClass('hide').addClass('hidden');
      }, 40);
    }
  });
});

function checkForm() {
  let $pw = $('#password');
  let $pwConfirm = $('#password-confirm');
  let $alert = $('#alertpwconfirm');

  pw = $pw.val();
  pwConfirm = $pwConfirm.val();

  if (pw !== pwConfirm) {
    setTimeout(function () {
      $alert.removeClass('hidden').removeClass('hide').addClass('show');
    }, 40);
    console.log('false');
    $pwConfirm.focus();
    return false;
  }

  return true;
}
