import socket
from csv import writer
from datetime import datetime
import os
import time
from threading import Thread
from queue import Queue
import kafka_publish

HOST = "127.0.0.1"  # The server's hostname or IP address
DATA_PORT = 12348  # The port at which the Android App sends measurements
CSV_NAME = ""
LOG_FOLDER = "./Logs"
EXPERIMENT_NAME_DELIM = ",logStarts,"
KILL_OLD_PROCESS = "fuser " + str(DATA_PORT) + "/tcp"
PORT_REVERSE_COMMAND = "adb reverse tcp:" + str(DATA_PORT) + " tcp:" + str(DATA_PORT)
PUBLISH_TO_KAFKA = True
TCP_BUFFER_SIZE = 10000

# To Do: Receive entire message from Pawprints, using an end character.

def recv_stream_from_android(kafka_publish_queue):
    os.system(KILL_OLD_PROCESS)
    os.system(PORT_REVERSE_COMMAND)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, DATA_PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            while True:
                data = conn.recv(TCP_BUFFER_SIZE).decode('utf-8')
                if len(data) == 0:
                    break
                print(data)
                if EXPERIMENT_NAME_DELIM in data:
                    CSV_NAME =  data.split(EXPERIMENT_NAME_DELIM,1)[0]
                    log = data.split(EXPERIMENT_NAME_DELIM,1)[1]
                    log = log + "," + str(time.time())
                    if not os.path.exists(LOG_FOLDER):
                        os.makedirs(LOG_FOLDER)
                    with open(LOG_FOLDER + "/" + CSV_NAME + ".csv", "a") as file_object:
                            file_object.write(log + "\n")

                    if PUBLISH_TO_KAFKA:
                        kafka_publish_queue.put(log)
                        
if __name__ == "__main__":
    msg_queue = Queue()
    if PUBLISH_TO_KAFKA:
        t_kafka = Thread(target=kafka_publish.publish_loop, args=(msg_queue,))
        t_kafka.start()
    
    t_from_android = Thread(target=recv_stream_from_android, args=(msg_queue,))
    t_from_android.start()

    
