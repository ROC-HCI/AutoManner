<?php 
    $id = $_GET['id']; 
?>
<html>
  <head>
    <script type="text/javascript" src="amcharts/amcharts.js"></script>
    <script type="text/javascript" src="amcharts/serial.js"></script>
    <script type="text/javascript" src="amcharts/pie.js"></script>
    <script type="text/javascript" src="amcharts/themes/light.js"></script>
    <script type="text/javascript" src="amcharts/themes/dark.js"></script>

    <script src="amcharts/gantt.js"></script>

    <script src="jquery-1.10.2.js"></script>
    <script src="jquery-ui.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>


    <script src="PapaParse-4.1.0/papaparse.js"></script>

    <link href="flatui/bootstrap/css/bootstrap.css" rel="stylesheet">
    <!--<link href="flatui/css/flat-ui.css" rel="stylesheet">-->
    <link href="demo.css" rel="stylesheet">
    
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r71/three.min.js"></script>
    <!--script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script-->
    <script>
    var folder_dir = "<?php echo $id; ?>";
    $(function() { 
      $( "#slider" ).slider({
        value: "<?php if(strpos($id,'random')) echo '1'; else echo '4'; ?>",
        min: .2,
        max: 8,
        step: .2,
        slide: function( event, ui ) {
          $( "#amount" ).val(ui.value );
          }
        });
        $( "#amount" ).val( $( "#slider" ).slider( "value" ) );
      });
    </script>
  </head>
  <body>
    <nav class="navbar navbar-inverse navbar-static-top" height = 10%>
    <div class="container-fluid">
      <div class="navbar-header">
        <a class="navbar-brand" href="#">AutoManner</a>
      </div>
    </div>
    </nav>
    <div  id="mainContainer" height = 90% >
      <div id ="topContainer" class="row" style="height:50%;background-color:#ffffff;border-radius:15px;padding-top:10px;padding-bottom:10px;">
        <div id="videoContainerOuter" class="col-md-6 col-lg-6">
          <div id="videoContainer" >
      		<video id = "video" >
      		  <source src="Data/<?php echo $id; ?>/<?php echo $_GET['id']; ?>.mp4" id = "video" type="video/mp4">
      		  <source src="Data/14.1/14.1.ogg" type="video/ogg">
      		  Your browser does not support HTML5 video.
      		</video>
          </div>
          <div id = "vidcontrols">
            <div class = "row">
                <div class = "col-md-7 col-md-offset-3 col-lg-7 col-md-offset-3">
                  <div  id = "seekbarcontainer">
                    <div class="col-lg-10" style="padding-left:0px;padding-right:0px;">
                      <div><input type="range" id="seek-bar" value="0" style="background-color:#434343;"></div>
                    </div>
                    <div class="col-lg-2" style="padding-left:0px;padding-right:0px;">
                      <div>
                        <div class="afterinput"id="time-now" value="0" style="background-color:#ffffff;line-height:14px;font-size:13px;">00&#58 00</div>
                      </div>
                    </div>
                    </div>
                </div>
          </div>

          <div class = "row">
               <div class = "col-md-7 col-md-offset-3 col-lg-7 col-md-offset-3">
                      <button type = "button" id="reset" title="fast forward">&#8634;</button>
                      <button type = "button" id="ffwd" title="fast forward">&#9654;</button>
                      <label  style="font-size:85%;width:25%;" class="checkbox-inline">
                        <input type="checkbox" name = "realtime" id="realtime" value="option1"> realtime w/audio
                      </label>
                </div>
                     
            <!--center><button type = "button" id="rewind" title="reverse">&laquo; fast-rewind</button>
            </center-->
          </div>
        </div>
        </div>
        <div class="col-md-6 col-lg-6" id="skeletonContainerOuter">
		  <div id = "display" style="padding:10 10 10 10;position:absolute;"></div>
          <div id = "skeletonContainer"><img src="skeleholder.png" id="skeleholder"/></div>
          <div id = "slidercontainer">
            <div class="col-md-2 col-lg-2"><button onclick = "playskeleton();" type = "button" id="skeleplay">&#10074;&#10074;</button></div>
            <div style="display:none;" class="col-md-4 col-lg-4"><label for="amount"> Prominence:</label>
            <input type="text" id="amount" readonly style="border:0; color:#f6931f; width:20px;font-weight:bold;"></div>
            <div style="display:none;" class="col-md-6 col-lg-6"><div id="slider"></div></div>
          </div>
        </div>

      </div>

      <div class ="row" id = 'in-q'>
          <div class="col-md-8 col-lg-8" id = "selector"><!--div id = "patternselector" class = "btn-group"></div-->
			<div id = "timelineChartdiv"></div>
		  </div>
          <div class="col-md-4 col-lg-4" id = "pieChartdiv"></div>
      </div>
    </div>
    <script src="OrbitControls.js"></script>
    <script src="demo.js"></script>
    <script>
      var myVid = document.getElementById("video");
      if (myVid.duration) {
        console.log("The video duration has already been set");
        drawTimeline();
      } else {
        $("#video").one("durationchange", function() {
        //myVid.ondurationchange=function() {
          console.log("The video duration has changed");
          drawTimeline();
        //};
        });
      }
    </script>
  </body>
</html>