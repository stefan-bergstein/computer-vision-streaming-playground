import sys
import time
import cv2
import os
import argparse
import json
import msgpack
import datetime
import numpy as np

from mss import mss
from PIL import Image
import pickle

from kafka import KafkaProducer
from random import shuffle
import base64
import socketio
import logging

from find_faces import faces
from detect_objects import objects

#
# Globals
#
web_server=None

# Logging
module = sys.modules['__main__'].__file__
logger = logging.getLogger(module)

# Kafka
send_kafka = False
producer = None
topic = None
cam_id = 0

#
# Sending message via web sockets
#
global is_connected
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
    #connect_server(web_server)


def connect_server(server):
    print('* Connecting to server {} ...'.format(server))
    global is_connected
    
    while not is_connected:
        try:
            sio.connect(server,  namespaces=['/cam'])
            print('my sid is', sio.sid)
            is_connected=True
            print("is_connected", is_connected)
        except:
            print('* Could not connect')
            
        time.sleep(2)


#
# Send message via web socket or kafka
#

def send_msg(msg):
    if send_kafka:
        producer.send(topic, msg)
    else:
        if is_connected:
            sio.emit('cam2server', msg, namespace='/cam' )
    return

#
# Convert image frame to base64 jpeg
#

def convert_image_to_jpeg(image):
    # Encode frame as jpeg
    frame = cv2.imencode('.jpg', image)[1].tobytes()
    # Encode frame in base64 representation and remove utf-8 encoding
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)


def scale_frame(frame, scale):
    # Scale frame
    frameHeight, frameWidth = frame.shape[:2]
    frameWidth = int(frameWidth * scale)
    frameHeight = int(frameHeight * scale)
    return cv2.resize(frame, (frameWidth, frameHeight))

#
# Capture local screen
#

def capture_screen(box, fps, scale, detect_faces, detect_objects):
    logger.info("Capture local screen ...")

    # Area to capture from screen
    screen_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

    if box and len(box) == 4:
        screen_box['top'] = args.box[0]
        screen_box['left'] = args.box[1]
        screen_box['width'] = args.box[2]
        screen_box['height'] = args.box[3]

    # Get sct
    sct = mss()

    # Faces
    if detect_faces:
        logger.info("Detect Faces")
        f = faces()

    # Objects
    if detect_objects:
        logger.info("Detect Objects")
        o = objects()


    last_update_time = time.time()
    wait_time = (1/fps)

    while True:
        try:

            # Empty Message 
            msg = {     
                "image": "empty",   
                "id": cam_id,
                "type": "screen",
                "time": "empty",
                "text": "empty"
            }   
            
            # Grab frame from screen

            im = np.array(sct.grab(screen_box))

            frame = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

            msg['text'] ="Screen: " + str(screen_box)

            cur_time = time.time()
            if cur_time - last_update_time > wait_time:

                # Faces
                if detect_faces:
                    frame = f.find(frame)

                # Objects
                if detect_objects:
                    frame = o.detect(frame)
                    

                # Scale frame
                frame = scale_frame(frame, scale)
                
                msg['time'] = str(datetime.datetime.now())
                msg['image'] = convert_image_to_jpeg(frame)

                send_msg(msg)

                logger.info("Message sent: %s - %s", msg['time'], str(frame.shape))
                last_update_time =  cur_time
            else:
                time.sleep(wait_time)

        except Exception as e: 
                logger.error(str(e))
                time.sleep(2)

    return

#
# Read image files from disk
#

def find_images(path):
    # Find images on disk

    image_list = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("png") or file.endswith("jpg"):
                image_meta =  {"label": "good", "path": "data/0.png" }
                ipath = os.path.join(root, file)
                label = os.path.basename(root).replace(" ", "-").lower()
                image_meta["label"] = label
                image_meta["path"] = ipath
                image_list.append(image_meta)
    return image_list


def read_imagefiles(path, fps, scale):
    logger.info("Read image files from disk ...")

    wait_time = (1/fps)

    # Get image list ans shuffle
    image_list = find_images(path)
    shuffle(image_list)


    i=0
    while True:
        # Empty Message 
        msg = {     
            "image": "empty",   
            "id": cam_id,
            "type": "image",
            "time": "empty",
            "text": "empty",
            "label": "empty"                
        }   

            
        # Read image from disk
        logger.info(f"Imagae {i}: {image_list[i]}" )

        image_meta = image_list[i]           
        pil_image = Image.open(image_meta["path"]) 
        frame = np.array(pil_image, "uint8")
        msg['label'] = image_meta["label"]
        
        i = i + 1
        if i == len(image_list):
            i = 0

        # Scale frame
        frame = scale_frame(frame, scale)


        msg['time'] = str(datetime.datetime.now())
        msg['text'] = msg['time']
        msg['image'] = convert_image_to_jpeg(frame)

        send_msg(msg)

        logger.info("Message sent: " +topic + " - " + msg['time'] + " - " + str(frame.shape))

        time.sleep(wait_time)

    return

#
# Capture local camera
#

def capture_cam(camera, fps, scale, detect_faces, detect_objects):
    logger.info("Capture local camera ...")
    
    # Open cam
    cap = cv2.VideoCapture(camera)
    if cap.isOpened():
        logger.info("Opened cam: %d", camera)
    else:
        logger.error("Could not opened cam: %d", camera)
        exit(1)



    # Faces
    if detect_faces:
        logger.info("Detect Faces")
        f = faces()

    # Objects
    if detect_objects:
        logger.info("Detect Objects")
        o = objects()

    last_update_time = time.time()
    wait_time = (1/fps)

 
    while True:

        try:

            # Empty Message 
            msg = {     
                "image": "empty",   
                "id": cam_id,
                "type": "cam",
                "time": "empty",
                "text": "empty"
            }    
            
            # Read frame from camera
            success, frame = cap.read()

            cur_time = time.time()
            if cur_time - last_update_time > wait_time:

                # Faces
                if detect_faces:
                    frame = f.find(frame)

                # Objects
                if detect_objects:
                    frame = o.detect(frame)

                # Scale frame
                frame = scale_frame(frame, scale)

                msg['time'] = str(datetime.datetime.now())
                msg['text'] = msg['time']
                msg['image'] = convert_image_to_jpeg(frame)

                send_msg(msg)

                logger.info("Message sent: %s - %s", msg['time'], str(frame.shape))
                last_update_time =  cur_time
            else:
                time.sleep(wait_time)

        except Exception as e: 
    
            logger.error(str(e))
            time.sleep(2)

        
    return

def connect_kafka(bootstrap_servers, security_protocol, ssl_check_hostname, ssl_cafile):

    logger.info(f"Connect to kafka bootstrap_servers: {bootstrap_servers} " )
    logger.info(f"- security_protocol: {security_protocol}")
    logger.info(f"- ssl_check_hostname: {ssl_check_hostname}")
    logger.info(f"- ssl_cafile: {ssl_cafile}")

    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
        value_serializer=lambda m: json.dumps(m).encode('utf-8'),
        security_protocol=security_protocol,
        ssl_check_hostname=ssl_check_hostname,
        batch_size=0,
        linger_ms=10,
        max_request_size=5048576,
        ssl_cafile=ssl_cafile)

    return producer



if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='Video Streamer Client')


    # Camera settings

    parser.add_argument(
            '--camera', type=int, default='0',
            help='Webcam index')

    parser.add_argument(
            '--scale',  type=float, default=1.0,
            help='Scale camera or screen. Default 1.0')

    # Screen capture settings

    parser.add_argument(
            '--screen',  action="store_true",
            help='Capture screen instead of using camera')

    parser.add_argument('--box', nargs='+', type=int,
            help='Screen box: top left width height')


    # Web socket server settings

    parser.add_argument(
            '--web',  action="store_true",
            help='Use web sockets for sending images [default: False]')

    parser.add_argument(
            '--server',  type=str, default='http://localhost:8088',
            help='Image receiver address (web socket server) [default: http://localhost:8088]')


    # Kafka settingsFalse

    parser.add_argument(
            '--topic',  type=str, default='distributed-video1',
            help='Kafka topic [default: distributed-video1]')

    parser.add_argument(
            '--bootstrap',  type=str, default='localhost:9092',
            help='Kafka bootstrap servers [default: localhost:9092]')

    parser.add_argument(
            '--ssl',  action="store_true",
            help='Use SSL for Kafka [default: no ssl]')

    parser.add_argument(
            '--check_hostname',  action="store_true",
            help='SSL check hostname for Kafka [default: false]')    

    parser.add_argument(
            '--cafile',  type=str, default='./ca.crt',
            help='SSL CA file for for Kafka [default: ./ca.crt]')

            
    # Face detection 

    parser.add_argument(
            '--faces',  action="store_true",
            help='Detect faces')

    # Object detection 

    parser.add_argument(
            '--objects',  action="store_true",
            help='Detect objects')

    # Stream images settings 

    parser.add_argument(
            '--images',  action="store_true",
            help='Stream images')

    parser.add_argument(
            '--path',  type=str, default='data',
            help='Path of the image directory')

    parser.add_argument(
            '--fps',  type=float, default=10.0,
            help='Frames per second')    

    parser.add_argument(
            '--camid', type=str, default='0',
            help='ID number for the simulated camera')
    
    parser.add_argument('-l', '--log-level', default='WARNING',
                                help='Set log level to ERROR, WARNING, INFO or DEBUG')

    args = parser.parse_args()

   
    #
    # Configure logging
    #

    try:
        logging.basicConfig(stream=sys.stderr, level=args.log_level, format='%(name)s (%(levelname)s): %(message)s')
    except ValueError:
        logger.error("Invalid log level: {}".format(args.log_level))
        sys.exit(1)

    logger.info("Log level set: {}"
                .format(logging.getLevelName(logger.getEffectiveLevel())))

    #
    # Kafka setting via env vars
    #

    topic = os.getenv("TOPIC", default=args.topic)
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVER", default=args.bootstrap)
    security_protocol = os.getenv("SECURITY_PROTOCOL", default="PLAINTEXT")
    ssl_check_hostname = bool(os.getenv("SSL_CHECK_HOSTNAME", default="FALSE").lower() == 'true') or args.check_hostname

    ssl_cafile = os.getenv("SSL_CAFILE", default=args.cafile)

    # ID number for the simulated camera
    cam_id = int(os.getenv("CAMID", default=args.camid))

    #
    # Connect to target either to web socket or kafka
    #

    web_server = args.server

    if args.web:
        send_kafka = False
    else:
        send_kafka = True

    if send_kafka:

        topic = args.topic
        
        if security_protocol == "PLAINTEXT":
            if args.ssl:
                security_protocol="SSL"
            else:
                security_protocol="PLAINTEXT"

        # To-Do: Add exception handling and retries
        producer = connect_kafka(bootstrap_servers, security_protocol, ssl_check_hostname, ssl_cafile)

    else:
        connect_server(web_server)

    #
    # Start the work ...
    #
     
    if args.screen:
        capture_screen(args.box, args.fps, args.scale, args.faces, args.objects)
    elif args.images:
        read_imagefiles(args.path, args.fps, args.scale)
    else:
        capture_cam(args.camera, args.fps, args.scale, args.faces, args.objects)


