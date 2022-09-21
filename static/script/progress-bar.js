$(function () {
  let $myskillbar = $(".skillbar-my");
  $myskillbar.find(".skillbar-bar").animate(
    {
      width: $myskillbar.attr("data-percent"),
    },
    2000
  );

  let $chevron = $(".chevron");
  let $friends = $(".friends-progress");
  $($chevron).click(function () {
    if ($chevron.hasClass("chevron-down")) {
      $chevron.removeClass("chevron-down").addClass("chevron-up");
      $friends.animate(
        {
          height: 50 * $friends.find(".skillbar").length + "px",
        },
        200,
        "swing"
      );
    } else if ($chevron.hasClass("chevron-up")) {
      $chevron.removeClass("chevron-up").addClass("chevron-down");
      $friends.animate(
        {
          height: 0,
        },
        500,
        "swing"
      );
    } else if ($chevron.hasClass("first")) {
      $chevron.removeClass("first").addClass("chevron-up");
      $friends.animate(
        {
          height: 50 * $friends.find(".skillbar").length + "px",
        },
        500,
        "swing"
      );
      $(".skillbar").each(function () {
        $(this)
          .find(".skillbar-bar")
          .animate(
            {
              width: $(this).attr("data-percent"),
            },
            2000
          );
      });
    }
  });
});
