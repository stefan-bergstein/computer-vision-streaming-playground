
import os
import sys

from kafka import KafkaConsumer
import json
import msgpack
import numpy as np
import cv2
import base64
import time
import socketio

# Predict using Darknet
from darknetyolo import DarknetYolo

# Predict using Tensorflow
from tensorflowyolo import TensorflowYolo

is_connected=False

sio = socketio.Client(logger=False,reconnection=True,reconnection_attempts=0)

@sio.event
def connect():
    print('* Successfully connected to server.')


@sio.event
def disconnect():
    print('* Disconnected from server.')
    global is_connected
    is_connected=False


def connect_server(server):
    print('* Connecting to server http://{} ...'.format(server))
    
    try:
        sio.connect('http://{}'.format(server),  namespaces=['/kcv'])
        print('my sid is', sio.sid)
        global is_connected
        is_connected=True
        print("is_connected", is_connected)
    except:
        print('* Could not connect')
        
    time.sleep(1)

def send_data(frame, text, cam_id, status):
    #frame = cv2.resize(frame, (640, 480))
    sio.emit(
            'kcv2server',
            {
                'image': convert_image_to_jpeg(frame),
                'text': text,
                'id': cam_id,
                'status': status
            }, namespace='/kcv')

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
    ssl_check_hostname = bool(os.getenv("SSL_CHECK_HOSTNAME", default="FALSE").lower() == 'true')


    ssl_cafile = os.getenv("SSL_CAFILE", default="./ca.crt")

    ui_server = os.getenv("UI_SERVER", default="localhost:8088")

    # Yolo conf

    yolo_config_file = os.getenv("YOLO_CFG_FILE", default="./yolov4.cfg")
    weights_file = os.getenv("YOLO_WEIGHTS_FILE", default="./yolov4.weigths")
    class_file = os.getenv("YOLO_CLASS_FILE", default="./classes.txt")
    tfmodel_path = os.getenv("TF_MODEL_PATH", default="./tf-model")

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
        print("KafkaConsumer: ", str(e))
        sys.exit('Could not connect to Kafka:' + bootstrap_servers)
    
    print("BOOTSTRAP_SERVER:" + bootstrap_servers)
    print("TOPIC:" + topic)


    tf = True # FWIW, TF can be used use GPU and CPU, but lets keep the darknet code

    if tf:
        # Configure TF based Yolo neural network ...
        print("Configure TF based Yolo neural network ...")
        my_tf = TensorflowYolo(tfmodel_path=tfmodel_path)

    else:
        # Configure darknet based Yolo neural network
        print("Configure darknet based Yolo neural network ...")
        my_darknet = DarknetYolo(yolo_config_file=yolo_config_file, class_file=class_file, 
                            weights_file=weights_file)


    push_bad = False

    print("Consume ...")
    for msg in consumer:
        data = json.loads(msg.value)

        frame = convert_b64jpeg_to_image(data['image'].split(',')[1])

        print(data['time'] + " " + str(frame.shape))

        if not is_connected:
            connect_server(ui_server)

        # check / set cam ID
        cam_id = 0
        if 'id' in data:
            cam_id = data['id']

        #
        # Add here the AI/ML CV Logic ....
        #

        status = 0
        predict = True
        
        if 'label' in data:
        
            if predict:
                start = time.time()

                if tf:
                    detected_classes, image_pred = my_tf.predict(frame)
                else:
                    detected_classes, image_pred = my_darknet.predict(frame)

                end = time.time()
                print('Predict: Total object detection took {:.5f} seconds'.format(end - start))

                if detected_classes:
                    print(detected_classes)
                    status = 1

                send_data(image_pred, data['time'], cam_id, status)

            else:
                #  Simulation only. No Prediction

                if data['label'] == "good":
                    status = 0
                    color = (0, 255, 0 ) # #BGR
                else:
                    status = 1
                    color = (0, 0, 255 ) # #BGR

                font = cv2.FONT_HERSHEY_SIMPLEX
                stroke = 1
                frameHeight, frameWidth = frame.shape[:2]
                cv2.putText(frame, data['label'], (10, frameHeight - 10 ), font, 0.5, color, stroke, cv2.LINE_AA)
                send_data(frame, data['time'], cam_id, status)

        else:
            send_data(frame, data['time'], cam_id, 0)





