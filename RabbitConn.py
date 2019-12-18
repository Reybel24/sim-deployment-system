import pika

class RabbitConn():
    # Define rabbit connection parameters
    host = '25.1.81.153'
    port = 5672
    credentials = pika.PlainCredentials('admin', 'password')
    connectionParams = pika.ConnectionParameters(host, port, '/', credentials)

    def __init__(self):
        pass