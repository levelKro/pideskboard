<?php
	// CRON File
	error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING & ~E_STRICT & ~E_DEPRECATED);
	ini_set("display_errors", true);
	date_default_timezone_set("America/Montreal");
	setlocale(LC_MONETARY, 'en_US');
	ini_set('ignore_repeated_errors', TRUE); // always use TRUE
	ini_set('log_errors', TRUE); // Error/Exception file logging engine.
	ini_set('error_log', '/home/pi/pideskboard/php/error.log'); // Logging file path	
	require("/home/pi/pideskboard/configs/config.php");
	require_once("sys/libs.php");

	$sync=array(
		"weather"	=>	array(	"limit"	=>	900,	"now"	=>	0),
		"mailbox"	=>	array(	"limit"	=>	300,	"now"	=>	0),
		"radio"		=>	array(	"limit"	=>	60,		"now"	=>	0),
		"config"	=>	array(	"limit"	=>	60,		"now"	=>	0)
	);
start:
	
	switch($cfg['system']['units']){
		case 'imperial':
		case 'IMPERIAL':
			$units=array(
				"name"=>"imperial",
				"winds"=>"mph",
				"rain"=>"mm",
				"snow"=>"cm",
				"temp"=>"°F"
			);
		
		break;
		case 'metric':
		case 'METRIC':
		default:
			$units=array(
				"name"=>"metric",
				"winds"=>"m/h",
				"rain"=>"mm",
				"snow"=>"cm",
				"temp"=>"°C"
			);
	}
	
	// Reload config
	if((time()-$sync['config']['now']) >= $sync['config']['limit']) {
		$sync['config']['now']=time();
		$cfg=readConfig(); // Reload config
		if(!$cfg) die("Can't load config , can't find in ".dirname(__FILE__));
		else $GLOBALS=$cfg;
	}
	
	// Auto-reboot
	if($cfg['system']['reboot']=="true" || $cfg['system']['reboot']=="True"){
		if(date("G:i",time())==$cfg['system']['reboot_time'] && (date("N",time())==$cfg['system']['reboot_day'] || $cfg['system']['reboot_day']=="0")){
			if($cfg['system']['icon']) system($cfg['icon']['path'].' 15000 '.$cfg['icon']['reboot'].' 3');
			if($cfg['system']['espeak']) speak(translateText("REBOOT"),$cfg['espeak']['module']);
			sleep(15);			
			system($cfg['cli']['reboot']." &");
			sleep(120);	 // wait 2 mins, prevent restart of script process if killed.
			die();
		}
	}
	
	// Time notice
	if(DBRamRead("time_ding")!=date("H",time()) && date("i",time())=="00"){
		
		switch(date("G",time())){
			case '0':
			case '00':
				if($cfg['system']['espeak']) speak(translateText("TIME_MIDNIGHT"),$cfg['espeak']['module']);
			break;
			case '1':
				if($cfg['system']['espeak']) speak(translateText("TIME_ONEHOUR"),$cfg['espeak']['module']);
			break;
			case '12':
				if($cfg['system']['espeak']) speak(translateText("TIME_DINER"),$cfg['espeak']['module']);
			break;
			default:
				if($cfg['system']['espeak']) speak(str_replace("%HOUR%",date("G",time()),translateText("TIME_CURRENT")),$cfg['espeak']['module']);
		}
	}
	DBRamSave("time_ding",date("H",time()));	
	
	// Date change & notice
	if(DBRamRead("date_ding")!=date("l, j F, Y",time()) && date("H:i",time())=="00:00"){
		if($cfg['system']['espeak']) speak(translateText("TIME_YOUARENOW")." ".translateDate(date("l, j F, Y",time())).".",$cfg['espeak']['module']);
		jsonSave("date",array("today"=>translateDate(date("l, j F, Y",time())),"today_text"=>translateText("TODAY")));
	}
	elseif(!file_exists($cfg['system']['cache']."date.json")) {
		jsonSave("date",array("today"=>translateDate(date("l, j F, Y",time())),"today_text"=>translateText("TODAY")));
	}
	DBRamSave("date_ding",date("l, j F, Y",time()));		


	// TODO Today
	$todo=array();
	$today=array(
		"day"=>date("j",time()), // date
		"day_pos"=>date("w",time()), // position in week
		"day_num"=>date("z",time()), // position in the year
		"week"=>date("W",time()), // position of the week
		"month"=>date("n",time()), // month
		"month_day"=>date("t",time()), // total day in the month
		"year"=>date("Y",time()), // year
		"unix"=>time()
	);	
	$fileday=$GLOBALS['system']['config']."calendar/".$today['month']."-".$today['day']."-".$today['year'].".txt";
	if(file_exists($fileday)){
		if($file=fopen($fileday,"r")){
			while(!feof($file)) {
				$line = fgets($file);
				if($line!="") $todo[]=$line;
			}
			fclose($file);
		}				
	}
	$fileday=$GLOBALS['system']['config']."calendar/".$today['month']."-".$today['day'].".txt";
	if(file_exists($fileday)){
		if($file=fopen($fileday,"r")){
			while(!feof($file)) {
				$line = fgets($file);
				if($line!="") $todo[]=$line;
			}
			fclose($file);
		}				
	}	
	if(count($todo)<=0) $todo[]=translateText("NOTHING");
	jsonSave("todo",$todo);
	
	// WEATHER
	$weather=DBRead("weather");
	if((time()-$sync['weather']['now']) >= $sync['weather']['limit'] && $weather) {
		$sync['weather']['now']=time();
		if($cfg['system']['icon']) system($cfg['icon']['path'].' 3000 '.$cfg['icon']['remote']);
		$jsonurl = "http://api.openweathermap.org/data/2.5/weather?q=".$weather['city']."&appid=".$weather['api']."&lang=".$cfg['system']['language']."&units=".$units['name'];
		$json = file_get_contents($jsonurl);
		$weather['remote'] = json_decode($json);
		$return['temp'] = round($weather['remote']->main->temp,0).$units['temp'];
		$return['feel'] = round($weather['remote']->main->feels_like,0).$units['temp'];
		$return['min'] = round($weather['remote']->main->temp_min,0).$units['temp'];
		$return['max'] = round($weather['remote']->main->temp_max,0).$units['temp'];
		$return['name'] = $weather['remote']->weather[0]->description;
		$return['ico'] = "http://openweathermap.org/img/wn/".$weather['remote']->weather[0]->icon."@2x.png";
		if(is_object($weather['remote']->snow)){
			$snow=(array) $weather['remote']->snow;
			if(is_numeric($snow["1h"])) $return['snow']=round($snow["1h"],1).$units['snow'];
		}
		if(is_object($weather['remote']->rain)){
			$rain=(array) $weather['remote']->rain;
			if(is_numeric($rain["1h"])) $return['rain']=round($rain["1h"],1).$units['rain'];			
		}
		if(is_object($weather['remote']->clouds)){
			$clouds=(array) $weather['remote']->clouds;
			if(is_numeric($clouds["all"])) $return['clouds']=$clouds["all"]."%";
		}
		jsonSave("weather",$return);
		unset($output);	
		// Extended informations
		$jsonurl = "http://api.openweathermap.org/data/2.5/forecast?q=".$weather['city']."&appid=".$weather['api']."&lang=".$cfg['language']."&units=".$units['name'];
		$json = file_get_contents($jsonurl);
		$weather['remote'] = (array) json_decode($json);
		$list=$weather['remote']['list'];
		$i=0;
		$today=date("j",time());
		$output['next']=array();
		foreach($list as $item){
			$item = (array) $item;
			if(is_object($item["snow"])) {
				$item["snow"]=(array) $item["snow"];
			}
			if(is_object($item["rain"])) {
				$item["rain"]=(array) $item["rain"];
			}
			$day=date("j",$item["dt"]);
			if($i<=4){
				$output['today'][]=array(
					"date"=>$item["dt"],
					"hour"=>date("H",$item['dt']),
					"code"=>$item["weather"][0]->id,
					"ico"=>"http://openweathermap.org/img/wn/".$item["weather"][0]->icon."@2x.png",
					"temp"=>round($item["main"]->temp,1).$units['temp'],
					"feel"=>round($item["main"]->feels_like,1).$units['temp'],
					"min"=>round($item["main"]->temp_min,0).$units['temp'],
					"max"=>round($item["main"]->temp_max,0).$units['temp'],
					"humidity"=>$item["main"]->humidity.'%',
					"clouds"=>$item["clouds"]->all.'%',
					"winds"=>$item["wind"]->speed.$units['winds'],
					"details"=>$item["weather"][0]->description,
					"snow"=>(($item["snow"])?$item["snow"]["3h"].$units['snow']:''),
					"rain"=>(($item["rain"])?$item["rain"]["3h"].$units['rain']:'')
				);
				$i++;
			}
			if($day!=$today){
				$output['next'][$day]['day']=$day;
				$output['next'][$day]['date']=$item["dt"];
				$output['next'][$day]['text_day']=translateDate(date("l",$item['dt']));
				$output['next'][$day]['text_month']=translateDate(date("F",$item['dt']));
				if($item["main"]->temp_min<$output['next'][$day]['min'] || $output['next'][$day]['min']=="") $output['next'][$day]['min']=round($item["main"]->temp_min,1).$units['temp'];
				if($item["main"]->temp_max>$output['next'][$day]['max'] || $output['next'][$day]['max']=="") $output['next'][$day]['max']=round($item["main"]->temp_max,1).$units['temp'];
				if($item["snow"]["3h"]>0) $output['next'][$day]['snow']=($output['next'][$day]['snow']+($item["snow"]["3h"]));
				if($item["rain"]["3h"]>0) $output['next'][$day]['rain']=($output['next'][$day]['rain']+($item["rain"]["3h"]));
				
			}
		}
		$lines=array();
		foreach($output['next'] as $line){
			$lines[]=$line;
		}
		$output['next']=$lines;
		foreach($output['next'] as $x=>$values){
			$output['next'][$x]['snow']=(($output['next'][$x]['snow'])?$output['next'][$x]['snow'].$units['snow']:"");
			$output['next'][$x]['rain']=(($output['next'][$x]['rain'])?$output['next'][$x]['rain'].$units['rain']:"");
		}
		jsonSave("forecast",$output);
	}
	unset($return);
	
	// MAILBOX
	$mailbox=DBRead("mail");
	if((time()-$sync['mailbox']['now']) >= $sync['mailbox']['limit'] && $mailbox) {
		$sync['mailbox']['now']=time();
		if($cfg['system']['icon']) system($cfg['icon']['path'].' 3000 '.$cfg['icon']['remote']);
		$mbox = imap_open('{'.$mailbox['host'].':'.$mailbox['port'].'/imap/ssl/novalidate-cert}INBOX', $mailbox['user'], $mailbox['pass']);
		if(empty($mbox)) {
			die(json_encode(array("error"=>imap_last_error()),true));
		}
		else {
			$output=array();
			$unread=imap_search($mbox, 'UNSEEN');
			if(empty($unread)) $output["unread"]=0;
			else $output["unread"]=count($unread);
			if($mail = imap_check($mbox)) $output["total"]=$mail->Nmsgs;
			else $output["total"]=0;
			$output["read"]=($output["total"]-$output["unread"]);
			if($output['total']==0) {
				$return=array("total"=>0,"unread"=>0,"read"=>0,"latest"=>array());
			}
			else{
				$return=$output;
				if($output['unread']>0){
					// speech
					if(DBRamRead("newmail")!==false && is_numeric(DBRamRead("newmail"))) $old=DBRamRead("newmail");
					else $old=0;
					if($old<$output['unread']) if($cfg['system']['espeak']) speak(str_replace("%UNREAD%",($output['unread']-$old),translateText("MAIL_YOUHAVEXNEW")),$cfg['espeak']['module']);
				}
			}
			DBRamSave("newmail",$output['unread']);				
		}
		imap_close($mbox);	
		jsonSave("mailbox",$return);	
	}
	unset($return);
	
	// RADIO
	$radio=DBRead("radio");
	if((time()-$sync['radio']['now']) >= $sync['radio']['limit'] && $radio) {
		$sync['radio']['now']=time();
		if($cfg['system']['icon']) system($cfg['icon']['path'].' 3000 '.$cfg['icon']['remote']);
		require_once($GLOBALS['root']."sys/sc/shoutcast.php");	
		$sc=New ShoutCast();
		$host=$radio['host'];
		$port=$radio['port'];
		$id=$radio['id'];
		if($id<1 || !is_numeric($id)) $id=1;
		if($port<1 || $port>65535 || !is_numeric($port)) $port=8000;
		if(!empty($host)) {
			jsonSave("radio",$sc->infos($host,$port,$id,$radio['pass']));		
		}
	}
	unset($return);
	
	sleep(5);
	goto start;
	
	