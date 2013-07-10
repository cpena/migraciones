var map;
var seconds;
var timer;

(function($) { 
	function createMap(){
		var myLatLng = new google.maps.LatLng(-35.675147,-71.542969); //chile
		var mapOptions = {
			zoom: 4,
			center: myLatLng,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};

		map = new google.maps.Map($('#map-canvas')[0], mapOptions);		
	}
	
	function getData(rows){
		seconds = 0;
		
		$("#running").show();
		$("#running").text("Processing");
		timer = setInterval(function(){
			seconds+= 0.1;
			$("#running").text("Processing "+seconds.toFixed(1)+"s");
		},100);
		
		$.getJSON("?q=data",{rows:rows},
		function(data){
			console.log(data);
			clearInterval(timer);
			if(data.error){
				$("#running").text(data.error);
			}
			else{
				var min,max;
		        $.each(data.rows, function(i, item) {
					if(i==0){
						max = item.f[4].v;
						min = data.rows[data.rows.length-1].f[4].v;
					}		
					var lineCoordinates = [
					    new google.maps.LatLng(item.f[0].v,item.f[1].v),
					    new google.maps.LatLng(item.f[2].v, item.f[3].v)
					  ];

					var lineSymbol = {
					    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
					};

					var line = new google.maps.Polyline({
					    path: lineCoordinates,
					    strokeColor: "#CC33FF",
					    strokeOpacity:(7*(item.f[4].v - min)/(max - min)+3)/10, //normalizado a [0.3,1]
					    icons: [{
					      icon: lineSymbol,
					      offset: '100%'
					    }],
					    map: map
					});
		        });
				$("#running").hide();
			}	
		});
	}
	
	createMap();
	getData(100);
})(jQuery);