#!/usr/bin/php
<?php
require_once('path.inc');
require_once('get_host_info.inc');
require_once('rabbitMQLib.inc');

// Listen for incoming data
$server = new rabbitMQServer("testRabbitMQ.ini","testServer");

function requestProcessor() {
    echo 'test';
}

// Process data
$server->process_requests('requestProcessor');
exit();

?>