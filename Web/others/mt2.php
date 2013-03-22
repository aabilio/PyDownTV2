<?php
	function curPageURL() {
		$pageURL = 'http';
		if ($_SERVER["HTTPS"] == "on") {$pageURL .= "s";}
		$pageURL .= "://";
		if ($_SERVER["SERVER_PORT"] != "80") {
			$pageURL .= $_SERVER["SERVER_NAME"].":".$_SERVER["SERVER_PORT"].$_SERVER["REQUEST_URI"];
		} else {
			$pageURL .= $_SERVER["SERVER_NAME"].$_SERVER["REQUEST_URI"];
		}
		return $pageURL;
	}
	if (isset($_GET['done']) && $_GET['done'] == "ok") {
		$u = $_GET['u'];
		$data = file_get_contents("http://web.pydowntv.com/api/".$u);
		$json = json_decode($data, true);
		header( 'Location: '.$json['videos'][0]['url_video'][0] );
	} else if (isset($_GET['r1']) && $_GET['r1'] == "ok") { //Second
		$loc = str_replace("&r1=ok", "&r2=ok", curPageURL());
		header( 'Location: '.$loc );
	} else if (isset($_GET['r2']) && $_GET['r2'] == "ok") { //Third
		$loc = str_replace("&r2=ok", "&r3=ok", curPageURL());
		header( 'Location: '.$loc );
	} else if (isset($_GET['r3']) && $_GET['r3'] == "ok") { //Third
		$loc = str_replace("&r3=ok", "&done=ok", curPageURL());
		header( 'Location: '.$loc );
	} else { //First
		header( 'Location: '.curPageURL()."&r1=ok" );
	}
?>