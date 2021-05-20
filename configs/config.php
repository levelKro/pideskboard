<?php 
	clearstatcache();
	function readConfig(){
		if(file_exists(dirname(__FILE__)."/config.ini"))	{
			return parse_ini_file(dirname(__FILE__)."/config.ini", true);
		}
		else return false;
	}
	$cfg=readConfig();
	if(!$cfg) die("Can't load config , can't find in ".dirname(__FILE__));
	else $GLOBALS=$cfg;
