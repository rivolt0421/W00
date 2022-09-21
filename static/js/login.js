function createCookie(value) {
  var now = new Date();
  var expirationDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 7, 0, 0, 0);

  document.cookie = 'token=' + value + '; expires=' + expirationDate + '; path=/';
}

$(document).ready(function () {
  $('#loginForm').submit(function (e) {
    e.preventDefault();

    const email = $('#email-address').val();
    const password = $('#password').val();

    $.ajax({
      method: 'POST',
      url: 'http://localhost:5000/login',
      data: JSON.stringify({
        email: email,
        password: password,
      }),
      contentType: 'application/json',
    })
      .then(function (msg) {
        if (msg.access_token) {
          const token = msg.access_token;
          createCookie(token);
          location.href = `/projects?token=${token}`;
        }
      })
      .fail(res => {
        if (res.status === 401) {
          alert('이메일 또는 비밀번호가 잘못되었습니다.');
        } else {
          alert('예상치 못한 오류가 발생하였습니다.');
          console.log(res.status);
        }
      });
  });
});
