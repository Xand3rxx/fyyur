$(document).ready(function () {
  "use strict";

  /**
   * @description Prevent characters or string asides number in phone number input field
   */
  $("#phone, #artist_id, #venue_id").on(
    "keypress keyup blur",
    function (event) {
      $(this).val(
        $(this)
          .val()
          .replace(/[^\d].+/, "")
      );
      if (event.which < 48 || event.which > 57) {
        event.preventDefault();
      }
    }
  );
});

const btn = document.getElementById("delete-venue");

btn.onclick = function (e) {
  fetch(`${e.target.dataset["url"]}`, {
    method: "DELETE",
    body: JSON.stringify({ venue_id: e.target.dataset["id"] }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (response) {
      console.log(response);
      // window.location.href = "/";
    })
    .catch(function () {
      alert(`Error occured while trying to delete venue`);
    });
};
