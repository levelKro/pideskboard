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
	
	// Reload config
	if((time()-$sync['config']['now']) >= $sync['config']['limit']) {
		$sync['config']['now']=time();
		$cfg=readConfig(); // Reload config
		if(!$cfg) die("Can't load config , can't find in ".dirname(__FILE__));
		else $GLOBALS=$cfg;
	}
	
	// Auto-reboot
	if($cfg['system']['reboot']!==false){
		if(date("G:i",time())==$cfg['system']['reboot']){
			if($cfg['system']['icon']) system($cfg['icon']['path'].' 15000 '.$cfg['icon']['reboot'].' 3');
			if($cfg['system']['espeak']) speak(translateText("REBOOT"),$cfg['espeak']['module']);
			sleep(15);			
			system($cfg['cli']['reboot']." &");
			sleep(120);	 // wait 2 mins, prevent retsart of script process if killed.
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
		jsonSave("date",array("today"=>translateDate(date("l, j F, Y",time()))));
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
		$jsonurl = "http://api.openweathermap.org/data/2.5/weather?q=".$weather['city']."&appid=".$weather['api']."&lang=".$cfg['system']['language']."&units=metric";
		$json = file_get_contents($jsonurl);
		$weather['remote'] = json_decode($json);
		$return['temp'] = round($weather['remote']->main->temp,0)."°C";
		$return['feel'] = round($weather['remote']->main->feels_like,0)."°C";
		$return['min'] = round($weather['remote']->main->temp_min,0)."°C";
		$return['max'] = round($weather['remote']->main->temp_max,0)."°C";
		$return['name'] = $weather['remote']->weather[0]->description;
		$return['ico'] = "http://openweathermap.org/img/wn/".$weather['remote']->weather[0]->icon."@2x.png";
		if(is_object($weather['remote']->snow)){
			$snow=(array) $weather['remote']->snow;
			if(is_numeric($snow["1h"])) $return['snow']=round($snow["1h"],1)."mm";
		}
		if(is_object($weather['remote']->rain)){
			$rain=(array) $weather['remote']->rain;
			if(is_numeric($rain["1h"])) $return['rain']=round($rain["1h"],1)."mm";			
		}
		if(is_object($weather['remote']->clouds)){
			$clouds=(array) $weather['remote']->clouds;
			if(is_numeric($clouds["all"])) $return['clouds']=$clouds["all"]."%";
		}
		$return['image']='<i class="fas fa-'.getWeatherIcon($weather['remote']->weather[0]->id).' '.getWeatherColor($weather['remote']->weather[0]->id).'"></i>';	
		jsonSave("weather",$return);
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
	
	