#!/usr/bin/php
<?php
require_once('path.inc');
require_once('get_host_info.inc');
require_once('rabbitMQLib.inc');


// Step 1: Take package name and version
// Step 2: Look up package inside JSON
// Step 3: Identify modules required for that package from JSON
// Step 4: Look up these modules in database by ID
// Step 5: Grab packages from stored location
// Step 6: Send to bundler script to be bundled into tar

// Listen for incoming data
# $server = new rabbitMQServer("testRabbitMQ.ini","testServer");

// Process data
# $server->process_requests('requestProcessor');
# exit();

?>