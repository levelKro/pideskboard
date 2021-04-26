var radioPlayerID=document.getElementById("radioPlayer");
var checkLinks="";
function updateDatas(view) {  
	if (window.XMLHttpRequest) { updateDatasCall=new XMLHttpRequest(); }
	else { updateDatasCall=new ActiveXObject("Microsoft.XMLHTTP"); }
	updateDatasCall.onreadystatechange=function() {
		if (updateDatasCall.readyState==4 && updateDatasCall.status==200) {
			var result=updateDatasCall.responseText;		
			var values=JSON.parse(result);	
			
			if(!values.error){
				if(values.radio){
					radio=values.radio;
					//document.getElementById("lvk_listen_now").innerText=values.listenNow;	
					//document.getElementById("lvk_listen_max").innerText=values.listenMax;	
					//document.getElementById("lvk_listen_peak").innerText=values.listenPeak;	
					
					if(radio.title=="")
						document.getElementById("radioTitle").innerText="Internet Radio";
					else
						document.getElementById("radioTitle").innerText=radio.title;	
					if(radio.songTitle=="")
						document.getElementById("radioSong").innerText="~ no informations ~";
					else							
						document.getElementById("radioSong").innerText=radio.songTitle;	
				}	
				else{
					document.getElementById("output").innerText="Radio error";
				}
				if(values.weather){
					var weather=values.weather;
					document.getElementById("weatherTemp").innerHTML=weather.temp;
					document.getElementById("weatherFeel").innerHTML=weather.feel;
					if(weather.clouds) document.getElementById("weatherCloud").innerHTML='<i class="fas fa-cloud grey"></i> '+weather.clouds+'%';
					else document.getElementById("weatherCloud").innerHTML='<i class="fas fa-cloud grey"></i> 0%';
					document.getElementById("weatherTempMin").innerHTML='<i class="fas fa-temperature-low blue"></i> '+weather.min;
					document.getElementById("weatherTempMax").innerHTML='<i class="fas fa-temperature-high orange"></i> '+weather.max;
					document.getElementById("weatherRainSnow").innerHTML="";
					if(weather.snow) document.getElementById("weatherRainSnow").innerHTML+='<i class="fas fa-snowflake white"></i> '+weather.snow+'cm';
					if(weather.rain) document.getElementById("weatherRainSnow").innerHTML+='<i class="fas fa-cloud-rain blue"></i> '+weather.rain+'mm';
					document.getElementById("weatherDetails").innerHTML=weather.name;
					document.getElementById("weatherImage").innerHTML=weather.image;
				}	
				else{
					document.getElementById("output").innerText="Weather error";
				}
				if(values.mailbox){
					var mailbox=values.mailbox;
					document.getElementById("mailboxUnread").innerHTML='<i class="fas fa-envelope"></i> '+mailbox.unread;
					document.getElementById("mailboxRead").innerHTML='<i class="fas fa-envelope-open"></i> '+mailbox.read;
				}	
				else{
					document.getElementById("output").innerText="Mailbox error";
				}

				if(values.time){
					var mailbox=values.mailbox;
					document.getElementById("time").innerHTML=values.time;
				}	
				else{
					document.getElementById("output").innerText="Time error";
				}	
				if(values.date){
					var mailbox=values.mailbox;
					document.getElementById("date").innerHTML=values.date;
				}	
				else{
					document.getElementById("output").innerText="Date error";
				}	

				if(values.todo){
					var todo=values.todo;
					document.getElementById("todo").innerHTML="<h4>"+values.text_today+"</h4>";
					var output="<ul>";
					for (var i = 0; i < todo.length; i++) {
						output+="<li>"+todo[i]+"</li>";
					}
					document.getElementById("todo").innerHTML+=output+"</ul>";
				}
				if(values.links){
					var links=values.links;
					document.getElementById("links").innerHTML="";
					links.forEach(function(item) { document.getElementById("links").innerHTML+='<div class="link" onclick="goView(\''+item.id+'\');"><i class="fas fa-'+item.icon+'"></i><span class="text">'+item.name+'</span></div>'; });
				}
			}
			else{
				document.getElementById("output").innerText=values.error;
			}
		}
	}
	updateDatasCall.open("GET","api.php?a=datas&r="+Math.random(),true);
	updateDatasCall.send();	
}
function playerState(){
	var playerRadioPlay = document.getElementById('radioPlayerPlay');
	var playerRadioPause = document.getElementById('radioPlayerPause');
	if(radioPlayerID.paused){
		playerRadioPause.style.display="none";
		playerRadioPlay.style.display="inline-block";
	}
	else{
		playerRadioPlay.style.display="none";
		playerRadioPause.style.display="inline-block";
	}
	return radioPlayerID.paused;
}
/* Adding support of scrolling for few boxes */
document.addEventListener('DOMContentLoaded', function(){
	var playerRadioPlay = document.getElementById('radioPlayerPlay');
	var playerRadioPause = document.getElementById('radioPlayerPause');
	playerRadioPlay.addEventListener('click', function() {
		radioPlayerID.load();
		radioPlayerID.play();
		playerState();
	});
	playerRadioPause.addEventListener('click', function() {
		radioPlayerID.pause();
		playerState();
	});
	radioPlayerID.addEventListener('play', function() {
		playerState();
	});
	radioPlayerID.addEventListener('pause', function() {
		playerState();
	});
	radioPlayerID.addEventListener('ended', function() {
		playerState();
	});
	radioPlayerID.addEventListener('timeupdate', function() {
		document.getElementById("radioTime").innerText=toHumanTime(radioPlayerID.currentTime);
	});	
});
function goRadio(){
	if(radioPlayerID.paused){
		radioPlayerID.load();
		radioPlayerID.play();
		playerState();
	}
	else{
		radioPlayerID.pause();
		playerState();
	}
}
function goGrabLinks(s) {		
	const sliderLinks = document.querySelector(".links");
	if(sliderLinks!=null) {			
		let isDownLinks = false;
		let startXLinks;
		let startYLinks;
		let scrollLeftLinks;
		let scrollTopLinks;		
		sliderLinks.addEventListener("mousedown", e => {
			isDownLinks = true;
			sliderLinks.classList.add("active");
			startXLinks = e.pageX - sliderLinks.offsetLeft;
			startYLinks = e.pageY - sliderLinks.offsetTop;
			scrollLeftLinks = sliderLinks.scrollLeft;
			scrollTopLinks = sliderLinks.scrollTop;
		});
		sliderLinks.addEventListener("mouseleave", () => {
			isDownLinks = false;
			sliderLinks.classList.remove("active");
		});
		sliderLinks.addEventListener("mouseup", () => {
			isDownLinks = false;
			sliderLinks.classList.remove("active");
		});
		sliderLinks.addEventListener("mousemove", e => {
			if (!isDownLinks) return;
			e.preventDefault();
			const xLinks = e.pageX - sliderLinks.offsetLeft;
			const yLinks = e.pageY - sliderLinks.offsetTop;
			const walkXLinks = xLinks - startXLinks;
			const walkYLinks = yLinks - startYLinks;
			sliderLinks.scrollLeft = scrollLeftLinks - walkXLinks;
			sliderLinks.scrollTop = scrollTopLinks - walkYLinks;
		});
	}
	else {
		checkLinks=setTimeout("goGrabLinks();",500);
	}				
}
var checkToday="";
function goGrabToday() {		
	const sliderToday = document.querySelector(".today");
	if(sliderToday!=null) {			
		let isDownToday = false;
		let startXToday;
		let startYToday;
		let scrollLeftToday;
		let scrollTopToday;		
		sliderToday.addEventListener("mousedown", e => {
			isDownToday = true;
			sliderToday.classList.add("active");
			startXToday = e.pageX - sliderToday.offsetLeft;
			startYToday = e.pageY - sliderToday.offsetTop;
			scrollLeftToday = sliderToday.scrollLeft;
			scrollTopToday = sliderToday.scrollTop;
		});
		sliderToday.addEventListener("mouseleave", () => {
			isDownToday = false;
			sliderToday.classList.remove("active");
		});
		sliderToday.addEventListener("mouseup", () => {
			isDownToday = false;
			sliderToday.classList.remove("active");
		});
		sliderToday.addEventListener("mousemove", e => {
			if (!isDownToday) return;
			e.preventDefault();
			const xToday = e.pageX - sliderToday.offsetLeft;
			const yToday = e.pageY - sliderToday.offsetTop;
			const walkXToday = xToday - startXToday;
			const walkYToday = yToday - startYToday;
			sliderToday.scrollLeft = scrollLeftToday - walkXToday;
			sliderToday.scrollTop = scrollTopToday - walkYToday;
		});
	}
	else {
		checkToday=setTimeout("goGrabToday();",500);
	}				
}
var checkOutput="";
function goGrabOutput() {		
	const sliderOutput = document.querySelector(".output");
	if(sliderOutput!=null) {			
		let isDownOutput = false;
		let startXOutput;
		let startYOutput;
		let scrollLeftOutput;
		let scrollTopOutput;		
		sliderOutput.addEventListener("mousedown", e => {
			isDownOutput = true;
			sliderOutput.classList.add("active");
			startXOutput = e.pageX - sliderOutput.offsetLeft;
			startYOutput = e.pageY - sliderOutput.offsetTop;
			scrollLeftOutput = sliderOutput.scrollLeft;
			scrollTopOutput = sliderOutput.scrollTop;
		});
		sliderOutput.addEventListener("mouseleave", () => {
			isDownOutput = false;
			sliderOutput.classList.remove("active");
		});
		sliderOutput.addEventListener("mouseup", () => {
			isDownOutput = false;
			sliderOutput.classList.remove("active");
		});
		sliderOutput.addEventListener("mousemove", e => {
			if (!isDownOutput) return;
			e.preventDefault();
			const xOutput = e.pageX - sliderOutput.offsetLeft;
			const yOutput = e.pageY - sliderOutput.offsetTop;
			const walkXOutput = xOutput - startXOutput;
			const walkYOutput = yOutput - startYOutput;
			sliderOutput.scrollLeft = scrollLeftOutput - walkXOutput;
			sliderOutput.scrollTop = scrollTopOutput - walkYOutput;
		});
	}
	else {
		checkOutput=setTimeout("goGrabOutput();",500);
	}				
}
/* Startup scripts */
updateDatas();
var updatesDatasInterval=setInterval("updateDatas();",5000);
goEmpty();
goGrabOutput(".output");
goGrabLinks(".menu");
goGrabToday(".frameTodo");
