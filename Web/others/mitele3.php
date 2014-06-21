<?php
$url = $_GET['url'];
//echo $url;
$referer = $_GET['referer'];
//echo $referer;
// Create a stream
$opts = array(
  'http'=>array(
    'method'=>	"GET",
    'header'=>	"Referer: http://static1.tele-cinco.net/comun/swf/playerMitele.swf\r\n" .
                "Accept: */*\r\n" .
                "Origin: http://static1.tele-cinco.net\r\n" .
                "Connection: keep-alive\r\n" .
                "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36\r\n" . 
                "Accept-Language: de,en;q=0.7,en-us;q=0.3\r\n" . 
                "Content-type: application/x-www-form-urlencoded\r\n" .
                "Cookie: s_cc=true;s_fid=7B0AC1148C6D6D16-0521A69344CCF613;s_ppv=".$referer.",49,49,1186;s_sq=[[B]];\r\n"
  )
);

$context = stream_context_create($opts);
// Open the file using the HTTP headers set above
$content = file_get_contents(str_replace(".es?",".es/?",$url), false, $context);
echo $content;
?>