def callbackQA(ch, method, properties, body):
    print('Installing QA package...')
    # Unpack

# Run callback on message consume
channel.basic_consume(
    queue='publish', on_message_callback=callbackQA, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Listen
channel.start_consuming()