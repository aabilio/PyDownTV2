<?php
	$mt_url = $_GET["mt_url"];
	$data = file_get_contents("http://web.pydowntv.com/api/".$mt_url);
	$json = json_decode($data, true);
	$_SERVER["HTTP_REFERER"] = "http://holacaracola.com";
	//echo $_SERVER["HTTP_REFERER"];
	//exit();
	/*$vu = $_GET["vu"];
	$h = $_GET["h"];
	$start = $_GET["start"];
	$final_url = $mt_url . "&vu=" . $vu . "&h=" . $h . "&start=" . $start;
	header( 'Location: '.$final_url );*/
	//header( 'Referer: hola.com')
	header( 'Location: '.$json['videos'][0]['url_video'][0] );
?>
