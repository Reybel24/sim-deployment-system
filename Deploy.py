#!/usr/bin/env python
# Invoke this from command line to retrieve a package

import pika, json, sys
from RabbitConn import RabbitConn
import install
import time

def requestPackage(pckgName, pckgVersion, requestorID):
    # Rabbit connection info
    rabbitConn = RabbitConn()

    # Create connection and channel
    connection = pika.BlockingConnection(rabbitConn.connectionParams)
    channel = connection.channel()
    channel.queue_declare(queue='dep')

    # Data to send
    _payload = {
        'packageName': pckgName,
        'packageVersion': float(pckgVersion),
        'requestorID': requestorID
    }

    # Send it
    channel.basic_publish(exchange='', routing_key='dep', body=json.dumps(_payload))
    print(" [x] Request sent")

    # Close the connection once the data is sent.
    connection.close()

    # Wait
    time.sleep(4)
    
    # Install recieved package
    install.installBundle()

# Take command line arguments
if ((len(sys.argv) - 1) == 3):
    _pckgName = sys.argv[1]
    _pckgVersion = sys.argv[2]
    _requestorID = sys.argv[3]
    print('Requesting: {0}, v{1} for user {2}'.format(_pckgName, _pckgVersion, _requestorID))
    requestPackage(_pckgName, _pckgVersion, _requestorID)
else:
    print('Invalid parameters. Please provide the package name, version, and destination as such: front-end 1.4 fe_qa')
