import pika
import json
import time
import config as cfg
import database_query
import Queue
import requests
import logging
import os.path

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

def setup_logging(folder=SCRIPT_DIR, logfile="scheduler.log"):
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # root.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.path.join(folder, logfile))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


setup_logging()

# Connect to RabbitMQ and create channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.RABBIT_HOST))
channel = connection.channel()

# Declare and listen queue
channel.queue_declare(queue=cfg.QUEUE_TOPIC)

logging.info(' [*] Waiting for messages.')


def check_for_vm_availabilty(message_passed_to_queue=None, env=True):
    list_of_available_vm = database_query.dbquery("AVAILABLE", env)
    if list_of_available_vm:
        schedule_the_vm(list_of_available_vm, message_passed_to_queue.get())
        return False
    else:
        time.sleep(5)
        return True


def schedule_the_vm(list_of_available_vm, message_passed_to_queue):
    for vm_state in list_of_available_vm:
        vm_details = {
            'id': vm_state[0],
            'vm_name': str(vm_state[1]),
            'vm_status': str(vm_state[2]),
            'vm_zone': str(vm_state[3]),
            'vm_ip': str(vm_state[4]),
            'createdAt': str(vm_state[5]),
            'updatedAt': str(vm_state[6]),
            'ssh_key': str(vm_state[7])
        }
    response = {'data': message_passed_to_queue, 'vm': vm_details}

    final_response = json.dumps(json.dumps(response))

    # api_url = 'https://workbenchtest.vimanalabs.com/graphql?query='
    api_url = str(message_passed_to_queue['api_url'])
    query = '''
        {
          photoscanProcess(input: ''' + final_response + ''')
        }
        '''
    logging.info(api_url + query)
    request_response = requests.get(api_url + query)
    logging.info(request_response)


def callback(ch, method, properties, body):
    logging.info("Method: {}" + format(method))
    logging.info("Properties: {}" + format(properties))
    message_json = json.loads(body)
    env = message_json['env']
    message_passed_to_queue = Queue.Queue()
    message_passed_to_queue.put(message_json)
    global db_not_available
    db_not_available = True
    while (db_not_available):
        db_not_available = check_for_vm_availabilty(message_passed_to_queue, env)


# Listen and receive data from queue
channel.basic_consume(callback, queue=cfg.QUEUE_TOPIC, no_ack=True)
channel.start_consuming()
