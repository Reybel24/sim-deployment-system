import pika

class RabbitConn():
    # Define rabbit connection parameters
    host = 'localhost'
    port = 5672
    credentials = pika.PlainCredentials('admin', 'password')
    connectionParams = pika.ConnectionParameters(host, port, '/', credentials)

    def __init__(self):
        pass