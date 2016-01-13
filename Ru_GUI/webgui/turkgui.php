<?php 
    $id = base64_decode($_GET['id']);
	
    /*if($id%2 == 0)
    { 
      if($id*10%2 == 0)
        $id = $id."_random";
    }else{
      if($id*10%2 == 1)
        $id = $id."_random";
    }*/
	$subid = str_replace("_random", "", $id);

	$datakey = MD5(date('Y-m-d_H:i:s')."_".rand());

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
    <link href="gui.css" rel="stylesheet">
    
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r71/three.min.js"></script>
	

    <!--script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script-->
    <script>
	var id = <?php echo $subid; ?>;
	var submitted = false;
    var isFirstVid = "<?php if($id*10%10 == 1) echo 'true'; else echo 'false'; ?>";
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
	  
	  var autoSelect = function(event) {
		  var event = event || window.event, 
			  elem = event.target || event.srcElement, 
			  tag = (elem.tagName || "").toLowerCase(), 
			  sel, range;
		  
		  if (tag === "textarea" || tag === "input") {
			try {
			  elem.select();
			} catch(e) {
			  // May be disabled or not selectable
			}
		  } else if (window.getSelection) { // Not IE
			sel = window.getSelection();
			range = document.createRange();
			range.selectNodeContents(elem);
			sel.removeAllRanges();
			sel.addRange(range);
		  } else if (document.selection) { // IE
			document.selection.empty();
			range = document.body.createTextRange();
			range.moveToElementText(elem);
			range.select();
		  }
	   };
	   
	   var datakey = "<?php echo $datakey; ?>";
    </script>
  </head>
  <body>
	<iframe name="hidden_iframe" id="hidden_iframe" style="display:none;" onload="if(submitted){post_survey();}"></iframe>
    <form action="https://docs.google.com/a/u.rochester.edu/forms/d/1qQlTo4dVfkxF4draYCn4zvTHc2So5YvwIY6R6xcA-74/formResponse" method="POST" target="hidden_iframe" onsubmit="submitted=true;" novalidate>             
    <nav class="navbar navbar-inverse navbar-static-top" height = 10%>
    <div class="container-fluid">
      <div class="navbar-header" style="width:100%;">
        <a class="navbar-brand" href="#">AutoManner</a>		
        <a class="navbar-brand" style="color:red;float:right;" href="http://goo.gl/forms/WRXzw3RXTj">Bug Report</a>
      </div>
    </div>
    </nav>
    <div  id="mainContainer" height = 90% >
      <div id ="topContainer" class="row col-md-offset-3 col-lg-offset-3 col-md-6 col-lg-6" style="height:50%;background-color:#ffffff;border-radius:15px;padding-top:10px;padding-bottom:10px;">
        <div id="videoContainerOuter">
          <div id="videoContainer" >
      		<video id = "video" >
      		  <source src="Data/<?php echo $id; ?>/<?php echo $subid; ?>.mp4" id = "video" type="video/mp4">
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
					  <button type = "button" id="play" title="normal speed">&#9654;</button>
                      <button type = "button" id="ffwd" title="fast forward">&#9654;&#9654;</button>

                      <label id ="realcheck" style="font-size:85%;width:25%;display:none" class="checkbox-inline">
                        <input type="checkbox" name = "realtime" id="realtime" value="option1"> realtime w/audio
                      </label>
                </div>
                     
            <!--center><button type = "button" id="rewind" title="reverse">&laquo; fast-rewind</button>
            </center-->
          </div>
        </div>
        </div>
		
		<div id = "instructionset">
			<fieldset>
			<center><p>Welcome to the RocSpeak Body Language Study! </p></center>
			<p>Please follow the instructions that will appear during each stages of the study.</p>
			<li>Please use <font color=cyan>Google Chrome</font>, other browsers may experience issues.</li>
			<li>Play the video at least once. A survey will appear after you complete this step.</li>
			<li>Please <font color=cyan>DO NOT</font> skip to the end, that will keep the survey hidden and you'll need to watch the video again.</li>
			<li>The HIT will take approximately <font color=cyan>10-15</font> minutes to complete.</li>
			<div id="mturk_info"></div>
			</fieldset>
		</div>
        <div class="col-md-6 col-lg-6" id="skeletonContainerOuter" style="display:none"> 
		  <div id = "display" style="padding:10 10 10 10;position:absolute;"></div>
          <div id = "skeletonContainer"><img src="skeleholder.png" id="skeleholder"/></div>
          <div id = "slidercontainer">
            <div class="col-md-2 col-lg-2"><button onclick = "playskeleton();" type = "button" id="skeleplay">&#10074;&#10074;</button></div>
            <div style="display:none" class="col-md-4 col-lg-4"><label for="amount"> Prominence:</label>
            <input type="text" id="amount" readonly style="border:0; color:#f6931f;width:20px;font-weight:bold;"></div>
            <div style="display:none" class="col-md-6 col-lg-6"><div id="slider"></div></div>
          </div>
        </div>

      </div>

      <div class = "row" id = "pre-q">
          <fieldset>
            <center><div id = "movewarning"></div></center>
              <input type="hidden" name="entry.1933898981" class="ss-q-short" id="entry_1933898981" dir="auto" aria-label="id  " aria-="true" title="" value="<?php echo $id; ?>">
             <div class = "row row-margin">
             <div class = "question">Overall rating for this speech is :</div>
              <div class="col-md-3 col-lg-3 centering">[Terrible]</div>
			  <div class="col-md-6 col-lg-6 centering">
              <div class=" btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_298715203_1" name="entry.298715203" value="1" /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_298715203_2" name="entry.298715203" value="2"/> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_298715203_3" name="entry.298715203" value="3"/> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_298715203_4" name="entry.298715203" value="4"/> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_298715203_5" name="entry.298715203" value="5"/> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_298715203_6" name="entry.298715203" value="6"/> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_298715203_7" name="entry.298715203" value="7"/> 7
                </label> 
            </div>
			</div>
            <div class="col-md-3 col-lg-3 centering">[Excellent]</div>
			</div>

            <div class = "row row-margin">
            <div class = "question">I would like to listen to another speech from this speaker.</div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			  <div class="col-md-6 col-lg-6 centering">
              <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="1" id="group_402079925_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="2" id="group_402079925_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="3" id="group_402079925_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="4" id="group_402079925_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="5" id="group_402079925_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="6" id="group_402079925_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.402079925" value="7" id="group_402079925_7"/> 7
                  </label> 
              </div>
			  </div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
          </div>
          <div class = "row row-margin">
            <div class = "question">The speaker displayed effective body language.</div>
             <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			 <div class="col-md-6 col-lg-6 centering">
             <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="1" id="group_1350142475_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="2" id="group_1350142475_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="3" id="group_1350142475_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="4" id="group_1350142475_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="5" id="group_1350142475_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="6" id="group_1350142475_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1350142475" value="7" id="group_1350142475_7"/> 7
                  </label> 
              </div>
			  </div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
            </div>
          <div class = "row row-margin">
            <div class = "question">The speaker's body language was appropriate with the speech.</div>
             <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			 <div class="col-md-6 col-lg-6 centering">
             <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="1" id="group_444518839_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="2" id="group_444518839_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="3" id="group_444518839_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="4" id="group_444518839_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="5" id="group_444518839_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="6" id="group_444518839_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.444518839" value="7" id="group_444518839_7" /> 7
                  </label> 
              </div>
			  </div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
            </div>

			
		<div class = "row row-margin">
             <div class = "question">The speaker's body language was synchronized with the story.</div>
             <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			 <div class="col-md-6 col-lg-6 centering">
             <div class="btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_1" name="entry.1973339660" value="1"/> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_2" name="entry.1973339660" value="2"/> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_3" name="entry.1973339660" value="3"/> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_4" name="entry.1973339660" value="4"/> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_5" name="entry.1973339660" value="5"/> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_6" name="entry.1973339660" value="6"/> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_7" name="entry.1973339660" value="7"/> 7
                </label> 
            </div>
			</div>
            <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
            </div>

            <div class = "row row-margin">
            <div class = "question">The speaker was moving about the space around him/her.</div>
                <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
				<div class="col-md-6 col-lg-6 centering">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="1" id="group_2021115824_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="2" id="group_2021115824_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="3" id="group_2021115824_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="4" id="group_2021115824_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="5" id="group_2021115824_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="6" id="group_2021115824_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="7" id="group_2021115824_7"/> 7
                  </label> 
              </div>
			  </div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
          </div>
          <div class = "row row-margin">
            <div class = "question">The speaker was using a variety of gestures.</div>
             <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			 <div class="col-md-6 col-lg-6 centering">
             <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="1" id="group_543518954_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="2" id="group_543518954_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="3" id="group_543518954_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="4" id="group_543518954_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="5" id="group_543518954_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="6" id="group_543518954_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="7" id="group_543518954_7"/> 7
                  </label>
              </div>
			  </div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div> 
            </div>
			
		   <div class = "row row-margin">
			  <div class = "question">The speaker look spontaneous with his/her gestures.</div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			 <div class="col-md-6 col-lg-6 centering">
             <div class="btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_1" name="entry.122496811" value="1"  /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_2" name="entry.122496811" value="2" /> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_3" name="entry.122496811" value="3" /> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_4" name="entry.122496811" value="4" /> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_5" name="entry.122496811" value="5" /> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_122496811_6" name="entry.122496811" value="6" /> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_7" name="entry.122496811"  value="7" /> 7
                </label> 
            </div>
			</div>
            <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
           	</div>

           	<div class = "row row-margin">
            <div class = "question">The speaker was able to add further meaning to their story through his/her gestures.</div>
             <div class="col-md-3 col-lg-3 centering">[Strongly Disagree]</div>
			 <div class="col-md-6 col-lg-6 centering">
             <div class="btn-group" data-toggle="buttons">
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="1" id="group_951552620_1" /> 1
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="2" id="group_951552620_2" /> 2
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="3" id="group_951552620_3" /> 3
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="4" id="group_951552620_4" /> 4
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="5" id="group_951552620_5" /> 5
	                </label>
	                  <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="6" id="group_951552620_6" /> 6
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="7" id="group_951552620_7" /> 7
	                </label> 
	            </div>
			  </div>
              <div class="col-md-3 col-lg-3 centering">[Strongly Agree]</div>
	        </div>
          <div class = "row row-margin">
            <center><button class="btn btn-default disabled" type="<?php if($_GET['id']*10%10 == 3) echo "submit"; else echo "button"; ?>" id= "complete-1" onclick="complete_presurvey();">Complete</button></center>
          </div>
          </fieldset>

      </div>

      <div class ="row" id = 'in-q' style="display:none">
          <div class="col-md-8 col-lg-8" id = "selector"><!--div id = "patternselector" class = "btn-group"></div-->
          <div id = "timelineChartdiv"></div>
		  <div class="individual-survey text-center"><div class = "individual-holder">Please click on each <b>time instance</b> above to answer a question. You can proceed to the next step when you are done.</div></div>

          <div id = "surveyq">
            <fieldset id = "p0">
			 <!--div class = "row row-margin">
			       <div class="col-md-5 col-lg-5">The body movement showed by the skeleton is something the person actually did.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_1" name="entry.122496811" value="1"  /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_2" name="entry.122496811" value="2" /> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_3" name="entry.122496811" value="3" /> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_4" name="entry.122496811" value="4" /> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_5" name="entry.122496811" value="5" /> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_122496811_6" name="entry.122496811" value="6" /> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_122496811_7" name="entry.122496811"  value="7" /> 7
                </label> 
            </div>
            <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
           	</div>

           	<div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The video pattern matched with the skeleton pattern in most cases.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
	            <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="1" id="group_951552620_1" /> 1
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="2" id="group_951552620_2" /> 2
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="3" id="group_951552620_3" /> 3
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="4" id="group_951552620_4" /> 4
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="5" id="group_951552620_5" /> 5
	                </label>
	                  <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="6" id="group_951552620_6" /> 6
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.951552620" value="7" id="group_951552620_7" /> 7
	                </label> 
	            </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
	        </div-->
           	<div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The body movement pattern is meaningful in the context.</div>
             <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="1" id="group_1904638195_1" /> 1
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="2" id="group_1904638195_2" /> 2
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="3" id="group_1904638195_3" /> 3
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="4" id="group_1904638195_4" /> 4
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="5" id="group_1904638195_5" /> 5
	                </label>
	                  <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="6" id="group_1904638195_6" /> 6
	                </label> 
	                <label class="btn btn-default">
	                    <input type="radio" name="entry.1904638195" value="7" id="group_1904638195_7" /> 7
	                </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>
            <!--div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> The meaning is:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_218713572" name="entry.218713572"></div>
            </div>
            <div class = "row row-margin">
          	  <div class="col-md-5 col-lg-5"> I want to name this pattern as:   </div>
          	  <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_1556891077" name="entry.1556891077" placeholder="pattern name"></div>
          	</div-->  
          </fieldset>		  
            <fieldset id = "p1" style="display:none">
             <!--div class = "row row-margin">
             <div class="col-md-5 col-lg-5">The body movement showed by the skeleton is something the person actually did.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_1" name="entry.1577018710" value="1"  /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_2" name="entry.1577018710" value="2" /> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_3" name="entry.1577018710" value="3" /> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_4" name="entry.1577018710" value="4" /> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_5" name="entry.1577018710" value="5" /> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_6" name="entry.1577018710" value="6" /> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1577018710_7" name="entry.1577018710" value="7" /> 7
                </label> 
            </div>
            <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>

            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The video pattern matched with the skeleton pattern in most cases.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="1" id="group_92779325_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="2" id="group_92779325_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="3" id="group_92779325_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="4" id="group_92779325_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="5" id="group_92779325_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="6" id="group_92779325_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.92779325" value="7" id="group_92779325_7" /> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
          </div-->
            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The body movement pattern is meaningful in the context.</div>
            <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="1" id="group_1346396188_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="2" id="group_1346396188_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="3" id="group_1346396188_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="4" id="group_1346396188_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="5" id="group_1346396188_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="6" id="group_1346396188_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1346396188" value="7" id="group_1346396188_7" /> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>
            <!-- div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> The meaning is:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_524096135" name="entry.524096135"></div>
            </div>
            <div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> I want to name this pattern as:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_974552018" name="entry.974552018" placeholder="pattern name"></div>
            </div-->  
          </fieldset>

          <fieldset id = "p2" style="display:none">
             <!--div class = "row row-margin">
             <div class="col-md-5 col-lg-5">The body movement showed by the skeleton is something the person actually did.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_1" name="entry.2056866798" value="1"  /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_2" name="entry.2056866798" value="2" /> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_3" name="entry.2056866798" value="3" /> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_4" name="entry.2056866798" value="4" /> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_5" name="entry.2056866798" value="5" /> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_6" name="entry.2056866798" value="6" /> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_2056866798_7" name="entry.2056866798"  value="7" /> 7
                </label> 
            </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>

            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The video pattern matched with the skeleton pattern in most cases.</div>
             <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="1" id="group_458959850_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="2" id="group_458959850_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="3" id="group_458959850_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="4" id="group_458959850_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="5" id="group_458959850_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="6" id="group_458959850_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.458959850" value="7" id="group_458959850_7" /> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
          </div-->
            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The body movement pattern is meaningful in the context.</div>
            <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="1" id="group_1686120955_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="2" id="group_1686120955_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="3" id="group_1686120955_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="4" id="group_1686120955_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="5" id="group_1686120955_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="6" id="group_1686120955_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1686120955" value="7" id="group_1686120955_7" /> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>
            <!--div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> The meaning is:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_700362299" name="entry.700362299"></div>
            </div>
            <div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> I want to name this pattern as:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_1069008800" name="entry.1069008800" placeholder="pattern name"></div>
            </div-->  
          </fieldset>

            <fieldset id = "p3" style="display:none">
             <!--div class = "row row-margin">
             <div class="col-md-5 col-lg-5">TThe body movement showed by the skeleton is something the person actually did.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_873246705_1" name="entry.873246705" value="1"  /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_873246705_2" name="entry.873246705" value="2" /> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_873246705_3" name="entry.873246705" value="3" /> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_873246705_4" name="entry.873246705" value="4" /> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_873246705_5" name="entry.873246705" value="5" /> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_873246705_6" name="entry.873246705" value="6" /> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_873246705_7" name="entry.873246705"  value="7" /> 7
                </label> 
            </div>
            <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>

            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The video pattern matched with the skeleton pattern in most cases.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="1" id="group_1206863554_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="2" id="group_1206863554_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="3" id="group_1206863554_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="4" id="group_1206863554_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="5" id="group_1206863554_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="6" id="group_1206863554_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1206863554" value="7" id="group_1206863554_7"/> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
          </div-->
            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The body movement pattern is meaningful in the context.</div>
             <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="1" id="group_25292253_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="2" id="group_25292253_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="3" id="group_25292253_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="4" id="group_25292253_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="5" id="group_25292253_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="6" id="group_25292253_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.25292253" value="7" id="group_25292253_7" /> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>
            <!--div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> The meaning is:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_2071423900" name="entry.2071423900"></div>
            </div>
            <div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> I want to name this pattern as:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_1801888973" name="entry.1801888973" placeholder="pattern name"></div>
            </div-->  
          </fieldset>

          <fieldset id = "p4" style="display:none">
             <!--div class = "row row-margin">
             <div class="col-md-5 col-lg-5">The body movement showed by the skeleton is something the person actually did.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_1" name="entry.1466720155" value="1"  /> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_2" name="entry.1466720155" value="2" /> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_3" name="entry.1466720155" value="3" /> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_4" name="entry.1466720155" value="4" /> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_5" name="entry.1466720155" value="5" /> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_6" name="entry.1466720155" value="6" /> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1466720155_7" name="entry.1466720155" value="7" /> 7
                </label> 
            </div>
            <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>

            <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The video pattern matched with the skeleton pattern in most cases.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="1" id="group_1761467458_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="2" id="group_1761467458_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="3" id="group_1761467458_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="4" id="group_1761467458_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="5" id="group_1761467458_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="6" id="group_1761467458_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1761467458" value="7" id="group_1761467458_7" /> 7
                  </label> 
              </div>
              <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
          </div-->

          <div class = "row row-margin">
            <div class="col-md-5 col-lg-5">The body movement pattern is meaningful in the context.</div>
            <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="1" id="group_1381118731_1" /> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="2" id="group_1381118731_2" /> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="3" id="group_1381118731_3" /> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="4" id="group_1381118731_4" /> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="5" id="group_1381118731_5" /> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="6" id="group_1381118731_6" /> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.1381118731" value="7" id="group_1381118731_7" /> 7
                  </label> 
              </div>
             <div class="col-md-2 col-lg-2">[Strongly Agree]</div>
            </div>
            <!--div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> The meaning is:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_732136702" name="entry.732136702"></div>
            </div>
            <div class = "row row-margin">
              <div class="col-md-5 col-lg-5"> I want to name this pattern as:   </div>
              <div class="col-md-6 col-lg-6"><input type="text" class = "textbox" id="entry_1355157743" name="entry.1355157743" placeholder="pattern name"></div>
            </div-->  
          </fieldset>


            <div class = "row-fluid row-margin">
                <div class="col-md-6 col-lg-6"></div>
                <div class="col-md-6 col-lg-6">
                    <button class="btn btn-default disabled" type="button" id = "next" onclick="next_pattern();">Next Pattern</button>
                    <!--button id = "previous">Previous</button-->
              </div>
            </div>
          </div></div>
          <div class="col-md-4 col-lg-4" id = "pieChartdiv"></div>
      </div>

    <!--div class = "row" id = "post-q" style="display:none">
          <fieldset>
             <div class = "row row-margin">
             <div class="col-md-6 col-lg-6">How helpful was the feedback?</div>
              <div class="col-md-2 col-lg-2">[Not helpful]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_1" name="entry.1973339660" value="1"/> 1
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_2" name="entry.1973339660" value="2"/> 2
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_3" name="entry.1973339660" value="3"/> 3
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_4" name="entry.1973339660" value="4"/> 4
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_5" name="entry.1973339660" value="5"/> 5
                </label>
                  <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_6" name="entry.1973339660" value="6"/> 6
                </label> 
                <label class="btn btn-default">
                    <input type="radio" id="group_1973339660_7" name="entry.1973339660" value="7"/> 7
                </label> 
            </div>
            <div class="col-md-1 col-lg-1">[Extremely Helpful]</div>
            </div>

            <div class = "row row-margin">
            <div class="col-md-6 col-lg-6">The feedback made me aware of the person's body language.</div>
              <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
              <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="1" id="group_2021115824_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="2" id="group_2021115824_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="3" id="group_2021115824_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="4" id="group_2021115824_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="5" id="group_2021115824_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="6" id="group_2021115824_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.2021115824" value="7" id="group_2021115824_7"/> 7
                  </label> 
              </div>
              <div class="col-md-1 col-lg-1">[Strongly Agree]</div>
          </div>
          <div class = "row row-margin">
            <div class="col-md-6 col-lg-6">The feedback made me aware of at-least one gesture that the person make too frequently.</div>
             <div class="col-md-2 col-lg-2">[Strongly Disagree]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="1" id="group_543518954_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="2" id="group_543518954_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="3" id="group_543518954_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="4" id="group_543518954_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="5" id="group_543518954_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="6" id="group_543518954_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.543518954" value="7" id="group_543518954_7"/> 7
                  </label>
              </div>
              <div class="col-md-1 col-lg-1">[Strongly Agree]</div> 
            </div>
          <div class = "row row-margin">
            <div class="col-md-6 col-lg-6">How often would you use the system if it were available?</div>
             <div class="col-md-2 col-lg-2">[Never]</div>
             <div class="col-md-3 col-lg-3 btn-group" data-toggle="buttons">
                  <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="1" id="group_840577731_1"/> 1
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="2" id="group_840577731_2"/> 2
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="3" id="group_840577731_3"/> 3
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="4" id="group_840577731_4"/> 4
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="5" id="group_840577731_5"/> 5
                  </label>
                    <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="6" id="group_840577731_6"/> 6
                  </label> 
                  <label class="btn btn-default">
                      <input type="radio" name="entry.840577731" value="7" id="group_840577731_7"/> 7
                  </label>
              </div>
              <div class="col-md-1 col-lg-1">[All the time]</div>

            </div>
             <div class = "row row-margin">
                <div class="col-md-5 col-lg-5"></div>
                <div class="col-md-6 col-lg-6">
                    <input id="complete" type="submit" name="submit" value="Complete Post-Survey" id="ss-submit" class="jfk-button jfk-button-action btn btn-default disabled">
              </div!>
            </div>
          </fieldset>

      </div-->
	  <input type="hidden" class = "textbox" id="entry_247949180" name="entry.247949180" value="<?php echo $datakey; ?>">

      </form>
	  <fieldset style="display:none;" id = "turk-post" >
	  <div class = "row row-margin">
		<center>
			<h1>Thank you for completing the study!</h1>
			</br>
			<h4>Please Copy and Paste this Session ID into the desingated box on Mechanical Turk</h4>
			<br>
			<h1 style="width:50%;border-style:dashed;border-width: medium;" onclick="autoSelect();"> <?php echo $datakey; ?> </h1>
        </center>
		</div>
	  </fieldset>
    </div>
    <script src="OrbitControls.js"></script>
    <script src="gui.js"></script>
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