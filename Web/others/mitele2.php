<?php
/* Enviar una petición POST a https://secure.example.com/form_action.php
* Incluir los elementos de formulario llamados "foo" y "bar" con valores sin importancia
*/
/*function hu_urlencode($t) 
{ 
    $tu = urlencode($t); 

    // /
    $tu = str_replace('%2F','/',$tu);
    return $tu; 
}; 

//Recibir hash e id
$hash= $_GET["hash"];
$id= $_GET["id"];
//echo "1 - $hash";

$hash = hu_urlencode($hash);

echo "2 - $hash";*/

$hash = $_POST["hash"]; 
//$id = $_POST["id"];
//Fin de recibir hash e id

$sock = fsockopen("token.mitele.es", 80, $errno, $errstr, 30);
if (!$sock) die("$errstr ($errno)\n");

$data = "hash=" . urlencode($hash); /*. "&id=" . urlencode($id) . "&startTime" . urlencode("0") . "&endTime" . urlencode("0");*/

fwrite($sock, "POST /index.php HTTP/1.0\r\n");
fwrite($sock, "Host: token.mitele.es\r\n");
fwrite($sock, "Accept-Charset: ISO-8859-1,UTF-8;q=0.7,*;q=0.7\r\n");
fwrite($sock, "Referer: http://static1.tele-cinco.net/comun/swf/playerMitele.swf\r\n");
fwrite($sock, "Connection: close\r\n");
fwrite($sock, "Accept-Language: de,en;q=0.7,en-us;q=0.3\r\n");
fwrite($sock, "Content-type: application/x-www-form-urlencoded\r\n");
fwrite($sock, "Content-length: " . strlen($data) . "\r\n");
fwrite($sock, "Accept: */*\r\n");
fwrite($sock, "\r\n");
fwrite($sock, "$data\r\n");
fwrite($sock, "\r\n");

$headers = "";
while ($str = trim(fgets($sock, 4096)))
$headers .= "$str\n";

echo "\n";

$body = "";
while (!feof($sock))
$body .= fgets($sock, 4096);

echo $body;

fclose($sock);
?>