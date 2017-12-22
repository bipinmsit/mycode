#! /bin/sh


#run rabbitMQ as flask app in 6000 port
FLASK_APP=/home/pgprocess/rabbitmq/scripts/rabbit-queue-python/producer.py flask run -h localhost -p 6000 &


#run scheduler as background process
nohup python /home/pgprocess/rabbitmq/scripts/rabbit-queue-python/scheduler.py &
