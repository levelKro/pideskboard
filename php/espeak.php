<?php
	// CLI File
	error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING & ~E_STRICT & ~E_DEPRECATED);
	ini_set("display_errors", true);
	date_default_timezone_set("America/Montreal");
	setlocale(LC_MONETARY, 'en_US');
	ini_set('ignore_repeated_errors', TRUE); // always use TRUE
	ini_set('log_errors', TRUE); // Error/Exception file logging engine.
	ini_set('error_log', '/home/pi/pideskboard/php/error.log'); // Logging file path	
	require_once("/home/pi/pideskboard/configs/config.php");
	require_once("sys/libs.php");
start:
	$f=$GLOBALS['cache']."talk/";
	$dh  = opendir($f);
	$output=array();
	while (false !== ($filename = readdir($dh))) {
		if($filename!="." && $filename!=".." && $filename!="lost+found" && substr($filename,0,1)!="." && !is_dir($f.$filename)){
			if ($file=fopen($f.$filename, "r")) { 
				while(!feof($file)) {
					$line = fgets($file);
					if($line!=""){
						$sector=explode("||",$line);
						if($sector[1]!="" || !$sector[1]) {
							echo "*** (".str_replace(" ","+",$sector[0]).") ".$sector[1]."\n";
							if($cfg['enable']['icons']) system($cfg['icon']['path'].' 5000 '.$cfg['icon']['speak']." 2");
							shell_exec($cfg['espeak']['path'].' "'.str_replace(" ","+",$sector[0]).'" "'.$sector[1].'" &');
						}
					}
				}
				fclose($file);		
				@unlink($f.$filename);
			}			
		}
	}
	sleep(2);
goto start;
