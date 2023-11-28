from confluent_kafka import Producer
from queue import Queue
from threading import Thread
import sys
from time import sleep

BROKER = "35.171.54.199"
TOPIC = "sampleTopic"

configuration = {'bootstrap.servers':BROKER}

def delivery_callback(err, msg):
    if err:
        sys.stderr.write('%% Message failed delivery: %s\n' % err)
    else:
        sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                            (msg.topic(), msg.partition(), msg.offset()))

def run_kafka_producer(msg_queue):
    p = Producer(**configuration)
    print("Kafka producer connected to Broker")
    while True:
        try:   
            msg = msg_queue.get()     
            p.produce(TOPIC, msg, callback = delivery_callback)
        except Exception as e:
            sys.stderr.write("Error: " + str(e))
        finally:    
            p.flush()

def dummy_msg_producer(msg_queue):
        counter = 0
        while True:
            sleep(3)
            msg = "message" + str(counter)
            msg_queue.put(msg)
            counter += 1

if __name__ == "__main__":
    msg_queue = Queue()
    t_kafka = Thread(target=run_kafka_producer, args=(msg_queue,))
    t_msg_stream = Thread(target=dummy_msg_producer, args=(msg_queue,))

    t_kafka.start()
    t_msg_stream.start()