$(document).ready(function () {
  "use strict";

  /**
   * @description Prevent characters or string asides number in phone number input field
   */
  $("#phone, #artist_id, #venue_id").on("keypress keyup blur", function (event) {
    $(this).val(
      $(this)
        .val()
        .replace(/[^\d].+/, "")
    );
    if (event.which < 48 || event.which > 57) {
      event.preventDefault();
    }
  });
});
