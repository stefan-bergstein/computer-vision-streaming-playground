#import datetime
import os
import sys
#from flask import Flask, Response
from kafka import KafkaConsumer
import json
import msgpack
import numpy as np
import cv2
import base64
import time
import socketio

is_connected=False

sio = socketio.Client()

@sio.event
def connect():
    print('* Successfully connected to server.')


@sio.event
def connect_error():
    print('* Failed to connect to server.')


@sio.event
def disconnect():
    print('* Disconnected from server.')
    global is_connected
    is_connected=False


def connect_server(server):
    print('* Connecting to server http://{} ...'.format(server))
    
    try:
        sio.connect('http://{}'.format(server),  namespaces=['/cam'])
        print('my sid is', sio.sid)
        global is_connected
        is_connected=True
        print("is_connected", is_connected)
    except:
        print('* Could not connect')
        
    time.sleep(1)

def send_data(frame, text, position):
    #frame = cv2.resize(frame, (640, 480))
    sio.emit(
            'cam2server',
            {
                'image': convert_image_to_jpeg(frame),
                'text': text,
                'pos': position
            })

def convert_image_to_jpeg(image):
    # Encode frame as jpeg
    frame = cv2.imencode('.jpg', image)[1].tobytes()

    # Encode frame in base64 representation and remove utf-8 encoding
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)


def convert_b64jpeg_to_image(b64jpeg):

    # Decode base64 string in bytes
    img_bytes = base64.b64decode(b64jpeg)
  
    # Convert in np array 
    jpg_as_np = np.frombuffer(img_bytes, dtype=np.uint8)

    # Decode into cv2 image
    return cv2.imdecode(jpg_as_np, flags=1) 



if __name__ == "__main__":

    topic = os.getenv("TOPIC", default="distributed-video1")
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVER", default="localhost:9092")
    security_protocol = os.getenv("SECURITY_PROTOCOL", default="PLAINTEXT")
    ssl_check_hostname = bool(os.getenv("SSL_CHECK_HOSTNAME", default="FALSE"))
    ssl_cafile = os.getenv("SSL_CAFILE", default="./ca.crt")

    ui_server = os.getenv("UI_SERVER", default="localhost:8088")

    if not is_connected:
        connect_server(ui_server)

    try:
        consumer = KafkaConsumer(topic, 
            value_deserializer=msgpack.unpackb,
            bootstrap_servers=[bootstrap_servers],
            security_protocol=security_protocol,
            ssl_check_hostname=ssl_check_hostname,
            max_partition_fetch_bytes=5048576,
            ssl_cafile=ssl_cafile)

    except Exception as e:
        sio.disconnect()
        print(str(e))
        sys.exit('Could not connect to Kafka:' + bootstrap_servers)



    print("Consume ...")
    print("BOOTSTRAP_SERVER:" + bootstrap_servers)
    print("TOPIC:" + topic)

    push_bad = False

    for msg in consumer:
        data = json.loads(msg.value)

        frame = convert_b64jpeg_to_image(data['frame'].split(',')[1])

        print(data['time'] + " " + str(frame.shape))

        if not is_connected:
            connect_server(ui_server)


        #
        # Add here the AI/ML CV Logic ....
        #
        
        postion = 0
        
        
        if 'label' in data:
        
            if data['label'] == "good":
                postion = 0
                color = (0, 255, 0 ) # #BGR
            else:
                postion = 1
                color = (0, 0, 255 ) # #BGR

        
            font = cv2.FONT_HERSHEY_SIMPLEX
            stroke = 1
            cv2.putText(frame, data['label'], (10, 240), font, 0.5, color, stroke, cv2.LINE_AA)

            send_data(frame, data['time'], postion)
        else:

            send_data(frame, data['time'], 0)





