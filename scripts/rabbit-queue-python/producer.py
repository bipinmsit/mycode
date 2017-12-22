import pika
import json
import config as cfg
from flask import json
from flask import request
from flask import Flask, url_for

app = Flask(__name__)


@app.route('/messages', methods=['POST'])
def api_message():
    if request.headers['Content-Type'] == 'application/json':
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.RABBIT_HOST))
        channel = connection.channel()

        # Declare queue to send data
        channel.queue_declare(queue=cfg.QUEUE_TOPIC)
        request_data = json.dumps(request.json)
        message_passed_to_queue = request_data

        # Send data
        channel.basic_publish(exchange='', routing_key=cfg.QUEUE_TOPIC, body=message_passed_to_queue)
        connection.close()
        return "Sent data to RabbitMQ"
    else:
        return "415 Unsupported Media Type ;)"


if __name__ == "__main__":
    app.run(port=6000)
