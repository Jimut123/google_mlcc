$(document).ready(function() {
  // Algorithm to follow when "go" clicked
  $("#go").click(function() {
    // First, compile a list of which features are requested
    selected_feats = []
    $('.requestbox:checked').each(function(){
      selected_feats.push(this.id);
    })
    // Then construct and send a POST request
    $.ajax({
      type:		"POST",
      url:		"https://intro-to-ml-apis-testing.appspot.com/request",
      // Include the URI typed in the box as well as the features
      data:		{
        uri: $("#img_uri").val(),
        features: selected_feats
      },
      // If successful, display the response
      success:	function(data) {
        results = JSON.parse(data).results
        $("#result").html('<div class="grid eee">')
        var i;
        for (i = 0; i < results.length; ++i) {
          var pre = '<div class="column third"><div class="module lighter">';
          var post = '</div></div>'
          $("#result").append(pre + results[i] + post)
          if (i % 3 == 2) {
            $("#result").append('</div><div class="grid fff">')
          }
        }
        $("#result").append('</div>')
      },
      // If unsuccessful, display the error message
      error:		function(jqXHR, textStatus, errorThrown) {
        $("#result").html("Error, status = " + textStatus + ", " +
        "error thrown: " + errorThrown + "<br><br>" + jqXHR.responseText
        );
      },
    });
    // Show that result is being worked on while waiting for a response
    $("#result").html("Working...");
    // Show image the requested image on the page
    $("#img").html('<div class="module darker"><img src="' + $("#img_uri").val() + '" alt="Requested image" style="height: 100%; width: 100%; object-fit: contain;"></div>');
  });

  // If the enter key is pressed, act as if "Go" was clicked
  $("input").keypress(function(e) {
    if (e.keyCode==13) {
      $("#go").click();
    }
  });
});