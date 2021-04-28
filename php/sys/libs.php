<?php
	// LIBS FILE
	if(!isset($cfg) || !is_array($cfg)) die("");
	if(file_exists($GLOBALS['system']['php']."sys/lang/".$cfg['system']['language'].".lang.php")) require_once($GLOBALS['system']['php']."sys/lang/".$cfg['system']['language'].".lang.php");
	else require_once($GLOBALS['system']['php']."sys/lang/en.lang.php");
	function remoteUrl($url,$array=false,$json=false){
		// Capture content on remote URL
		$ch = curl_init();
		curl_setopt($ch,CURLOPT_URL,$url);
		curl_setopt($ch,CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch,CURLOPT_USERAGENT, "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3");
		if(is_array($array)){
			curl_setopt($ch, CURLOPT_POST, 1);
			if($json===true) curl_setopt($ch, CURLOPT_POSTFIELDS,json_encode($array));
			else {
				$out="@@@";
				foreach($array as $n=>$v) $out."&".$n."=".$v;
				curl_setopt($ch, CURLOPT_POSTFIELDS,str_replace("@@@&","",$out));
			}
		}
		curl_setopt($ch,CURLOPT_TIMEOUT,100000);
		$result = curl_exec($ch);
		return $result; 
		curl_close($ch);
	}	
	function remotePing($ip){
		// Ping the remote host
		$ping = exec("ping -c 1 $ip"); 
		$ping=explode("=",$ping); 
		if(!$ping[1]) return "offline";
		else return "online";	
	}
	function remoteState($host,$port){
	    // Check if port on the host is open
	  	if($fp=@fsockopen($host, $port, $errno, $errstr, 20)){ $rep="online"; } 
		else{ $rep="offline"; }
		return($rep); 
	  	@fclose($fp);
	}	
	function getWeatherIcon($code,$h=null){
	    // Code to Image name, based on OpenWeather and the FontAwesome limitations
		if(!is_numeric($h) || $h==null) $h=date("H");
		elseif($h>24) $h=24;
		elseif($h<0) $h=0;
		$icons=array(
			"300"=>"smog",
			"301"=>"smog",
			"302"=>"smog",
			"310"=>"cloud-rain",
			"311"=>"cloud-rain",
			"312"=>"cloud-showers-heavy",
			"313"=>"cloud-showers-heavy",
			"314"=>"cloud-showers-heavy",
			"321"=>"cloud-showers-heavy",
			"500"=>array("cloud-sun-rain","cloud-moon-rain"),
			"501"=>"cloud-rain",
			"502"=>"cloud-showers-heavy",
			"503"=>"cloud-showers-heavy",
			"504"=>"cloud-showers-heavy",
			"511"=>"cloud-mealtball",
			"520"=>"cloud-showers-heavy",
			"521"=>"cloud-showers-heavy",
			"522"=>"cloud-showers-heavy",
			"531"=>"cloud-showers-heavy",
			"600"=>"snowflake",
			"601"=>"snowflake",
			"602"=>"snowflake",
			"611"=>"cloud-rain",
			"612"=>"cloud-rain",
			"613"=>"cloud-showers-heavy",
			"615"=>"cloud-showers-heavy",
			"620"=>"cloud",
			"621"=>"cloud-rain",
			"622"=>"cloud-showers-heavy",
			"701"=>"smog",
			"711"=>"smog",
			"721"=>"smog",
			"731"=>"wind",
			"741"=>"smog",
			"751"=>"wind",
			"761"=>"wind",
			"762"=>"wind",
			"771"=>"wind",
			"781"=>"wind",
			"200"=>"bolt",
			"201"=>"bolt",
			"202"=>"bolt",
			"210"=>"bolt",
			"211"=>"bolt",
			"212"=>"bolt",
			"221"=>"bolt",
			"230"=>"bolt",
			"231"=>"bolt",
			"232"=>"bolt",
			"800"=>array("sun","moon"),
			"801"=>array("cloud-sun","cloud-moon"),
			"802"=>array("cloud-sun","cloud-moon"),
			"803"=>"cloud",
			"804"=>"cloud",
		);
		$icon=$icons[$code];
		if(is_array($icon)){ 
			if($h>=21 || $h<=4){ return $icon[1]; } 
			else{ return $icon[0]; } 
		}
		else{ return $icon;	}
	}	
	function getWeatherColor($code,$h=null){
		// COlor the weatherIcon with a good color
		if(!is_numeric($h) || $h==null) $h=date("G");
		elseif($h>24) $h=24;
		elseif($h<0) $h=0;
		$colors=array(
			"300"=>"grey",
			"301"=>"grey",
			"302"=>"grey",
			"310"=>"grey",
			"311"=>"grey",
			"312"=>"grey",
			"313"=>"grey",
			"314"=>"grey",
			"321"=>"grey",
			"500"=>"blue",
			"501"=>"blue",
			"502"=>"blue",
			"503"=>"blue",
			"504"=>"blue",
			"511"=>"blue",
			"520"=>"blue",
			"521"=>"blue",
			"522"=>"blue",
			"531"=>"blue",
			"600"=>"white",
			"601"=>"white",
			"602"=>"white",
			"611"=>"white",
			"612"=>"white",
			"613"=>"white",
			"615"=>"white",
			"620"=>"white",
			"621"=>"white",
			"622"=>"white",
			"701"=>"red",
			"711"=>"red",
			"721"=>"red",
			"731"=>"red",
			"741"=>"red",
			"751"=>"red",
			"761"=>"red",
			"762"=>"red",
			"771"=>"red",
			"781"=>"red",
			"200"=>"orange",
			"201"=>"orange",
			"202"=>"orange",
			"210"=>"orange",
			"211"=>"orange",
			"212"=>"orange",
			"221"=>"orange",
			"230"=>"orange",
			"231"=>"orange",
			"232"=>"orange",
			"800"=>array("yellow","white"),
			"801"=>array("yellow","white"),
			"802"=>array("yellow","white"),
			"803"=>"grey",
			"804"=>"grey",
		);
		$color=$colors[$code];
		if(is_array($color)){ 
			if($h>=21 || $h<=4){ return $color[1]; } 
			else{ return $color[0]; } 
		}
		else{ return $color;	}
	}
	function getServicePort($service){
		// Services ports, not complete, but containt most common
		$services=array(
			"ftp"=>"21",
			"ssh"=>"22",
			"dns"=>"53",
			"http"=>"80",
			"https"=>"443",
			"sc"=>"8000",
			"tnet"=>"31457",
			"webmin"=>"10000",
			"sql"=>"3306",
			"source"=>"27015",
			"smtp"=>"25",
			"pop"=>"995",
			"rtmp"=>"1935",
			"mc"=>"25565",
			"mcpe"=>"19132",
			"smb"=>"445",
			"netb"=>"139",
			"proxy"=>"3128"
		);	
		return $services[$service];
	}
	/*
		Ultra mini Database like a Ram for current session
		This is for manage process on the machine, like speaking, for not made multiple time if more than one client is connected on dashboard UI
	*/
	function DBRamInit(){
		// Cleaning and reset datas
		$dh=opendir($GLOBALS['system']['cache']);
		while (false !== ($filename = readdir($dh))) {
			if($filename!="." && $filename!=".." && !is_dir($d.$filename)){
				@unlink($d.$filename);
			}
		}		
	}
	function DBRamSave($name,$value){
		// Save data
		$f=$GLOBALS['system']['cache'].$name.".dbr";
		if(file_exists($f) && ($value=="" || $value==false)) unlink($f);
		else {
			$fp=fopen($f, 'w+');
			fwrite($fp,'<?php $value="'.$value.'";');
			fclose($fp);		
		}
	}
	function DBRamRead($name){
		// Read data
		$f=$GLOBALS['system']['cache'].$name.".dbr";
		if(file_exists($f))	{
			@include($f);
			return $value;
		}
		else return false;
	}
	// For static values
	function DBSave($name,$value,$table=null){
		// Save data
		$f=$GLOBALS['system']['db'].(($table!=null)?$table."/":"").$name.".ini";
		return write_ini_file($f,$value);
	}
	function DBRead($name,$table=null){
		// Read data
		$f=$GLOBALS['system']['db'].(($table!=null)?$table."/":"").$name.".ini";
		if(file_exists($f))	{
			return parse_ini_file($f, true);
		}
		else return false;
	}
	function DBReadAll($name){
		// Read data
		$f=$GLOBALS['system']['db'].$name."/";
		$dh  = opendir($f);
		$output=array();
		while (false !== ($filename = readdir($dh))) {
			if($filename!="." && $filename!=".." && $filename!="lost+found" && substr($filename,0,1)!="." && !is_dir($f.$filename)){
				$output[str_replace(".ini","",$filename)]=parse_ini_file($f.$filename, true);
			}
		}		
		if(count($output)>=1) return $output;
		else return false;
	}
	// Speak (add to queue list)
	function speak($txt,$lang="en"){
		$txt=strip_tags(html_entity_decode($txt));
		$fp = fopen($GLOBALS['system']['cache']."talk/".time().".dbr", 'a+'); 
		fwrite($fp, $lang."||".$txt."\r\n");	
		fclose($fp);
		/*
		$txt=strip_tags(html_entity_decode($txt));
		$fp = fopen($GLOBALS['cache']."talk.dbr", 'a+'); 
		fwrite($fp, $lang."||".$txt."\r\n");	
		fclose($fp);
		*/		
	}
	function jsonSave($name,$value,$table=null){
		// Save data
		$f=$GLOBALS['system']['cache'].(($table!=null)?$table."/":"").$name.".json";
		if(file_exists($f) && ($value=="" || $value==false)) unlink($f);
		else {
			$fp=fopen($f, 'w+');
			fwrite($fp,json_encode($value,true));
			fclose($fp);		
		}
	}
	function jsonRead($name,$table=null){
		// Save data
		$f=$GLOBALS['system']['cache'].(($table!=null)?$table."/":"").$name.".json";
		$lines="";
		if($file=fopen($f,"r")){
			while(!feof($file)) {
				$line = fgets($file);
				if($line!="") $lines.=$line;
			}
			fclose($file);
		}	
		return json_decode($lines,true);
	}
	if (!function_exists('write_ini_file')) {
		/**
		 * Write an ini configuration file
		 * 
		 * @param string $file
		 * @param array  $array
		 * @return bool
		 */
		function write_ini_file($file, $array = []) {
			// check first argument is string
			if (!is_string($file)) {
				throw new \InvalidArgumentException('Function argument 1 must be a string.');
			}
			// check second argument is array
			if (!is_array($array)) {
				throw new \InvalidArgumentException('Function argument 2 must be an array.');
			}
			// process array
			$data = array();
			foreach ($array as $key => $val) {
				if (is_array($val)) {
					$data[] = "[$key]";
					foreach ($val as $skey => $sval) {
						if (is_array($sval)) {
							foreach ($sval as $_skey => $_sval) {
								if (is_numeric($_skey)) {
									$data[] = $skey.'[] = '.(is_numeric($_sval) ? $_sval : (ctype_upper($_sval) ? $_sval : '"'.$_sval.'"'));
								} else {
									$data[] = $skey.'['.$_skey.'] = '.(is_numeric($_sval) ? $_sval : (ctype_upper($_sval) ? $_sval : '"'.$_sval.'"'));
								}
							}
						} else {
							$data[] = $skey.' = '.(is_numeric($sval) ? $sval : (ctype_upper($sval) ? $sval : '"'.$sval.'"'));
						}
					}
				} else {
					$data[] = $key.' = '.(is_numeric($val) ? $val : (ctype_upper($val) ? $val : '"'.$val.'"'));
				}
				// empty line
				$data[] = null;
			}
			// open file pointer, init flock options
			$fp = fopen($file, 'w');
			$retries = 0;
			$max_retries = 100;
			if (!$fp) {
				return false;
			}
			// loop until get lock, or reach max retries
			do {
				if ($retries > 0) {
					usleep(rand(1, 5000));
				}
				$retries += 1;
			} while (!flock($fp, LOCK_EX) && $retries <= $max_retries);
			// couldn't get the lock
			if ($retries == $max_retries) {
				return false;
			}
			// got lock, write data
			fwrite($fp, implode(PHP_EOL, $data).PHP_EOL);
			// release lock
			flock($fp, LOCK_UN);
			fclose($fp);
			return true;
		}
	}

	// Modules access by the dashboard section
	$cfg["mailbox"]=DBRead("mail");
	$cfg["weather"]=DBRead("weather");
	$cfg["calendar"]=array();
	// Register to a Global variables
	$GLOBALS=$cfg;	