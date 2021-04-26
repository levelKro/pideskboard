<?php
	// API FILE
	error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING & ~E_STRICT & ~E_DEPRECATED);
	ini_set("display_errors", 1);
	date_default_timezone_set("America/Montreal");
	setlocale(LC_MONETARY, 'en_US');
	ini_set('max_execution_time', '300');
	ini_set('ignore_repeated_errors', TRUE); // always use TRUE
	ini_set('log_errors', TRUE); // Error/Exception file logging engine.
	ini_set('error_log', '/home/pi/pideskboard/php/error.log');	
	set_time_limit(300);
	require_once("../configs/config.php");
	require_once("../php/sys/libs.php");

	switch($_GET['a']){
		case 'speak':
			// Save speak text for the CLI
			// BG
			if($cfg['enable']['icons']) system($cfg['icon_script'].' 1000 '.$cfg['icon']['save'].' 1');
			if($_GET['m']) {
				$m=strip_tags(html_entity_decode($_GET['m']));
				if($cfg['enable']['speak']) speak($m,$cfg['speak_module']);	
			}
			exit;
		break;
		case "ping":
			// Ping a host
			// BG
			echo remotePing($_GET['h']);
			exit;
		break;
		case "state":
			// Check port on a host
			// BG
			echo remoteState($_GET['h'],$_GET['p']);
			exit;
		break;
		case "refresh":
			// Request a refresh page
			// BG
			echo json_encode(array("html"=>translateText("CTRL_REFRESH"),"cmd"=>array("document.location.reload();")),true);
		break;
		case "bluetooth":
			// Request a BT reconnection
			// BG
			echo json_encode(array("html"=>translateText("CTRL_BLUETOOTH")),true);
			system('sudo /home/pi/pideskboard/sh/cli_bt.sh &');
		break;
		case "poweroff":
			// Request a power off
			// BG
			if($cfg['enable']['icons']) system($cfg['icon_script'].' 15000 '.$cfg['icon']['poweroff'].' 3');
			if($cfg['enable']['speak']) speak(translateText("POWEROFF"),$cfg['speak_module']);
			echo json_encode(array("html"=>translateText("CTRL_POWEROFF")),true);
			sleep(15);
			system('sudo /sbin/shutdown -P now &');
		break;
		case "reboot":
			// Request a reboot
			// BG
			if($cfg['enable']['icons']) system($cfg['icon_script'].' 15000 '.$cfg['icon']['reboot'].' 3');
			if($cfg['enable']['speak']) speak(translateText("REBOOT"),$cfg['speak_module']);
			echo json_encode(array("html"=>translateText("CTRL_REBOOT")),true);
			sleep(15);			
			system('sudo /sbin/shutdown -r now &');
		break;
		case 'datas':
			// Output background jobs synchronised
			// BG
			$links=array();
			foreach($cfg['links'] as $id=>$item){
				if(!empty($item["file"]) && filesize($GLOBALS['root']."configs/".$item["file"])==0) $ok=false;
				else $ok=true;
				if($ok==true) $links[]=array("id"=>$id,"name"=>$item['name'],"icon"=>$item['icon']);
			}	
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
			$fileday=$GLOBALS['root']."configs/calendar/".$today['month']."-".$today['day']."-".$today['year'].".txt";
			if(file_exists($fileday)){
				if($file=fopen($fileday,"r")){
					while(!feof($file)) {
						$line = fgets($file);
						if($line!="") $todo[]=$line;
					}
					fclose($file);
				}				
			}
			$fileday=$GLOBALS['root']."configs/calendar/".$today['month']."-".$today['day'].".txt";
			if(file_exists($fileday)){
				if($file=fopen($fileday,"r")){
					while(!feof($file)) {
						$line = fgets($file);
						if($line!="") $todo[]=$line;
					}
					fclose($file);
				}				
			}	
			if(count($todo)<=0) $todo[]="<i>".translateText("NOTHING")."</i>";			
			echo json_encode(array(
				"time"=>date("H:i",time()),
				"date"=>translateDate(date("l, j F, Y",time())),
				"weather"=>jsonRead("weather"),
				"mailbox"=>jsonRead("mailbox"),
				"radio"=>jsonRead("radio"),
				"todo"=>$todo,
				"links"=>$links,
				"text_today"=>translateText("TODAY")
			));
		break;
		case 'view':
			// Output view
			$output=array("html"=>'');
			if($_GET['v'] || $_GET['v']==0){
				if($_GET['v']>=0 && is_array($cfg['links'][$_GET['v']])) { $view=$cfg['links'][$_GET['v']]; }
				elseif(!is_numeric($_GET['v']) && is_array($cfg[$_GET['v']])) {$view=$cfg[$_GET['v']]; $view['module']=$_GET['v']; }
				else die(json_encode(array("error"=>$output['html'].translateText("ERROR_MODULE_NOTVALID")),true));
				switch($view['module']){
					case 'image':
						// SUB PAGE : image / camera ip
						#if($cfg['enable']['speak']) speak($view['name'],$cfg['speak_module']);
						$output['html'].='<div style="text-align:center;" class="showImage"><img src="'.$view['url'].'"/></div>';
					break;
					case 'list':
						// SUB PAGE : list
						if($cfg['enable']['speak']) speak($view['name'],$cfg['speak_module']);
						if ($file = fopen($GLOBALS['root']."configs/".$view["file"], "r")) {
							$output['html'].='<ul>';
							$i=0;
							while(!feof($file)) {
								$line = fgets($file);
								$output['html'].='<li>'.$line.'</li>';
								$i++;
							}
							if($i==0 || ($i==1 && empty($line))) {
								$output['html'].='<li><i>'.translateText("NODATA").'</i></li>'; 
							}
							fclose($file);
							$output['html'].='</ul>';
						}
						else { 
							$output['html'].='<p class="Message"><center><i>'.translateText("NODATA").'</i></center></p>'; 
						}					
					break;
					case 'servers':
						// SUB PAGE : server status
						#if($cfg['enable']['speak']) speak($view['name'],$cfg['speak_module']);	
						$list=DBReadAll("servers");
						if(!$list) die(json_encode(array("error"=>$output['html'].translateText("ERROR_MODULE_DISABLED")),true));
						ksort($list);
						$i=0;
						$scan=array();
						$output['html'].='<dl class="servers">';
						foreach($list as $item){
							$output['html'].='<dt>'.$item['name'].'<small class="serverIp">'.$item['ip'].'</small></dt><dd>';
							$item['services']=explode(",",$item['services']);
							foreach($item['services'] as $raw){
								if(count(explode(":",$raw))==2){ 
									$t=explode(":",$raw);
									$n=$t[0];						
									$p=$t[1];
								}
								else{
									$n=$raw;
									$p=getServicePort($raw);
								}
								$scan[]=array("name"=>"srv".$i,"ip"=>$item['ip'],"port"=>$p);
								$output['html'].='<span class="state"><i class="fas fa-spinner grey rotating" id="srv'.$i.'"></i> '.$n.' </span> ';
								$i++;
							}
							$output['html'].='</dd>';
						}
						$output['html'].='</dl>';	
						$output['cmd']=array();
						foreach($scan as $item) $output['cmd'][]='getServerState("'.$item['ip'].'","'.$item['port'].'","'.$item['name'].'"); '; 
					break;
					case 'network':
						// SUB PAGE : network local
						#if($cfg['enable']['speak']) speak($view['name'],$cfg['speak_module']);
						$list=DBReadAll("network");
						if(!$list) die(json_encode(array("error"=>$output['html'].translateText("ERROR_MODULE_DISABLED")),true));
						ksort($list);
						$i=0;
						$scan=array();
						$s=false;
						$output['html'].='<table class="network">';
						foreach($list as $item){
							$i++;
							$clean=false;
							if($s==false) { $output['html'].='<tr>'; }
							$output['html'].='<th style="width:30%; vertical-align:top;">'.$item['name'].'<small class="networkNote">'.$item['note'].'</small></th>';
							$output['html'].='<td style="text-align:left; vertical-align:top; width:20%; white-space:nowrap;">';
							$output['html'].=((!empty($item['ip1']))?'<div class="state"><i class="fas fa-spinner grey rotating" id="ip1-'.$i.'"></i> '.$item['ip1'].'</div>':'');
							$output['html'].=((!empty($item['ip2']))?'<div class="state"><i class="fas fa-spinner grey rotating" id="ip2-'.$i.'"></i> '.$item['ip2'].'</div>':'').'</td>';
							if($s==false) { $s=true; }
							else { 
								$output['html'].='</tr><tr><td colspan=4 class="hr"></td></tr>';	
								$s=false; 
								$clean=true;
							}
							if(!empty($item['ip1'])) $scan[]=array("name"=>"ip1-".$i,"ip"=>$item['ip1']);
							if(!empty($item['ip2'])) $scan[]=array("name"=>"ip2-".$i,"ip"=>$item['ip2']);
						}
						if(!$clean)	$output['html'].='</tr><tr><td colspan=4 class="hr"></td></tr>';
						$output['html'].='</table>';
						$output['cmd']=array();
						foreach($scan as $item) $output['cmd'][]='getHostState("'.$item['ip'].'","'.$item['name'].'");';
					break;
					case 'calendar':
						// SUB PAGE : calendar
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
						$gm=null;
						$gy=null;
						if(isset($_GET['m'])) $gm=$_GET['m'];
						if($gm>=1 && $gm<=12) $m=$gm;
						else $m=$today['month'];
						if(isset($_GET['y'])) $gy=$_GET['y'];
						if($gy>=1 && $gy<=12) $y=$gy;
						else $y=$today['year'];
						if(($m-1)<=0) { $yp=($y-1); $mp=12; }
						else { $yp=$y; $mp=($m-1); }
						if(($m+1)>=13) { $yn=($y+1); $mn=1; }
						else { $yn=$y; $mn=($m+1); }
						$work=array(
							"month"=>$m,
							"year"=>$y,
							"unix"=>strtotime($m.'/13/'.$y),
							"total"=>date("t",strtotime($m.'/13/'.$y)),
							"days"=>array()
						);
						#if($cfg['enable']['speak']) speak(translateDate(date("F",$work['unix']))." ".$work['year'],$cfg['speak_module']);
						for($i=1;$i<=$work['total'];$i++){
							$unix=strtotime($m.'/'.$i.'/'.$y);
							$work['days'][$i]=array(
								"unix"=>$unix,
								"day"=>date("j",$unix), // date
								"day_pos"=>date("w",$unix), // position in week
								"day_num"=>date("z",$unix), // position in the year
								"week"=>date("W",$unix), // position of the week
								"month"=>date("n",$unix), // month
								"month_day"=>date("t",$unix), // total day in the month
								"year"=>date("Y",$unix), // year
							);
						}						
						$output['html'].='<div class="calendarTitle">
							<a onclick="goView(\'calendar&y='.$yp.'&m='.$mp.'\')" class="prevMonth"><i class="fas fa-chevron-left"></i></a>
							<span class="titleDate">'.translateDate(date("F",$work['unix'])).'<small>'.$work['year'].'</small></span>
							<a onclick="goView(\'calendar&y='.$yn.'&m='.$mn.'\')" class="nextMonth"><i class="fas fa-chevron-right"></i></a>
						</div>';						
						$output['html'].='<div class="calendar">
							<div class="daynames">
								<div class="dayname weekend">'.translateDate("Sunday").'</div>
								<div class="dayname workday">'.translateDate("Monday").'</div>
								<div class="dayname workday">'.translateDate("Tuesday").'</div>
								<div class="dayname workday">'.translateDate("Wednesday").'</div>
								<div class="dayname workday">'.translateDate("Thursday").'</div>
								<div class="dayname workday">'.translateDate("Friday").'</div>
								<div class="dayname weekend">'.translateDate("Saturday").'</div>
							</div>';
						if($work['days'][1]['day_pos']!=0){
							$output['html'].='<div class="week">';
							for($i=0;$i<$work['days'][1]['day_pos'];$i++){
								$output['html'].='<div class="day previous"></div>';
							}
						}
						foreach($work['days'] as $day){
							if($day['day']==1 && $day['day_pos']==0) $output['html'].='<div class="week">';
							else if($day['day_pos']==0) $output['html'].='</div><div class="week">';
							$output['html'].='<div class="day'.(($day['day']==$today['day'] && $day['month']==$today['month'] && $day['year']==$today['year'])?' active':'').'"><span class="num">'.$day['day'].'</span>';
							$output['html'].='<span class="notes"><span class="title">'.translateDate(date("l, j F Y",$day['unix'])).'</span>';
							$fileday=$GLOBALS['root']."configs/calendar/".$day['month']."-".$day['day']."-".$day['year'].".txt";
							if(file_exists($fileday)){
								if($file=fopen($fileday,"r")){
									$i=0;
									while(!feof($file)) {
										$line = fgets($file);
										if($line!="") $output['html'].=$line."<br/>";
										$i++;
									}
									fclose($file);
								}				
							}
							$fileday=$GLOBALS['root']."configs/calendar/".$day['month']."-".$day['day'].".txt";
							if(file_exists($fileday)){
								if($file=fopen($fileday,"r")){
									$i=0;
									while(!feof($file)) {
										$line = fgets($file);
										if($line!="") $output['html'].=$line."<br/>";
										$i++;
									}
									fclose($file);
								}				
							}			
							$output['html'].='</span></div>';
						}
						if($work['days'][$work['total']]['day_pos']!=6){
							for($i=($work['days'][$work['total']]['day_pos']+1);$i<7;$i++){
								$output['html'].='<div class="day next"></div>';
							}
						}		
						$output['html'].='</div>
						</div>';
						
					break;
					case 'weather':
						// SUB PAGE : weather
						$weather=DBRead("weather");
						if(!$weather || !$cfg['enable']['weather']) die(json_encode(array("error"=>$output['html'].translateText("ERROR_MODULE_DISABLED")),true));
						if($cfg['enable']['icons']) system($cfg['icon_script'].' 3000 '.$cfg['icon']['remote']);
						#if($cfg['enable']['speak']) speak(translateText("WEATHER_FORECAST_FOR")." ".$weather['name'],$cfg['speak_module']);
						$jsonurl = "http://api.openweathermap.org/data/2.5/forecast?q=".$weather['city']."&appid=".$weather['api']."&lang=".$cfg['language']."&units=metric";
						$json = file_get_contents($jsonurl);
						$weather['remote'] = (array) json_decode($json);
						$list=$weather['remote']['list'];
						$i=0;
						$today=date("j",time());
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
									"code"=>$item["weather"][0]->id,
									"temp"=>round($item["main"]->temp,1).'°C',
									"feel"=>round($item["main"]->feels_like,1).'°C',
									"min"=>round($item["main"]->temp_min,0).'°C',
									"max"=>round($item["main"]->temp_max,0).'°C',
									"humidity"=>$item["main"]->humidity.'%',
									"clouds"=>$item["clouds"]->all.'%',
									"winds"=>$item["wind"]->speed.'m/s',
									"details"=>$item["weather"][0]->description,
									"snow"=>(($item["snow"])?$item["snow"]["3h"]:''),
									"rain"=>(($item["rain"])?$item["rain"]["3h"]:'')
								);
								$i++;
							}
							if($day!=$today){
								$output['next'][$day]['date']=$item["dt"];
								if($item["weather"][0]->id!="800") $output['next'][$day]['code'][substr($item["weather"][0]->id,0,1)]++;
								else $output['next'][$day]['code'][0]++;
								if($item["main"]->temp_min<$output['next'][$day]['min'] || $output['next'][$day]['min']=="") $output['next'][$day]['min']=round($item["main"]->temp_min,1);
								if($item["main"]->temp_max>$output['next'][$day]['max'] || $output['next'][$day]['max']=="") $output['next'][$day]['max']=round($item["main"]->temp_max,1);
								if($item["snow"]["3h"]>0) $output['next'][$day]['snow']=($output['next'][$day]['snow']+($item["snow"]["3h"]));
								if($item["rain"]["3h"]>0) $output['next'][$day]['rain']=($output['next'][$day]['rain']+($item["rain"]["3h"]));
							}
						}
						$output["html"].='<div class="weatherToday">';
						foreach($output['today'] as $today) {
							$output["html"].='<div class="todayBox">
								<div class="weatherRow">
									<span class="todayIcon"><i class="fas fa-'.getWeatherIcon($today['code'],date("H",$today["date"])).' '.getWeatherColor($today['code']).'"></i></span>
									<span class="todayTime">'.date("H",$today["date"]).'h00</span>
									<span class="todayTemp white">'.$today['temp'].'</span>
									<span class="todayFeel grey">('.$today['feel'].')</span>								
									<span class="todayDetails white">'.$today['details'].'</span>
								</div>
								<div class="weatherRow">
									<span class="todayTempMin white"><i class="fas fa-temperature-low blue"></i> '.$today['min'].'</span>
									<span class="todayTempMax white"><i class="fas fa-temperature-high orange"></i> '.$today['max'].'</span>
									<span class="todayHumidity"><i class="fas fa-tint blue"></i> '.$today['humidity'].'</span>
									<span class="todayWinds"><i class="fas fa-wind grey"></i> '.$today['winds'].'</span>
									<span class="todayClouds"><i class="fas fa-cloud grey"></i> '.$today['clouds'].'</span>
									'.(($today['snow']>0)?'<span class="todaySnow"><i class="fas fa-snowflake white"></i> '.$today['snow'].'cm</span>':'').'
									'.(($today['rain']>0)?'<span class="todayRain"><i class="fas fa-cloud-rain blue"></i> '.$today['rain'].'mm</span>':'').'
								</div>
							</div>';
						}
						$output["html"].='</div>
						<div class="weatherNextdays">';
						foreach($output['next'] as $nextday) {
							$t=0;
							foreach($output['code'] as $inc){
								$t=($t+$inc);
							}
							$code=null;
							foreach($output['code'] as $name=>$inc){
								if($inc>=($inc/count($output['code']))) $code=(($name=="0")?"800":$name."02");
							}
							if(!$code) $code=800;
							$output["html"].='<div class="nextdayBox">
								<span class="nextdayTime">'.translateDate(date("l",$nextday["date"])).' <small>'.translateDate(date("j F",$nextday["date"])).'</small></span>
								<span class="nextdayIcon"><i class="fas fa-'.getWeatherIcon($code,12).' '.getWeatherColor($code).'"></i></span>
								<span class="nextdayTempMin"><i class="fas fa-temperature-low blue"></i>  '.$nextday['min'].'°C</span>
								<span class="nextdayTempMax"><i class="fas fa-temperature-high orange"></i> '.$nextday['max'].'°C</span>
								'.(($nextday['snow']>0)?'<span class="nextdaySnow"><i class="fas fa-snowflake white"></i> '.$nextday['snow'].'cm</span>':'').'
								'.(($nextday['rain']>0)?'<span class="nextdayRain"><i class="fas fa-cloud-rain blue"></i> '.$nextday['rain'].'mm</span>':'').'		
							</div>';
						}
						$output["html"].='</div>';					
					break;
					case 'mailbox':
						// SUB PAGE : mailbox
						$mailbox=DBRead("mail");
						if(!$mailbox || !$cfg['enable']['mail']) die(json_encode(array("error"=>$output['html'].translateText("ERROR_MODULE_DISABLED")),true));
						if($cfg['enable']['icons']) system($cfg['icon_script'].' 3000 '.$cfg['icon']['remote']);
						$mbox = imap_open('{'.$mailbox['host'].':'.$mailbox['port'].'/imap/ssl/novalidate-cert}INBOX', $mailbox['user'], $mailbox['pass']);
						if(empty($mbox)) {
							die(json_encode(array("error"=>imap_last_error()),true));
						}
						else {
							$unread=imap_search($mbox, 'UNSEEN');
							if(empty($unread)) $tmp["unread"]=0;
							else $tmp["unread"]=count($unread);
							if($mail = imap_check($mbox)) $tmp["total"]=$mail->Nmsgs;
							else $tmp["total"]=0;
							$tmp["read"]=($tmp["total"]-$tmp["unread"]);
							if($tmp['total']==0) {
								$return=array("total"=>0,"unread"=>0,"read"=>0,"latest"=>array());
							}
							else{
								$return=$tmp;
								$return['latest']=array();
								if($tmp['unread']>0){
									foreach($unread as $unread_id) {
										$overview = imap_fetch_overview($mbox,$unread_id,0);
										$elements = imap_mime_header_decode($overview[0]->from);
										$from="";
										for ($i=0; $i<count($elements); $i++) {
											$from.=$elements[$i]->text;
										}							
										$return['latest'][]=array(
											"date"=>translateDate(date("l, j F, Y - H:i",strtotime($overview[0]->date))),
											"author"=>str_replace('"','',strip_tags($from)),
											"subject"=>strip_tags(imap_utf8($overview[0]->subject)));
									}
								}
							}
						}
						imap_close($mbox);	
						if(count($return['latest'])>=1){
							$output['html'].='<dl id="mailUnreadList">';
							foreach($return['latest'] as $mail){
								$output['html'].='<dt>'.$mail['subject'].'</dt><dd><i class="fas fa-calendar-alt"></i> '.$mail['date'].' <i class="fas fa-user"></i> '.$mail['author'].'</dd>';
							}
							$output['html'].='</dl>';
						}
						else{
							$output['html'].='<p class="Message"><center><i>'.translateText("NOMAIL").'</i></center></p>'; 
						}
						#if($cfg['enable']['speak']) speak(str_replace("%UNREAD%",($tmp['unread']),translateText("MAIL_YOUHAVEXNEW")),$cfg['speak_module']);
					break;
					default:
						// SUB PAGE : error
					$output['error']="Not valid content";
				}
			}
			else {
				$output['error']="Not valid action";
			}
			echo json_encode($output,true);
			exit;
		break;
		default:
			die("");
	}