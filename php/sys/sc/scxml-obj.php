<?php

/* MusicTicker - XML version 1.666                           */
/* MAD props to Tom Pepper and Tag Loomis for all their help */
/* --------------------------------------------------------- */
/* SCXML object version 0.666                                */
/* January 26 2014 23:46 PT                                  */

error_reporting (E_ALL ^ E_NOTICE);

class SCXML {

  var $host="shoutcast_server_ip_address"; // host or ip of shoutcast server
  var $port="shoutcast_server_port_number"; // port of shoutcast server
  var $password="shoutcast_server_password"; // password for shoutcast server
  var $stream_id="shoutcast_stream_id"; // stream id (sid) for shoutcast stream

/* DO NOT CHANGE ANYTHING FROM THIS POINT ON - THIS MEANS YOU !!! */

  var $depth = 0;
  var $lastelem= array();
  var $xmlelem = array();
  var $xmldata = array();
  var $stackloc = 0;

  var $parser;

  function set_host($host) {
    $this->host=$host;
  }

  function set_port($port) {
    $this->port=$port;
  }

  function set_password($password) {
    $this->password=$password;
  }

  function set_streamid($stream_id) {
    $this->stream_id=$stream_id;
  }

  function startElement($parser, $name, $attrs) {
    $this->stackloc++;
    $this->lastelem[$this->stackloc]=$name;
    $this->depth++;
  }

  function endElement($parser, $name) {
    unset($this->lastelem[$this->stackloc]);
    $this->stackloc--;
  }

  function characterData($parser, $data) {
    $data=trim($data);
    if ($data) {
      $this->xmlelem[$this->depth]=$this->lastelem[$this->stackloc];
      $this->xmldata[$this->depth].=$data;
    }
  }

  function retrieveXML() {
    $rval=1;

    $sp=@fsockopen($this->host,$this->port,$errno,$errstr,10);
    if (!$sp) $rval=0;
    else {
      stream_set_blocking($sp,false);
      
	  // request xml data from sc server
      fputs($sp,"GET /admin.cgi?pass=$this->password&mode=viewxml&sid=$this->stream_id HTTP/1.1\nUser-Agent:Mozilla\n\n");
      
	  // if request takes > 15s then exit
      for($i=0; $i<30; $i++) {
        if(feof($sp)) break; // exit if connection broken
        $sp_data.=fread($sp,31337);
        usleep(500000);
      }

      // strip useless data so all we have is raw sc server XML data
      $sp_data=substr($sp_data, (strpos($sp_data, "\r\n\r\n")+4));

      // plain xml parser
      $this->parser = xml_parser_create();
      xml_set_object($this->parser,$this);
      xml_set_element_handler($this->parser, "startElement", "endElement");
      xml_set_character_data_handler($this->parser, "characterData");

      if (!xml_parse($this->parser, $sp_data, 1)) {
        $rval=-1;
      }

      xml_parser_free($this->parser);
    }
    return $rval;
  }

  function debugDump(){
    reset($this->xmlelem);
	foreach($this->xmlelem as $key=>$val) {
    //while (list($key,$val) = each($this->xmlelem)) {
      echo "$key. $val -> ".$this->xmldata[$key]."\n";
    }

  }

  function fetchMatchingArray($tag){
    reset($this->xmlelem);
    $rval = array();
	foreach($this->xmlelem as $key=>$val) {
	//while (list($key,$val) = each($this->xmlelem)) {
      if ($val==$tag) $rval[]=$this->xmldata[$key];
    }
    return $rval;
  }

  function fetchMatchingTag($tag){
    reset($this->xmlelem);
    $rval = "";
	foreach($this->xmlelem as $key=>$val) {
    //while (list($key,$val) = each($this->xmlelem)) {
      if ($val==$tag) $rval=$this->xmldata[$key];
    }
    return $rval;
  }

}

?>

