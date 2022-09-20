/**
 * @author Riya Bhargava
 */
 
//  var BASE_URL = "http://127.0.0.1:5000//api/v1/indexer"
 var BASE_URL = "http://127.0.0.1:5000/search"
 var data = [];
 
 function customEngine(data) {
     var restaurantsIFrame = document.getElementById("restaurants").contentWindow.document;
     let frameElement = document.getElementById("restaurants");
     let doc = frameElement.contentDocument;
     doc.body.innerHTML = doc.body.innerHTML + '<style>a {margin: 0px 0px 0px 0px;}</style>';
     
     restaurantsIFrame.open();
     console.log(data)
     var out = "";
     var i;
      for(i = 0; i < data.length; i++) {
          out += '<a href="' + data[i].url + '">' +
          data[i].title + '</a><br>' + "<p>" + data[i].preview + "<br> </p>";
     }
     restaurantsIFrame.write(out);
     
     restaurantsIFrame.close();
 }

 function valueChange(dropdownType) {
     if(dropdownType == 'relevance'){
         var relevance = $('#relevance').find(":selected").val();
         if(relevance){
             $('#clustering').val('');
             $('#query').val('');
         }
     }
     else if(dropdownType == 'query'){
         var query = $('#query').find(":selected").val();
         if(query){
             $('#clustering').val('');
             $('#relevance').val('');
         }
     }
     else if(dropdownType == 'clustering'){
         var clustering = $('#clustering').find(":selected").val();
         if(clustering){
             $('#relevance').val('');
             $('#query').val('');
         }
     }

 }

 function myFunction(resp) {
     // var text = document.getElementById("query").value();
     document.getElementById("expanded_qu").innerHTML= "Expanded query: " + resp;
     console.log("text");
 }


 function queryToGoogleBing() {
     var input = document.getElementById("UserInput").value;
     document.getElementById("google").src = "https://www.google.com/search?igu=1&source=hp&ei=lheWXriYJ4PktQXN-LPgDA&q=" + input;
     document.getElementById("bing").src = "https://www.bing.com/search?q=" + input;
     document.getElementById("restaurants").src = "/restaurant";
 }

 
 function search_query() {
     document.getElementById("expanded_qu").innerHTML = '';
     var input = document.getElementById("UserInput").value;
     document.getElementById("google").src = "https://www.google.com/search?igu=1&source=hp&ei=lheWXriYJ4PktQXN-LPgDA&q=";
     document.getElementById("bing").src = "https://www.bing.com/search?q=";
     // var select_rev = document.getElementById('relevance');
     var relevance = $('#relevance').find(":selected").val();
     // var select_clus = document.getElementById('clustering');
     var clustering = $('#clustering').find(":selected").val();
     // var select_qe = document.getElementById('query');
     var query = $('#query').find(":selected").val();

     console.log(relevance)
     console.log(clustering)
     console.log(query)

     // var page_rank = document.getElementById("page_rank").checked;
     // var hits = document.getElementById("hits").checked;
     // var flat_clustering = document.getElementById("flat_clustering").checked;
     // var agglo1_clustering = document.getElementById("agglo1_clustering").checked;
     // var agglo2_clustering = document.getElementById("agglo2_clustering").checked;
     // var association_qe = document.getElementById("association_qe_label").checked;
     // var metric_qe = document.getElementById("metric_qe_label").checked;
     // var scalar_qe = document.getElementById("scalar_qe_label").checked;
     var type = "default";

     if (relevance) {
         type = relevance;
     }
     else if (clustering) {
         type = clustering;
     }
     else if (query) {
         type = query;
     }



     // console.log("in script")
     $.get(BASE_URL, {"query": input, "type": type})
     
     .done(function(resp) {
         console.log(resp);
         // customEngine(resp);
         // console.log(resp)
         queryToGoogleBing();
         var query = $('#query').find(":selected").val();
         if (query){
             myFunction(resp);
         }
         // myFunction(resp);
     })
     .fail(function(e) {
         
         console.log("error", e)
     })
 }