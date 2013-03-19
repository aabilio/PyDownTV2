<?php
	$mt_url = $_GET["mt_url"];
	$vu = $_GET["vu"];
	$h = $_GET["h"];
	$start = $_GET["start"];
	$final_url = $mt_url . "&vu=" . $vu . "&h=" . $h . "&start=" . $start;
	header( 'Location: '.$final_url ) ;
?>
