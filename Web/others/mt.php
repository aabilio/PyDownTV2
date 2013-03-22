<?php

	function get_url($h, $p) {
		$sock = fsockopen($h, 80, $errno, $errstr, 30);
		if (!$sock) die("$errstr ($errno)\n");


		fwrite($sock, "GET ".$p." HTTP/1.0\r\n");
		fwrite($sock, "Host: ".$p."\r\n");
		fwrite($sock, "Accept-Charset: ISO-8859-1,UTF-8;q=0.7,*;q=0.7\r\n");
		fwrite($sock, "Referer: http://holass.com\r\n");
		fwrite($sock, "Connection: close\r\n");
		fwrite($sock, "Accept-Language: de,en;q=0.7,en-us;q=0.3\r\n");
		fwrite($sock, "Content-type: application/x-www-form-urlencoded\r\n");
		//fwrite($sock, "Content-length: " . strlen($data) . "\r\n");
		fwrite($sock, "Accept: */*\r\n");
		fwrite($sock, "\r\n");
		//fwrite($sock, "$data\r\n");
		//fwrite($sock, "\r\n");

		$headers = "";
		while ($str = trim(fgets($sock, 4096)))
		$headers .= "$str\n";

		echo "\n";

		$body = "";
		while (!feof($sock))
		$body .= fgets($sock, 4096);
		fclose($sock);
		echo $body;
		exit();
		return $body;
	}

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
		//$data = get_url("pydowntv.com", "/api/".$u);
		$json = json_decode($data, true);
		header( 'Location: '.$json['videos'][0]['url_video'][0] );
	} else {
		echo '<html>
	<head>
    	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js" type="text/javascript"></script>
	</head>
	<body>
		<p>Clic derecho en el enlace: Guardar Enlace Como...</p>
		<a rel=noreferrer href="'.curPageURL().'&done=ok" id="go">Descargar MP4</a>
		<script type="text/javascript">
			//$(\'#go\').attr("href", window.location.href + "&done=ok");
			//$(\'#go\').click(function(){
			//	window.location.href = window.location.href + "&done=ok"
			//});
		</script>
	</body>
</html>';
	}
?>
