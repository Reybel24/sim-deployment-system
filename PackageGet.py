#!/usr/bin/env python
import pika, json, sys, os
from RabbitConn import RabbitConn

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

    # Install package
    _wd = os.getcwd()
    _file = os.path.join(_wd, 'installer.sh')
    os.system(_file + ' /home/rey/Desktop/bundle.zip')

# Take command line arguments
if ((len(sys.argv) - 1) == 3):
    _pckgName = sys.argv[1]
    _pckgVersion = sys.argv[2]
    _requestorID = sys.argv[3]
    print('Requesting: {0}, v{1} for user {2}'.format(_pckgName, _pckgVersion, _requestorID))
    requestPackage(_pckgName, _pckgVersion, _requestorID)
else:
    print('Invalid parameters. Please provide the package name and version as such: front-end 1.4')
