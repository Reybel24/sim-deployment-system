#!/usr/bin/env python
import pika, json, sys

# Rabbit host
rabbitHost = 'localhost'

def requestPackage(pckgName, pckgVersion):
    # Create connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitHost))
    channel = connection.channel()

    channel.queue_declare(queue='dep')

    # Data to send
    _payload = {
        'packageName': pckgName,
        'packageVersion': float(pckgVersion)
    }

    channel.basic_publish(exchange='', routing_key='dep', body=json.dumps(_payload))
    print(" [x] Request sent")
    connection.close()

# Take command line arguments
if ((len(sys.argv) - 1) == 2):
    _pckgName = sys.argv[1]
    _pckgVersion = sys.argv[2]
    print('Requesting: {0}, v{1}'.format(_pckgName, _pckgVersion))
    requestPackage(_pckgName, _pckgVersion)
else:
    print('Invalid parameters.')
