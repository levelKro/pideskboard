<?php
Class ShoutCast{
	function __construct () {
		require_once("scxml-obj.php");
	}
	function infos($host,$port,$stream_id,$password){
		$serv1 = new SCXML;
		$serv1->set_host("$host");
		$serv1->set_port("$port");
		$serv1->set_password("$password");
		$serv1->set_streamid("$stream_id");
		if (!$serv1->retrieveXML()) return ("Can't retrieve XML");
		if (!$serv1->fetchMatchingTag("STREAMSTATUS") == "1") return ("No source on server");

		$trackpattern = "/^[0-9][0-9] /";
		$trackreplace = "";

	$con_time=$serv1->fetchMatchingArray("PLAYEDAT");
	if (preg_match ("/^[0-9]{10}$/", $con_time[0])) {
   		for ($i=0; $i<count($con_time); $i++) {
    		$con_time[$i] = $con_time[$i] + $adjust;
    		$con_time[$i] = date('H:i:s', $con_time[$i]);
		}
		$playtime = $con_time;
	}
	else {
		$playtime = $con_time;
	}
	if ($timeat == "0") {
		$playat = array_shift ($playtime);
	} 
	else {
		$playtime = $playtime;
	}
		
		
		
		$return=array(
			"url"=>"http://".$host.":".$port."/".$stream_id,
			"hostname"=>$serv1->fetchMatchingArray("HOSTNAME"),
			"listenNow"=>(($serv1->fetchMatchingTag("CURRENTLISTENERS")=="")?0:$serv1->fetchMatchingTag("CURRENTLISTENERS")),
			"listenPeak"=>$serv1->fetchMatchingTag("PEAKLISTENERS"),
			"listenMax"=>$serv1->fetchMatchingTag("MAXLISTENERS"),
			"listenTime"=>$serv1->fetchMatchingArray("CONNECTTIME"),
			"title"=>$serv1->fetchMatchingTag("SERVERTITLE"),
			"songTitle"=>preg_replace($trackpattern, $trackreplace, $serv1->fetchMatchingTag("SONGTITLE")),
			//"songLast"=>array("tracks"=>$serv1->fetchMatchingArray("TITLE"),"times"=>$playtime),
		);
		return $return;
	}

}

?>