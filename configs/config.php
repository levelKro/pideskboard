<?php 
	clearstatcache();
	function readConfig(){
		// Read data
		if(file_exists(dirname(__FILE__)."/config.ini"))	{
			return parse_ini_file(dirname(__FILE__)."/config.ini", true);
		}
		else return false;
	}
	$cfg=readConfig();
	if(!$cfg) {
		die("Can't load config , can't find in ".dirname(__FILE__));
	}
	// Main config files	
	$cfg["links"]=array(
			array(
				"module"=>"list",
				"icon"=>"shipping-fast",
				"file"=>"orders.txt",
				"name"=>"Commandes",
			),/*
			array(
				"module"=>"network",
				"icon"=>"network-wired",
				"name"=>"Réseau"
			),
			array(
				"module"=>"servers",
				"icon"=>"server",
				"name"=>"Serveurs"
			),*/
			array(
				"module"=>"image",
				"icon"=>"video",
				"url"=>"http://192.168.0.100:8090/camera1",
				"name"=>"Caméra Salon"
			),
			array(
				"module"=>"image",
				"icon"=>"video",
				"url"=>"http://192.168.0.100:8090/camera2",
				"name"=>"Caméra Cuisine"
			),
			array(
				"module"=>"image",
				"icon"=>"video",
				"url"=>"http://192.168.0.100:8090/camera3",
				"name"=>"Caméra Ruelle"
			)
		);
	// Register to a Global variables
	$GLOBALS=$cfg;
