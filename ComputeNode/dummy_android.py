#!/usr/bin/env python3
import socket
from datetime import datetime
import os
import time
from threading import Thread
from queue import Queue
import kafka_publish

LOG_PATH = "./pawprints_log.txt"
PUBLISH_TO_KAFKA = True
STREAM_INTERVAL = 1 # seconds
SOURCE_ID = "Garuda"

def read_stream_from_log(kafka_publish_queue):
    with open(LOG_PATH) as f:
        log_lines = f.readlines()
        for log_line in log_lines:
            time.sleep(STREAM_INTERVAL)
            kafka_publish_queue.put(log_line)
    
if __name__ == "__main__":
    msg_queue = Queue()
    if PUBLISH_TO_KAFKA:
        t_kafka = Thread(target=kafka_publish.publish_loop, args=(msg_queue,))
        t_kafka.start()
    
    t_from_log = Thread(target=read_stream_from_log, args=(msg_queue,))
    t_from_log.start()
