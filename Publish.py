# Invoke from command line to publish a bundle
# A bundle consists of 1 or more packages
import shutil
import os
import glob
import Send
from RabbitConn import RabbitConn
import pika
import json

# Bundle working directory into publish.zip
def doPublish():
    # Prepare for publish
    _dest = 'publish/'
    _working = 'working/'

    # Bundle (zip, tar)
    shutil.make_archive(_dest + 'publish', 'zip', _working)

    # Send to QA
    # Send.send('QA', 'publish/publish.zip')

    _path = os.path.join(_working, 'vue-front-end', 'sim-config.json')
    with open(_path) as f:
        _data = json.load(f)
    # print(_data)

    # Create bundle meta
    _meta = []
    for item in os.listdir(_working):
        if os.path.isdir(os.path.join(_working, item)):
            # print(item)
            if os.path.isfile(os.path.join(_working, item, 'sim-config.json')):
                print('Found config for ' + item)
                # Add config to meta
                # Add bundle metadata to file
                _path = os.path.join(_working, str(item), 'sim-config.json')
                with open(_path) as f:
                    _data = json.load(f)
                    # print(_data)
                    _meta.append(_data)

    print('Done.')
    # print(_meta)

    # Notify
    sendPublishMessage(_meta)

    
def sendPublishMessage(payload):
    # Send published message
    rabbitConn = RabbitConn()

    # Create connection and channel
    connection = pika.BlockingConnection(rabbitConn.connectionParams)
    channel = connection.channel()
    channel.queue_declare(queue='publish')

    # Send it
    channel.basic_publish(exchange='', routing_key='publish', body=json.dumps(payload))

    # Close the connection once the data is sent.
    connection.close()

# Publish package
doPublish()