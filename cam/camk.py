import sys
import time
import cv2
import os
import argparse
import json
import msgpack
import datetime
import numpy as np
from PIL import Image
from kafka import KafkaProducer
from random import shuffle




    
def find_images(path):
    """
    Find images on disk
    """

    image_list = []
    

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("png") or file.endswith("jpg"):
                image_meta =  {"label": "good", "path": "data/0.png" }
                ipath = os.path.join(root, file)
                label = os.path.basename(root).replace(" ", "-").lower()
                image_meta["label"] = label
                image_meta["path"] = ipath
                # print(label, ipath)
                image_list.append(image_meta)
    return image_list




def cam_to_kafka(camera, fps, image_list, scale):
    """
    Send cam video stream to specified Kafka topic.
    """

    producer = KafkaProducer(value_serializer=msgpack.dumps,
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,ssl_check_hostname=ssl_check_hostname,
        max_request_size=5048576,
        ssl_cafile=ssl_cafile)





    if not image_list:
        cap = cv2.VideoCapture(camera)
        if cap.isOpened():
            print("* Opened cam", camera)
        else:
            print("* Could not opened cam", camera)
            exit(1)

        

    last_update_time = time.time()
    wait_time = (1/fps)

    try:
        i=0
        while True:
            msg = {     
                "frame": [],   
                "id": "empty"
            }   
            
            if not image_list:
                # Read frame from camera
                success, frame = cap.read()
                frameWidth = int(320 * scale)
                frameHeight = int(240 * scale)
                #frameWidth = 160
                #frameHeight = 120
                
            else:
                # Read image from disk
                print(i, image_list[i])
                image_meta = image_list[i]
                frameWidth = 250
                frameHeight = 250            
                pil_image = Image.open(image_meta["path"]) # grayscale
                frame = np.array(pil_image, "uint8")
                msg['label'] = image_meta["label"]
                
                i = i + 1
                if i == len(image_list):
                    i = 0

            cur_time = time.time()

            if cur_time - last_update_time > wait_time:

                frame = cv2.resize(frame, (frameWidth, frameHeight))

                msg['time'] = str(datetime.datetime.now())
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                msg['frame'] = frame.tolist()
                #msg['frame'] = gray.tolist()
                j=json.dumps(msg)
                print(len(j))

                producer.send(topic, json.dumps(msg))
                print("Message sent: " +topic + " - " + msg['time'] + " - " + str(gray.shape))
                last_update_time =  cur_time
            else:
                if not image_list:
                    pass
                else:
                    time.sleep(wait_time)


    except Exception as e: 
  
        print(str(e) + "\nExiting.")
        sys.exit(1)

    
    cap.release()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Kafka Cam Streamer')
    parser.add_argument(
            '--camera', type=int, default='0',
            help='Camera index')
    parser.add_argument(
            '--server',  type=str, default='localhost:9092',
            help='The IP address or hostname and port of the server (localhost:9092).')
    parser.add_argument(
            '--fps',  type=float, default=10.0,
            help='Frames per second')

    parser.add_argument(
            '--scale',  type=float, default=1.0,
            help='Scale cam. Default 1.0 = 320x240')


    parser.add_argument(
            '--images',  action="store_true",
            help='Stream images')

    parser.add_argument(
            '--path',  type=str, default='data',
            help='Path of the image directory')

    args = parser.parse_args()


    topic = os.getenv("TOPIC", default= "distributed-video1")
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVER", default="localhost:9092")
    security_protocol = os.getenv("SECURITY_PROTOCOL", default="PLAINTEXT")
    ssl_check_hostname = bool(os.getenv("SSL_CHECK_HOSTNAME", default="FALSE"))
    ssl_cafile = os.getenv("SSL_CAFILE", default="./ca.crt")

    image_list = []
    
    if args.images:    
        image_list = find_images(args.path)
        print(len(image_list))
        shuffle(image_list)




    cam_to_kafka(args.camera, args.fps, image_list, args.scale)

