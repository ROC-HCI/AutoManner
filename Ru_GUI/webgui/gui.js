var chart;
//var id = getQSParam('id');
var numofPatterns;
var loopstopper =[];
var color = ["#0099CC","#999900", "#FF9900","#FFFF00","#CC66FF"];
var patternIndex = [];
var chartData = [];
var current = 0;
var piechartDataProvider;
var piechart;
var stage = 1;
var videoplayed = false;
var clickedallflag = false;

var intervalRewind = [];
$('#video').on('play',function(){
    //$("#play").html("pause(realtime) ||");
    $("#ffwd").html("&#10074;&#10074;");
    $("#play").html("&#10074;&#10074;");

    //myVid.playbackRate = 1.0;
    //clearAllTimeout(loopstopper);
    clearAllInterval(intervalRewind);
});
$('#video').on('pause',function(){
    //$("#play").html("play &#9654;");
	if(myVid.playbackRate == 1 && stage == 2)
		$("#ffwd").html("&#9654;");
	else
		$("#ffwd").html("&#9654;&#9654;");
    $("#play").html("&#9654;");

    myVid.playbackRate = 1.0;
    //clearAllTimeout(loopstopper);
    partialer = false;
    clearAllInterval(intervalRewind);
});

var timeTracker = 0;

$('#video').on('timeupdate',function(){

	if(!videoplayed){
		var totalSec = parseInt(myVid.duration, 10)*3; // don't forget the second param
		timeTracker++;
		//console.log("max me " + totalSec);
		console.log(timeTracker);
		if(myVid.currentTime == myVid.duration)
		{
			if(timeTracker > totalSec)
			{
				timeTracker = 0;
				$('#mturk_info').html("<h3 style = 'color:cyan'>You did not completly watch the video, please go back and start from the beggining.</h3>");
			}
			else
			{
				videoplayed = true;
				$("#topContainer").removeClass("col-md-offset-3");
				$("#topContainer").removeClass("col-lg-offset-3");
				$("#pre-q").show();
				$("#instructionset").html("<fieldset><li>Answer each question.</li> <li>You may replay the video as much as you like.</li><li><font color=cyan>Tips</font> : Fast forwarding the video will help you to see the body gestures more visibly.</li><li>After you have answered the questions, press submit to move to the next step.</li>");
				$("#ffwd").show();

				//document.getElementById('mturk_info').style.display = 'none';
				//document.getElementById('mturk_form').style.display = 'block';
			}
		}
		else
		{
			//$('#mturk_info2').html("");
		}
	}else{
    var graphWidth = $("#timelineChartdiv svg > g:nth-last-child(15) > rect:last-child").attr("width");
    var translateX = parseFloat(graphWidth)*myVid.currentTime/myVid.duration;
    //$("#timelineChartdiv svg > g:nth-last-child(9)").attr("transform","translate("+translateX+",0)");
    //$("#timelineChartdiv svg > g:nth-last-child(9)").attr("visibility","visible");
    //$("#timelineChartdiv svg > g:nth-last-child(9)").html("<path cs='100,100' d='M0.5,0.5 L28.5,0.5 L34.5,-4.5 L40.5,0.5 L68.5,0.5 L68.5,23.5 L0.5,23.5 L0.5,0.5 Z' fill='#FFFFFF' stroke='#FFFFFF' fill-opacity='1' stroke-width='1' stroke-opacity='1'></path>");
    //$("#timelineChartdiv svg > g:nth-last-child(8) > g").html("<path cs='100,100' d='M0.5,0.5 L28.5,0.5 L34.5,-4.5 L40.5,0.5 L68.5,0.5 L68.5,23.5 L0.5,23.5 L0.5,0.5 Z' fill='#FFFFFF' stroke='#FFFFFF' fill-opacity='1' stroke-width='1' stroke-opacity='1'></path>");
    $("#timelineChartdiv svg > g:nth-last-child(8) > g > path:last-child").attr("transform","translate("+translateX+",0)");
    $("#timelineChartdiv svg > g:nth-last-child(8) > g > path:last-child").attr("visibility","visible");
	}
});

$("#ffwd").click(function() { // button function for 3x fast speed forward
    //clearAllTimeout(loopstopper);.
    if(myVid.paused)
        myVid.play();
    else
        myVid.pause();
    if($('#realtime').is(":checked"))
        myVid.playbackRate = 1;
    else
        myVid.playbackRate = 5;
});

$("#play").click(function() { // button function for 3x fast speed forward
    //clearAllTimeout(loopstopper);
    if(myVid.paused)
        myVid.play();
    else
        myVid.pause();
});

$('input[name=realtime]').change(function(){

    if($(this).is(':checked'))
    {
        // Checkbox is checked.
        myVid.playbackRate = 1.0;
		
		if(myVid.paused)
			$("#ffwd").html("&#9654;");

    }
    else
    {
        // Checkbox is not checked.
        myVid.playbackRate = 5.0;
        partialer = false;
		
		if(myVid.paused)
			$("#ffwd").html("&#9654;&#9654;");
    }    

});

$("#reset").click(function() { // button function for 3x fast speed forward
    //clearAllTimeout(loopstopper);
    myVid.currentTime = 0;
});

  var seekBar = document.getElementById("seek-bar");

  var timenow = document.getElementById("time-now");

  // Event listener for the seek bar
  seekBar.addEventListener("change", function() {
    // Calculate the new time
    var time = myVid.duration * (seekBar.value / 100);

    // Update the video time
    myVid.currentTime = time;
  });

  // Update the seek bar as the video plays
  $('#video').on("timeupdate", function() {
    // Calculate the slider value
    var value = (100 / myVid.duration) * myVid.currentTime;
    
    // Update the slider value
    seekBar.value = value;

    var total_minute=myVid.duration/60;
    var now_minute=myVid.currentTime/60;
    var display_second;
    if(myVid.currentTime%60<10){
      display_second="0"+Math.round(myVid.currentTime%60);
    } else{
      display_second=Math.round(myVid.currentTime%60);
    }

    timenow.innerHTML= "0"+ parseInt(now_minute)+":"+display_second;
  });

  // Pause the video when the seek handle is being dragged
  seekBar.addEventListener("mousedown", function() {
    myVid.pause();
    //ga('send', 'event', 'video_seek_bar', 'click', dataKey);
    //console.log("sent video_seek_bar to ga");
  });

  // Play the video when the seek handle is dropped
  seekBar.addEventListener("mouseup", function() {
    if (myVid.paused) {
      myVid.pause();
    } else {
      myVid.play();
    }
  });


$("#rewind").click(function() { // button function for rewind
   intervalRewind.push(setInterval(function(){
       myVid.playbackRate = 1.0;
       if(myVid.currentTime == 0){
           clearAllTimeout(loopstopper);
           clearAllInterval(intervalRewind);
           myVid.pause();
       }
       else{
           myVid.currentTime += -.1;
       }
                },30));
});


function drawPieChart(data) {
    piechartDataProvider = [];

    for(var i = 0; i < data.length; i++)
	{
		if(i == 0)
			piechartDataProvider.push({"pattern": data[i].category, "color": data[i].segments[0].color, count : data[i].segments.length});
	    else
			piechartDataProvider.push({"pattern": data[i].category, "color": "#848484", count : data[i].segments.length});
	}
    piechart = AmCharts.makeChart( "pieChartdiv", {
      "type": "pie",
      "theme": "dark",
      "dataProvider": piechartDataProvider,
      "valueField": "count",
      "colorField" : "color",
      "titleField": "pattern",
	  "pullOutOnlyOne": true,
      "export": {
      "enabled": true}
    });

}

function drawTimeline() {
    /*var patternChartFormattedData;

     patternChartFormattedData.push({
        "balloonText": "<b style='font-size:18px'>[[title]]</b>",
        "fillAlphas": fillAlphas,
        "lineColor": lineColor,
        "lineThickness": CHART_LINE_THICKNESS,
        "lineAlpha": lineAlpha,
        "labelText": "[[title]]",
        "title": title,
        "type": "column",
        "color": "#000000",
        "valueField": elem,
        "id": elem,
        "visibleInLegend": visibleInLegend,
        "columnWidth": columnWidth,
        "pointPosition": "end",
        "showAllValueLabels": showAllValueLabels
      });

    patternchartDiv = AmCharts.makeChart("patternchartDiv", {
        "fontFamily": "Lato",
        "marginTop": -120,
        "type": "serial",
        "rotate": true,
        "dataProvider": patternChartFormattedData,
        "autoMargins": false,
        "marginLeft": 0,
        "marginRight": 0,
        "creditsPosition": "top-left",
        "valueAxes": [{
            "stackType": "100%",
            "axisAlpha": 0,
            "gridAlpha": 0,
            "labelsEnabled": false,
            "precision":8
        }],
        "balloon": {
          "fillAlpha": 0.9,
          "animationDuration":0
        },
        "chartCursor": {
          "valueLineEnabled": true,
          "valueBalloonsEnabled": false,
          "categoryBalloonEnabled": false,
          "cursorColor": "1red",
          "valueLineAlpha": 1,
          "cursorAlpha": 0,
          "valueLineBalloonEnabled":true,
          "cursorPosition":"mouse",
          "categoryBalloonAlpha": 0,
          "categoryBalloonColor": "transparent",
          "zoomable": false,
          "animationDuration": 0
        },
        "graphs":transcriptGraphs,
        "categoryField": "session",
        "categoryAxis": {
          "axisAlpha": 0,
          "gridAlpha": 0,
          "labelsEnabled": false
        }
    });*/

    AmCharts.useUTC = true;
	/*$.get( "Data/13.3.csv", function( data ) {
		//$( "#result" ).html( data );
		var csv = Papa.parse(data);
		console.log(csv);
	});*/
    console.log(myVid.duration)
	
    var path = "Data/" + folder_dir + "/timeline_" + id + ".csv";
    $.get( path, function( data ) {
	//$.get( "Data/timeline.csv", function( data ) {
		//$( "#result" ).html( data );
		var csv = Papa.parse(data);
		console.log(csv);
	
	//console.log(myVid.duration);
    //console.log(Math.floor(csv['data'][csv['data'].length-2][0]));
    var lastindex = csv['data'].length-1;

    //trim last line
    if(csv['data'][lastindex].length < 3)
        csv['data'].splice(lastindex, lastindex);

    for(var i = 0; i <= Math.floor(csv['data'][csv['data'].length-1][0]); i++)
    {
        console.log(i);
        chartData.push({"category": "", "segments" : []});
    }
    //console.log(chartData);

	//console.log(chartData["category"]);
	//console.log(chartData[0]["category"]);

	for(var i = 1; i < csv['data'].length; i++)
	{
        console.log(csv['data'][i]);
        //Math.floor(csv['data'][i][0])
		chartData[Math.floor(csv['data'][i][0])]['segments'].push({
			"start": csv['data'][i][1],
			"end": csv['data'][i][2],
			"color": color[Math.floor(csv['data'][i][0])],
			"task": csv['data'][i][0],
        });
	}

    chartData.sort(function(a, b){return b['segments'].length-a['segments'].length});

    for(var i = 0; i < chartData.length; i++)
    {
        chartData[i].category = "Pattern " + (i+1);
        if(chartData[i].segments.length <=1)
        {
            //console.log("hi");
            chartData.length = i;
            break;
        }
        patternIndex.push(Math.floor(chartData[i].segments[0].task));
        //console.log("patternIndex", patternIndex);
    }

    if(chartData.length < 3 && isFirstVid)
        $("#movewarning").show();

    numofPatterns = chartData.length-1;


    console.log(chartData);

	chart = AmCharts.makeChart( "timelineChartdiv", {
		"type": "gantt",
		"theme": "dark",
		"marginRight": 70,
		"period": "ss",
		"dataDateFormat":"NN:SS",
		"balloonDateFormat": "NN:SS",
		"columnWidth": 0.5,
		"addClassNames" : true,
		"valueAxis": {
			"type": "date",
			"minimum": 0,
			"maximum":  Math.ceil(myVid.duration)
		},
		"brightnessStep": 0,
		"graph": {
			"fillAlphas": 1,
			//"balloonText": "<b>[[task]]</b>: [[open]] [[value]]"
			//"balloonText": "<b>[[task]]</b>: starttime:[[start]] endtime:[[end]]"
            "balloonText": ""
		},
		"rotate": true,
		"categoryField": "category",
		"segmentsField": "segments",
		"colorField": "color",
		"startDate": "00:00",
		"startField": "start",
		"endField": "end",
		"durationField": "duration",
		"dataProvider": chartData,
		"chartCursor": {
			"valueBalloonsEnabled": false,
			"cursorAlpha": 0,
            "cursorColor":"#FFFF00",
            "valueLineAlpha": 1,
			"valueLineBalloonEnabled": true,
			"valueLineEnabled": true,
			"fullWidth": true,
            "valueLineEnabled": true,
              /*"valueBalloonsEnabled": false,
              "categoryBalloonEnabled": false,
              "valueLineEnabled": true,
              "cursorColor": "red",
              "valueLineAlpha": 1,
              "cursorAlpha": 1,
              "valueLineBalloonEnabled":true,
              "cursorPosition":"mouse",
              "categoryBalloonAlpha": 0,
              "categoryBalloonColor": "transparent",
              "animationDuration": 0*/
		},
		"export": {
			"enabled": true
		 }
	} );
    
    //chart.zoomToIndexes(0, 0);
    drawPieChart(chartData);
	

    /*var selectorHtml ="";
    for(var i = 0; i <= Math.floor(csv['data'][csv['data'].length-1][0]); i++)
    {
        selectorHtml += "<button type ='button' class = 'btn btn-primary' onclick=\"zoomToIndexes(chart,"+i+","+i+")\">Pattern "+(i+1)+"</button>";
    }
    $("#patternselector").html(selectorHtml);*/

    //console.log(chart.chartCursor);

	chart.addListener("clickGraphItem", handleClick);
    //console.log(chart.chartCursor.showCursorAt(2));
    myVid.addEventListener("timeupdate", function() {   
        //console.log(chart.chartCursors);
        //.showCursorAt(myVid.currentTime);
    });

	});
}

function zoomToIndexes(chart, start, end)
{
    chart.zoom(start,end);
    console.log("zoomindex", patternIndex[start]);
    showPattern(patternIndex[start],0,0,false);
    $('#realtime').prop('checked', false);
    myVid.currentTime = 0;
    myVid.pause();
    myVid.playbackRate = 5.0;
}

function clickYes(itemrowposition, itemcolumnposition)
{
	chartData[itemrowposition]['segments'][itemcolumnposition].color = "#00FF00";
	chart.validateData();
	chart.zoom(itemrowposition,itemrowposition);
	$(".yes").addClass("disabled");
	$(".no").removeClass("disabled");
	
	transition();
}

function transition()
{
	var overlapflag = false;
	var maxtime = myVid.duration;
	var segments = chartData[current]['segments'];
	for(var i = 0; i < segments.length; i++) {
		//console.log(segments[i].color);
		if(segments[i].color !== "#FF0000" && segments[i].color !== "#00FF00" && segments[i].end <= maxtime)
		{
			//test if an overlap has a been answered
			if(i == segments.length-1 && segments[i].start == 0)
			{
				for(var j = 0; j < segments.length-1; j++ )
				{
					//if(segments[i].start < segments[j].end && segments[j].start < segments[i].end)
					if(segments[j].start == 0)
					{
							/*if(segments[j].color == "#FF0000" || segments[j].color == "#00FF00")
							{
								console.log(segments[i].task);	
								console.log(segments[j].task);	
							}
							else
							{
								console.log(segments[i].task);	
								console.log(segments[j].task);
								return;;
							}*/
						overlapflag = true;
							
					}
				}
				
				if(overlapflag == false)
				{
					console.log(segments[i].task);
					return;
				}	
			}else{
				console.log(segments[i].task);
				return;
			}
		}
	
	}
	console.log("hello");
	
	clickedallflag = true;
	$('.individual-survey').css("display", "none");
	$('#surveyq').css("display", "block");

	//$('#next').removeClass('disabled');
}

function clickNo(itemrowposition, itemcolumnposition)
{
	chartData[itemrowposition]['segments'][itemcolumnposition].color = "#FF0000";
	chart.validateData();
	chart.zoom(itemrowposition,itemrowposition);
	$(".no").addClass("disabled");
	$(".yes").removeClass("disabled");
	
	transition();
}

function handleClick(event)
{
	console.log(event.item);
	//var column = event.item.columnGraphics.node.childNodes[0];
    //column.setAttribute("stroke","#000000");
    //column.setAttribute("fill","#FFFFFF");

	if(!clickedallflag)
	{

	$("#surveyq").hide();
	$(".individual-survey").show();

	var itemrowposition = event.item.index; 
	var itemcolumnposition = event.item.graph.customData.task;
	itemcolumnposition = (itemcolumnposition + "").split(".")[1];
	console.log(chartData);
	var itemcolor = chartData[itemrowposition]['segments'][itemcolumnposition].color;
	
	var disabledyes = "";
	var disabledno = "";
	if(itemcolor != "#FFFFFF")
	{
		if(itemcolor == "#00FF00")
		{
			disabledyes = "disabled";
		}else if(itemcolor == "#FF0000"){
			disabledno = "disabled";
		}else{
			chartData[itemrowposition]['segments'][itemcolumnposition].color = "#FFFFFF";
			chart.validateData();
			chart.zoom(event.item.index,event.item.index);
		}
	}
	
	$(".individual-survey").html("<div class='individual-prompt'><p>Does the skeleton matches with the body gesture of the person?</p> <p class='tip'>You can adjust the slider below the skeleton to make the movements more prominent or subtle. </p> <button type='button' class = 'btn btn-default yes "+disabledyes+"' onclick=clickYes("+itemrowposition + "," + itemcolumnposition +")>Yes</button><button type='button' class='btn btn-default no "+disabledno+"' onclick=clickNo("+itemrowposition + "," + itemcolumnposition +")>No</button></div>");
	}
    //$('#realtime').prop('checked', true);
    myVid.playbackRate = 1.0;
    clearAllTimeout(loopstopper);
    clearAllInterval(intervalRewind);
	myVid.currentTime = event.item.graph.customData.start;
	console.log("hello",event.item.graph.customData);
    //alert(event.item.category + ": " + event.item.graph.customData.start);
    showPattern(patternIndex[event.item.index],event.item.graph.customData.start,event.item.graph.customData.end, true);
    myVid.play();
}

var verticesSphere = [];
var verticesLine = [];
var camera;
var scene;
var renderer;
var csv;
var paused = false;
var animating = true;
var starter;
var partialer;
var controls;

var framecounter = 0;

function animate(t) {
    if (!paused) {
        last = t;
        if (animating) {
            if(framecounter > 63)
            { 
                console.log(starter);
                framecounter = 0;
                console.log(starter + "--" + partialer);
                if(partialer)
                {
                    myVid.currentTime = starter;
                    myVid.play();
                }
            }

            var verticesF = [];

        for (var i = 0; i < csv['data'][framecounter].length; i+=3) {
                    //console.log(framecounter);
             var value = $( "#slider" ).slider( "value" );
                    //console.log(value);
             verticesF.push(new THREE.Vector3(value*csv['data'][framecounter][i]+parseFloat(csv['data'][64][i]), value*csv['data'][framecounter][i+1]+parseFloat(csv['data'][64][i+1]), value*csv['data'][framecounter][i+2]+parseFloat(csv['data'][64][i+2])));
                    //console.log(verticesF);
             updateJointPosition(verticesF);


            }
            framecounter+=1;
        }
        renderer.clear();
        camera.lookAt(scene.position);
        renderer.render(scene, camera);
    }
};

function playskeleton()
{
    if(animating)
    {
        $("#skeleplay").html("&#9654;");
    }else
    {
        $("#skeleplay").html("&#10074;&#10074;");
    }

    animating = !animating;
}


function updateJointPosition(vertices)
{
        //console.log(verticesSphere);
        for(var i = 0; i < vertices.length ; i++){
            //console.log(i);
            verticesSphere[i].position.set(vertices[i].x, vertices[i].y, vertices[i].z);
        } 

        //drawSkeleton(scene, vertices, .1, .1);

        //updateBones(verticesLine[0].geometry.vertices, vertices.slice(0, 4));
        verticesLine[0].geometry.dynamic = true;
        verticesLine[0].geometry.vertices = vertices.slice(0, 4);
        verticesLine[0].geometry.verticesNeedUpdate = true;

        
        verticesLine[1].geometry.dynamic = true;
        var vertex = vertices.slice(4, 8);
        vertex.splice(0,0,vertices[2]);
        verticesLine[1].geometry.vertices = vertex;
        verticesLine[1].geometry.verticesNeedUpdate = true;

        
        verticesLine[2].geometry.dynamic = true;
        //updateBones(verticesLine[1].geometry.vertices, vertex);
        var vertex2 = vertices.slice(8, 12);
        vertex2.splice(0,0,vertices[2]);
        verticesLine[2].geometry.vertices = vertex2;
        verticesLine[2].geometry.verticesNeedUpdate = true;


        verticesLine[3].geometry.dynamic = true;
        //updateBones(verticesLine[2].geometry.vertices, vertex2);
        var vertex3 = vertices.slice(12, 16);
        vertex3.splice(0,0,vertices[0]);
        verticesLine[3].geometry.vertices = vertex3;
        verticesLine[3].geometry.verticesNeedUpdate = true;

        
        //updateBones(verticesLine[3].geometry.vertices, vertex3);
        verticesLine[0].geometry.dynamic = true;
        var vertex4 = vertices.slice(16, 19);
        vertex4.splice(0,0,vertices[0]);
        verticesLine[4].geometry.vertices = vertex4;
        verticesLine[4].geometry.verticesNeedUpdate = true;

        //updateBones(verticesLine[4].geometry.vertices, vertex4);
    }
var setup = false;

function setupSkele()
{
    var skeletonElement = document.getElementById("skeletonContainer");
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(document.getElementById('skeletonContainer').offsetWidth, document.getElementById('skeletonContainer').offsetHeight);
    //skeletonElement.empty();
    $('#skeletonContainer').empty();
    skeletonElement.appendChild(renderer.domElement);
    camera = new THREE.PerspectiveCamera(2, window.innerWidth / window.innerHeight, 1, 500);
    camera.position.set(0, 0, -60);
    camera.lookAt(new THREE.Vector3(0, 0, 10));
    controls = new THREE.OrbitControls( camera, renderer.domElement );
    scene = new THREE.Scene();
    var skeleton = new THREE.Object3D();
    scene.add(skeleton);
}

function showPattern(pattern, start, end, partial)
{
	$("#display").html("<font size='5' color='"+color[pattern]+"'>Pattern "+(patternIndex.indexOf(pattern)+1)+"</font>");
    $("#skeleplay").html("&#10074;&#10074;");

    if(setup == false)
        setupSkele();
 	//var verticesSphere = [];
    //var verticesLine = [];
    partialer = partial;
    starter = start;

    var jointSizes = [0.09,0.1,0.1,0.2,0.1,0.1,0.08,0.08,0.1,0.1,0.08,0.08,0.1,0.1,0.1,0.09,0.1,0.1,0.1,0.09];

    /*var skeletonElement = document.getElementById("skeletonContainer");
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(document.getElementById('skeletonContainer').offsetWidth, document.getElementById('skeletonContainer').offsetHeight);
    //skeletonElement.empty();
    $('#skeletonContainer').empty();
    skeletonElement.appendChild(renderer.domElement);
    camera = new THREE.PerspectiveCamera(2, window.innerWidth / window.innerHeight, 1, 500);
    camera.position.set(0, 0, -60);
    camera.lookAt(new THREE.Vector3(0, 0, 10));
    var controls = new THREE.OrbitControls( camera, renderer.domElement );
    scene = new THREE.Scene();
    var skeleton = new THREE.Object3D();
    scene.add(skeleton);*/

    //skeleton.add(material);
    var file = "Data/" + folder_dir + "/tdp_" + pattern + "_" + id +".csv";
    //      var file = "Data/skele_" + pattern + ".csv";
    $.get( file, function( data ) {
        //$( "#result" ).html( data );
        csv = Papa.parse(data);
        //console.log(csv);
    
    renderer.setClearColor(0xFFFFFF, 1.0);
    
    ///////////
    // LIGHT //
    ///////////
    
    // create a light
    /*var light = new THREE.PointLight(0xffffff);
    light.position.set(0,250,0);
    scene.add(light);
    var ambientLight = new THREE.AmbientLight(0x111111);
    // scene.add(ambientLight);
    
    //////////////
    // GEOMETRY //
    //////////////
        
    // most objects displayed are a "mesh":
    //  a collection of points ("geometry") and
    //  a set of surface parameters ("material")    
    // Sphere parameters: radius, segments along width, segments along height
    var sphereGeometry = new THREE.SphereGeometry( .1, 10, 10 ); 
    // use a "lambert" material rather than "basic" for realistic lighting.
    //   (don't forget to add (at least one) light!)
    var sphereMaterial = new THREE.MeshLambertMaterial( {color: 0x8888ff} ); 
    var sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    sphere.position.set(0, 0, 0);
    scene.add(sphere);*/

    ///////////
    // FLOOR //
    ///////////
    
    // note: 4x4 checkboard pattern scaled so that each square is 25 by 25 pixels.
    /*ar floorTexture = new THREE.ImageUtils.loadTexture( 'images/checkerboard.jpg' );
    floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping; 
    floorTexture.repeat.set( 10, 10 );
    // DoubleSide: render texture on both sides of mesh
    var floorMaterial = new THREE.MeshBasicMaterial( { map: floorTexture, side: THREE.DoubleSide } );
    var floorGeometry = new THREE.PlaneGeometry(1000, 1000, 1, 1);
    var floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = -0.5;
    floor.rotation.x = Math.PI / 2;
    scene.add(floor);
*/

    var vertices = [];
    for(var i = 0; i < csv['data'][0].length; i+=3)
    {
        //console.log(csv['data'][0][i]);
        vertices.push(new THREE.Vector3(csv['data'][0][i], csv['data'][0][i+1], csv['data'][0][i+2]));
        //geometry.vertices.push(new THREE.Vector3(-10, 0, 0));
        //geometry.vertices.push(new THREE.Vector3(0, 10, 0));
        //geometry.vertices.push(new THREE.Vector3(10, 0, 0));
    }

    //var line = new THREE.Line(geometry, material);
    //skeleton.scale.set(10,10,10);
    if(setup == false)
    {
        makeSphereVertices(scene, vertices);
        drawSkeleton(scene, vertices, .1, .1);
        setup = true;
    }
    //drawCylinder(geometry.vertices[0], vertices[1],scene);
    //skeleton.add(boxline);
    //scene.add(line);

    renderer.render(scene, camera);

    paused = false;
    var last = new Date().getTime();
    var down = false;
    /*var sx = 0,
        sy = 0;
        
    window.onmousedown = function(ev) {
        down = true;
        sx = ev.clientX;
        sy = ev.clientY;
    };
    window.onmouseup = function() {
        down = false;
    };
    window.onmousemove = function(ev) {
        if (down) {
            var dx = ev.clientX - sx;
            var dy = ev.clientY - sy;
            skeleton.rotation.y += dx * 0.01;
            camera.position.y += dy;
            sx += dx;
            sy += dy;
        }
    }*/
    animating = true;
    window.ondblclick = function() {
        animating = !animating;
        myVid.currentTime = start;
        myVid.play();
        if(!animating)
           myVid.pause();
    };


    /*var framecounter = 0;
    function animate(t) {
        if (!paused) {
            last = t;
            if (animating) {
                //var v = pointGeo.vertices;
                if(framecounter > 63)
                { 
                    console.log(start);
                    framecounter = 0;
                    if(partial)
                    {
                        myVid.currentTime = start;
                        myVid.play();
                    }
                }

                var verticesF = [];


                for (var i = 0; i < csv['data'][framecounter].length; i+=3) {
                    //console.log(framecounter);
                    var value = $( "#slider" ).slider( "value" );
                    //console.log(value);
                    verticesF.push(new THREE.Vector3(value*csv['data'][framecounter][i]+parseFloat(csv['data'][64][i]), value*csv['data'][framecounter][i+1]+parseFloat(csv['data'][64][i+1]), value*csv['data'][framecounter][i+2]+parseFloat(csv['data'][64][i+2])));
                    //console.log(verticesF);
                    updateJointPosition(verticesF);



                }
                 framecounter+=1;
            }
            renderer.clear();
            camera.lookAt(scene.position);
            renderer.render(scene, camera);
        }

        loopstopper.push(setTimeout(function() {
            controls.update();
            window.requestAnimationFrame(animate, renderer.domElement);
        }, 50));
    };*/
    framecounter = 0;
    clearAllInterval(loopstopper);
    loopstopper.push(setInterval(function() {
        controls.update();
        window.requestAnimationFrame(animate, renderer.domElement);
    }, 50));


    animate(new Date().getTime());

    onmessage = function(ev) {
        paused = (ev.data == 'pause');
    };

    });




    //draw joints
    function makeSphereVertices(scene, vertices){
        //console.log("makesphere");

        spheres = [];
        //console.log(geometryContainer);

        for(var i = 0; i < vertices.length ; i++){
            //console.log(vertices[i].x);
            var color;
            switch(i){
            	case 3:
					color = 0xcc0000;
            		break;
            	case 6:
            	case 7:
            	case 10:
            	case 11:
            		color = 0x72a0e5;
            		break;
            	case 15:
            	case 19:
            	case 0:
            		color = 0x0000ff;
            		break;
            	default:
            		color = 0x00000;

            }

            var sphereGeometry = new THREE.SphereGeometry(0.5*jointSizes[i],10,10);//relative to dimension object : ToDo
            //var sphereMaterial = new THREE.MeshLambertMaterial( {color: 0x8888ff} ); 
            var sphereMaterial = new THREE.MeshNormalMaterial({color: 0x821717});

            spheres = new THREE.Mesh(sphereGeometry,sphereMaterial);
            spheres.position.set(vertices[i].x, vertices[i].y, vertices[i].z);
            scene.add(spheres);
            verticesSphere.push(spheres);
        }

    }

    //draw bones
    function drawSkeleton(scene, vertices, width, height)
    {
        /*var vertex, geometry, material, mesh;
        var segments = new THREE.Object3D();
        //vertices = vertices.map(convert);

        for (var i = 0, len = vertices.length - 1; i < len; i++) {
            vertex = vertices[i];
            geometry = new THREE.BoxGeometry(width, height, 1);
            material = new THREE.MeshNormalMaterial({
                opacity: 0.5,
                transparent: true
            });

            mesh = new THREE.Mesh(geometry, material);
            mesh.position = vertex;
            mesh.lookAt(vertices[1 + i]);

            length = vertex.distanceTo(vertices[1 + i]);
            //mesh.scale.set(1, 1, length + width);
            //mesh.translateZ(0.5 * length);
            segments.add(mesh);
        }
        return segments;*/
        
        /*var points = [];
        for (var i = 0; i < vertices.length; i++) {
            var randomX = Math.round(vertices[i].x);
            var randomY = Math.round(vertices[i].y);
            var randomZ = Math.round(vertices[i].z);
       
            points.push(new THREE.Vector3(randomX, randomY, randomZ));
            console.log(points[i]);
        }

        var tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.SplineCurve3(points), 1, 2), new THREE.MeshLambertMaterial({ color:0x000000 }));
        tube.rotation.y = -Math.PI / 2;
        tube.position.x = 0;
        tube.position.y = 1;
        tube.position.z = 0;
        tube.castShadow = tube.receiveShadow = true;
        scene.add(tube);*/
        var material = new THREE.LineBasicMaterial({
            color: 0x0000ff
        });
        drawBones(scene, vertices.slice(0, 4), material);
        var vertex = vertices.slice(4, 8);
        vertex.splice(0,0,vertices[2]);
        drawBones(scene, vertex, material);
        var vertex2 = vertices.slice(8, 12);
        vertex2.splice(0,0,vertices[2]);
        drawBones(scene, vertex2, material);
        var vertex3 = vertices.slice(12, 16);
        vertex3.splice(0,0,vertices[0]);
        drawBones(scene, vertex3, material);
        var vertex4 = vertices.slice(16, 19);
        vertex4.splice(0,0,vertices[0]);
        drawBones(scene, vertex4, material);


    }

    function drawBones(scene, vertices, material)
    {
        //var curve = new THREE.SplineCurve3(vertices);
        //var geometry = new THREE.TubeGeometry(curve);
        var linegeometry = new THREE.Geometry()
        linegeometry.vertices =  vertices;
        var line = new THREE.Line(linegeometry, material);
        verticesLine.push(line);
        scene.add(line);
    }



    function drawCylinder(vstart,vend,scene){
        var HALF_PI = Math.PI * .5;
        var distance = vstart.distanceTo(vend);
        var position  = vend.clone().add(vstart).divideScalar(2);

        var material = new THREE.MeshLambertMaterial({color:0x0000ff});
        var cylinder = new THREE.CylinderGeometry(3,3,distance,3,3,false);

        var orientation = new THREE.Matrix4();//a new orientation matrix to offset pivot
        var offsetRotation = new THREE.Matrix4();//a matrix to fix pivot rotation
        var offsetPosition = new THREE.Matrix4();//a matrix to fix pivot position
        orientation.lookAt(vstart,vend,new THREE.Vector3(0,1,0));//look at destination
        offsetRotation.makeRotationX(HALF_PI);//rotate 90 degs on X
        orientation.multiply(offsetRotation);//combine orientation with rotation transformations
        cylinder.applyMatrix(orientation)

        var mesh = new THREE.Mesh(cylinder,material);
        mesh.position=position;
        scene.add(mesh);
    }
}

function getQSParam(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : results[1].replace(/\+/g, " ");
}

function complete_presurvey() {
	$("#topContainer").removeClass("col-md-6");
	$("#topContainer").removeClass("col-lg-6");
    $('#videoContainerOuter').addClass("col-md-6 col-lg-6");
    $('#skeletonContainerOuter').css("display", "block");
    $('#pre-q').css("display", "none");
    $('#in-q').css("display", "block");
    //showPattern(0, 0, 0, false);
    zoomToIndexes(chart,0,0);
	stage = 2;
	$("#play").hide();
	$("#ffwd").css("width", "55%");
	$("#realcheck").show();
	$("#instructionset").hide();


}

function post_survey() {
	$('#post-q').css("display", "none");
	$('#turk-post').css("display", "block");
}

function next_pattern() {
	myVid.pause();
	$("#pieChartdiv").show();
	$(".individual-survey").show();
	$(".individual-survey").html("<div class = 'individual-holder'>Please click on each <b>time instance</b> above to answer a question. You can proceed to the next step when you are done.</div>");
	clickedallflag = false;
    
	console.log(current);
    if(current < numofPatterns)
    {
        if(current == (numofPatterns-1))
        {
			$("#next").text('Complete Survey');
        }

        $('#next').addClass('disabled');
		$('#surveyq').css("display", "none");
        $('#p'+current).css("display", "none");
        current++;
        zoomToIndexes(chart, current, current);
        $('#p'+current).css("display", "block");
		
		piechartDataProvider[current].color = chartData[current].segments[0].color;
		piechart.validateData();
		
    }else{
		$("#next").attr('type', 'submit');
		$.ajax({
			type: 'POST',
			data: {chartData: chartData, id: folder_dir, datakey:datakey },
			dataType: 'json',
			url: 'db.php',
		});
			
		$('#in-q').css("display", "none");
        //$('#post-q').css("display", "block");
        $("#topContainer").css("display", "none");
    }
}

$('input[type=radio]').change( function() {
    //alert($("input[name='entry.298715203']:checked").val());
    if($("input[name='entry.298715203']:checked").val() != undefined && $("input[name='entry.402079925']:checked").val() != undefined && $("input[name='entry.1350142475']:checked").val() != undefined && $("input[name='entry.444518839']:checked").val() != undefined && $("input[name='entry.1973339660']:checked").val() != undefined && $("input[name='entry.2021115824']:checked").val() != undefined && $("input[name='entry.543518954']:checked").val() != undefined && $("input[name='entry.122496811']:checked").val() != undefined && $("input[name='entry.951552620']:checked").val() != undefined)
    {
        $('#complete-1').removeClass('disabled');
    }
	
    if(current == 0)
    {
       if($("input[name='entry.1904638195']:checked").val() != undefined)
       {
            $('#next').removeClass('disabled');

       }
    }else if (current == 1){
       if($("input[name='entry.1346396188']:checked").val() != undefined)
       {

            $('#next').removeClass('disabled');

       }

    }else if (current == 2){
       if($("input[name='entry.1686120955']:checked").val() != undefined)
       {
            $('#next').removeClass('disabled');
       }
    }else if (current == 3){
       if($("input[name='entry.25292253']:checked").val() != undefined)
       {

            $('#next').removeClass('disabled');

       }

    }else if (current == 4){
       if($("input[name='entry.1381118731']:checked").val() != undefined)
       {
            $('#next').removeClass('disabled');

       }
    }

    /*if($("input[name='entry.1973339660']:checked").val() != undefined && $("input[name='entry.2021115824']:checked").val() != undefined && $("input[name='entry.543518954']:checked").val() != undefined && $("input[name='entry.840577731']:checked").val() != undefined)
    {
        $('#complete').removeClass('disabled');
    }*/


});

function clearAllTimeout(timeouts)
{
    for (var i=0; i<timeouts.length; i++) {
        clearTimeout(timeouts[i]);
    }
}

function clearAllInterval(intervals)
{
    for (var i=0; i<intervals.length; i++) {
        clearInterval(intervals[i]);
    }
}