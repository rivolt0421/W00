$(function () {
  let $dropdown = $("[role='menu']");
  $("#user-menu-button").click(function () {
    if ($dropdown.hasClass("hide")) {
      $dropdown.removeClass("hidden").removeClass("hide").addClass("show");
    } else if ($dropdown.hasClass("show")) {
      $dropdown.addClass("hide").removeClass("show");
      setTimeout(function () {
        $dropdown.addClass("hidden");
      }, 40);
    } else if ($dropdown.hasClass("hidden")) {
      $dropdown.removeClass("hidden").addClass("show");
    }
  });
  $("#user-menu-button").focusout(function () {
    if ($dropdown.hasClass("show")) {
      $dropdown.addClass("hide").removeClass("show");
      setTimeout(function () {
        $dropdown.addClass("hidden");
      }, 40);
    }
  });
});
