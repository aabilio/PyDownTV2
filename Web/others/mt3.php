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
		$data = file_get_contents("http://www.pydowntv.com/api/".$u);
		$json = json_decode($data, true);
		header( 'Location: '.$json['videos'][0]['url_video'][0] ); 
	} else {
		echo "<html>
				<head>
					<meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
				</head>
				<body style='background-color: #181818;'>
					<a rel=noreferrer target='_blank' style='color: #16a6b6; text-decoration: underline; font-weight: bold; font-family: \"Source Sans Pro\";' href='".curPageURL()."&done=ok'>".$_GET['tit']."</a>
				</body>
				</html>";
	}
?>