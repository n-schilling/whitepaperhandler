window.onload = function(){
  initEventHandling();
}

function initEventHandling() {
  var sendRequestButton;

  sendRequestButton = document.getElementById("sendRequest");
  sendRequestButton.onclick = function () {
      var name, email, dataProtection;
      name = document.getElementById("name").value;
      email = document.getElementById("email").value;
      dataProtection = document.getElementById("dataProtection");
      if (!name){
        document.getElementById("responseDiv").innerHTML = "Please fill out the form completely.";
        return;
      }
      if (!email){
        document.getElementById("responseDiv").innerHTML = "Please fill out the form completely.";
        return;
      }
      if (dataProtection.checked == true){
        document.getElementById("responseDiv").innerHTML = "Your request is processed...";
        callWebService(name,email);
      } else {
        document.getElementById("responseDiv").innerHTML = "Without consent to the data protection, your request can not be processed.";
      }
  }
}

function callWebService(name,email) {
  var url, fileName, xapikey;
  fileName = "<file name to request in S3>";
  url = "<API gateway URL>?name="+name+"&email="+email+"&fileName="+fileName;
  xapikey = "<X-API-Key>";

  $.ajax({
    type: "GET",
    url: url,
    data: "",
    dataType: 'text',
    headers: { "x-api-key": xapikey },
    success: function(data) {
      document.getElementById("responseDiv").innerHTML = data;
        },
    error: function (data) {
      // There are multiple reasons for an error, which are not helpful for the user. So we use a standard error message
      document.getElementById("responseDiv").innerHTML = "Sorry, there was an error while requesting the whitepaper. Please try again later.";
        }
    })
}
