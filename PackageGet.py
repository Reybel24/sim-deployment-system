#!/usr/bin/env python
import pika, json, sys
from RabbitConn import RabbitConn

def requestPackage(pckgName, pckgVersion):
    # Rabbit connection info
    rabbitConn = RabbitConn()

    # Create connection and channel
    connection = pika.BlockingConnection(rabbitConn.connectionParams)
    channel = connection.channel()
    channel.queue_declare(queue='dep')

    # Data to send
    _payload = {
        'packageName': pckgName,
        'packageVersion': float(pckgVersion)
    }

    # Send it
    channel.basic_publish(exchange='', routing_key='dep', body=json.dumps(_payload))
    print(" [x] Request sent")

    # Close the connection once the data is sent.
    connection.close()

# Take command line arguments
if ((len(sys.argv) - 1) == 2):
    _pckgName = sys.argv[1]
    _pckgVersion = sys.argv[2]
    print('Requesting: {0}, v{1}'.format(_pckgName, _pckgVersion))
    requestPackage(_pckgName, _pckgVersion)
else:
    print('Invalid parameters. Please provide the package name and version as such: front-end 1.4')
