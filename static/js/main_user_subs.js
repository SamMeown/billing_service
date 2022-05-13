// Handle cancel subscription modal
$(document).on('shown.bs.modal', '#modal-cancel', function (event) {
  var element = $(event.relatedTarget);

  var name = element.data("name");
  var pk = element.data("pk");
  $("#modal-cancel-text").text("This will cancel " + name + " " + pk + " ?");

  var url = new URL(element.data("url"));
  $("#modal-stop-button").attr("data-url", url.href);
  url.searchParams.append('chargeback', true);
  $("#modal-chargeback-button").attr("data-url", url.href);
});

["#modal-stop-button", "#modal-chargeback-button"].forEach(btnId => {
    $(document).on('click', btnId, function() {
        // TODO
        console.log($(this).attr('data-url'));
        //  $.ajax({
        //    url: $(this).attr('data-url'),
        //    method: 'DELETE',
        //    success: function(result) {
        //
        ////        window.location.href = result;
        //    }
        //  });
    });
});
