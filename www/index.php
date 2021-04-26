<?php
	// PiDeskBoard
	// 2021-03
	// By Mathieu Légaré (levelKro)
	
	// INDEX FILE
	error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING & ~E_STRICT & ~E_DEPRECATED);
	ini_set("display_errors", 1);
	ini_set('ignore_repeated_errors', TRUE); // always use TRUE
	ini_set('log_errors', TRUE); // Error/Exception file logging engine.
	ini_set('error_log', '/home/pi/pideskboard/php/error.log');	
	date_default_timezone_set("America/Montreal");
	setlocale(LC_MONETARY, 'en_US');
	
	@require_once("../configs/config.php");
	@require_once("../php/sys/libs.php");
	$radio=DBRead("radio");
	
	// HTML output
	echo '
<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<meta http-equiv="X-UA-Compatible" content="ie=edge">
		<meta name="google" content="notranslate">
		<title>PiDeskBoard UI</title>
		<link rel="stylesheet" href="ui/fontawesome/css/all.css">
		<link rel="stylesheet" href="ui/animate.min.css">
		<link rel="stylesheet" href="ui/ui.css">
		<link rel="stylesheet" href="ui/modules.css">
		<link rel="stylesheet" href="ui/cube3d.css">
		<script src="ui/libs.js"></script>
	</head>
	<body>
		<div class="frameLimit" id="mainFrame">
			<div class="frameMenu" id="mainMenu">
				<div class="menu">
					<i class="fas fa-folder-plus"></i>
					<div class="links" id="links"></div>
				</div>
				<div class="controls">
					<!-- Controls the deskboard or the display -->
					<i class="fas fa-toolbox grey"></i>
					<div class="options">
						<span class="title">'.translateText("CTRL_TITLE").'</span>
						<ul>
							<li onclick="getApi(\'output\',\'poweroff\',\'\');"><i class="fas fa-power-off red"></i> '.translateText("CTRL_POWEROFF").'</li>
							<li onclick="getApi(\'output\',\'reboot\',\'\');"><i class="fas fa-redo orange"></i> '.translateText("CTRL_REBOOT").'</li>
							<li onclick="getApi(\'output\',\'refresh\',\'\');"><i class="fas fa-sync green"></i> '.translateText("CTRL_REFRESH").'</li>
							<li onclick="getApi(\'output\',\'bluetooth\',\'\');"><i class="fas fa-volume-up blue"></i> '.translateText("CTRL_BLUETOOTH").'</li>
						</ul>
					</div>
				</div>
			</div>
			<div class="frameContent" id="mainContent">
				<div id="loading" class="loading rotating" style="display:none;"><i class="fas fa-spinner"></i></div>
				<div id="buttonBack" class="buttonBack" onclick="goEmpty();"><i class="fas fa-chevron-circle-left"></i></div>
				<div id="mainStatus">
					<img class="piLogo" src="ui/rpi3d.gif" width="64" height="64"/>
					<div class="frameClock" onclick="goView(\'calendar\');">
						<span id="time"></span>
						<span id="date"></span>
					</div>
					<div class="frameTodo" id="todo" onclick="goView(\'calendar\');"></div>
					<div class="frameMailbox" id="mailbox" onclick="goView(\'mailbox\');">
						<span id="mailboxRead"></span>
						<span id="mailboxUnread"></span>
					</div>
					<div class="frameWeather" id="weather" onclick="goView(\'weather\');">
						<div class="weatherCurrent">
							<span id="weatherImage"></span>
							<span id="weatherTemp"></span>
							<span id="weatherFeel"></span>
							<span id="weatherDetails"></span>
						</div>
						<div class="weatherInfos">
							<span id="weatherCloud"></span>
							<span id="weatherTempMin"></span>
							<span id="weatherTempMax"></span>
							<span id="weatherRainSnow"></span>
						</div>
					</div>
					<div class="frameRadio" onclick="goRadio();">
						<a id="radioPlayerPlay"><i class="fas fa-play"></i></a>
						<a id="radioPlayerPause" style="display:none;"><i class="fas fa-pause"></i></a>
						<span id="radioTime">00:00:00</span>
						<marquee behavior="alternate" direction="left" scrollamount=1 scrolldelay=150" class="radioDetails"><span id="radioTitle"></span> -- <span id="radioSong"></span></marquee>					
						<audio id="radioPlayer" preload="none"><source src="http://'.$radio["host"].':'.$radio["port"].'/'.$radio["id"].'" type="audio/mpeg"></audio>					
					</div>
				</div>
				<div class="output" id="output"></div>
			</div>
		</div>
		<script src="ui/run.js"></script>
	</body>
</html>';	