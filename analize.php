<?php

$PESS = 'gh4ldSDcm45DDDff34SS2k234deElC';
$REG_IP = '189.111.203.249';
$IP = $_SERVER['REMOTE_ADDR'];

$conf = explode("\n",file_get_contents('.config'));
for($i=0; $i<count($conf); $i++)
{
	$s = explode(" ", $conf[$i]);
	if ($e[0]=='SEND_PASS') $PESS = $e[1];
	if ($e[0]=='SEND_IP') $REG_IP = $e[1];
}

if ($REG_IP==='none') $REG_IP = $IP;

if ($IP === $REG_IP)
	if ($PESS === $_GET['pass'])
	{
		file_put_contents('./sumario_online.log', $_GET['data']);
		echo 'ok';
	} else {
		echo 'erro de conexao';
	}

?>
