	/*
		JAVASCRIPTS FILE
	*/
	var ga=new Array();
	function goView(id){
		document.getElementById("loading").style.display="block";
		document.getElementById("buttonBack").style.display="block";
		document.getElementById("mainStatus").style.display="none";
		var Output=document.getElementById("output");
		//Output.style.left="0";
		Output.style.right="20px";
		Output.style.top="60px";
		//Output.style.bottom="0";
		Output.style.width="calc(100vw - 20px)";
		Output.style.height="calc(100vh - 60px)";
		Output.style.display="block";
		getApi("output","view","&v="+id);
		document.getElementById("loading").style.display="none";
	}	
	function getApi(id,action,values) { 
		if(!values) values=""; //&name=value&name=value
		if (window.XMLHttpRequest) { ga[id]=new XMLHttpRequest(); }
		else { ga[id]=new ActiveXObject("Microsoft.XMLHTTP"); }
		ga[id].onreadystatechange=function() {
			if (ga[id].readyState==4 && ga[id].status==200) {
				//document.getElementById(id).innerHTML=ga[id].responseText;
				var result=ga[id].responseText;		
				var values=JSON.parse(result);	
				if(!values.error){
					if(values.html) {
						document.getElementById(id).innerHTML=values.html;
					}
					if(values.cmd){
						for(var c=0;c<values.cmd.length;c++){
							console.log("Eval: "+values.cmd[c]);
							eval(values.cmd[c]);
						}
					}
					
				}
				else{
					document.getElementById(id).innerHTML=values.error;
				}	
				goGrabOutput();			
			}
		}
		ga[id].open("GET","api.php?a="+action+values+"&r="+Math.random(),true);
		ga[id].send();	
	}
	function setMaxsize(id){
		document.getElementById(id).style.width=screen.width+"px";
		document.getElementById(id).style.height=screen.height+"px";
		document.getElementById(id).style.maxWidth=screen.width+"px";
		document.getElementById(id).style.maxHeight=screen.height+"px";
	}	
	var ghs=new Array();
	function getHostState(host,id) { 
		 document.getElementById(id).setAttribute("class","fas fa-spinner grey rotating"); 	 
		if (window.XMLHttpRequest) { ghs[id]=new XMLHttpRequest(); }
		else { ghs[id]=new ActiveXObject("Microsoft.XMLHTTP"); }
		ghs[id].onreadystatechange=function() {
			if (ghs[id].readyState==4 && ghs[id].status==200) {
				if (ghs[id].responseText=="online") { document.getElementById(id).setAttribute("class","fas fa-check-circle green"); }
				else { document.getElementById(id).setAttribute("class","fas fa-times-circle red");  }
			}
		}
		ghs[id].open("GET","api.php?a=ping&h="+host+"&r="+Math.random(),true);
		ghs[id].send();	
	}	
	var gss=new Array();
	function getServerState(host,port,id) { 
		 document.getElementById(id).setAttribute("class","fas fa-spinner grey rotating"); 	 
		if (window.XMLHttpRequest) { gss[id]=new XMLHttpRequest(); }
		else { gss[id]=new ActiveXObject("Microsoft.XMLHTTP"); }
		gss[id].onreadystatechange=function() {
			if (gss[id].readyState==4 && gss[id].status==200) {
				if (gss[id].responseText=="online") { document.getElementById(id).setAttribute("class","fas fa-check-circle green"); }
				else { document.getElementById(id).setAttribute("class","fas fa-times-circle red");  }
			}
		}
		gss[id].open("GET","api.php?a=state&h="+host+"&p="+port+"&r="+Math.random(),true);
		gss[id].send();	
	}	
	function toHumanTime(secs) {
		var sec_num = parseInt(secs, 10); // don't forget the second param
		var hours   = Math.floor(sec_num / 3600);
		var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
		var seconds = sec_num - (hours * 3600) - (minutes * 60);

		if (hours   < 10) {hours   = "0"+hours;}
		if (minutes < 10) {minutes = "0"+minutes;}
		if (seconds < 10) {seconds = "0"+seconds;}
		return hours+':'+minutes+':'+seconds;
	}
	function countProperties(obj) {
		var count = 0;
		for(var prop in obj) {
			if(obj.hasOwnProperty(prop))
				++count;
		}
		return count;
	}
	function randomBall(){
		var ballArray = ['volleyball-ball','basketball-ball','baseball-ball','futbol',];
		var randomNumber = Math.floor(Math.random()*ballArray.length);
		return ballArray[randomNumber];
	}
	function goEmpty(){
		document.getElementById("buttonBack").style.display="none";
		var Output=document.getElementById("output");
		document.getElementById("mainStatus").style.display="block";
		/*
		//Output.style.left="0";
		Output.style.right="5vw";
		Output.style.top="38vh";
		//Output.style.bottom="0";
		Output.style.width="180px";
		Output.style.height="180px";
		var Ow=Output.getBoundingClientRect().width;
		var Oh=Output.getBoundingClientRect().height;
		
		//Output.innerHTML='<marquee direction="down" behavior="alternate" width='+Ow+' height='+Oh+' style="display:block;margin:0 -10px -10px 0;"><marquee behavior="alternate"><i class="fas fa-'+randomBall()+' myBall"></i></marquee></marquee><dl>';
		//Output.innerHTML='<div class="scene" style="max-height:'+Oh+'px; max-width:'+Ow+'px;"><div class="el-wrap x" style="max-height:'+Oh+'px; max-width:'+Ow+'px;"><div id="el1" class="el y"><div class="cube"><div class="side back"></div><div class="side left"></div><div class="side right"></div><div class="side top"></div><div class="side bottom"></div><div class="side front"></div></div></div></div></div>';
		
		//
		//document.documentElement.style.setProperty("--width", Ow+"px");
		document.documentElement.style.setProperty("--outputH", Oh+"px");
		document.documentElement.style.setProperty("--outputW", Ow+"px");
		*/
		Output.innerHTML="";
		Output.style.display="none";
		
	}


