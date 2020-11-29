import time
import argparse
import socketio
import cv2
import base64
import os
import pickle
import numpy as np
from mss import mss
from PIL import Image


is_connected=False

screen_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
#screen_box = {'top': 0, 'left': 0, 'width': 640, 'height': 480}

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

def send_data(frame, text):
    frame = cv2.resize(frame, (640, 480))
    sio.emit(
            'cam2server',
            {
                'image': convert_image_to_jpeg(frame),
                'text': text
            })

def convert_image_to_jpeg(image):
    # Encode frame as jpeg
    frame = cv2.imencode('.jpg', image)[1].tobytes()
    # Encode frame in base64 representation and remove utf-8 encoding
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)


def main(camera, server, fps, find_faces, screen):


    if find_faces:
        f = os.path.dirname(cv2.__file__) +  '/data/haarcascade_frontalface_alt2.xml'
        print("* CascadeClassifier:", f)
        face_cascade = cv2.CascadeClassifier(f)

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("./trainer.yml")

        labels = {"person_name": 1}
        with open("labels.pickle", 'rb') as f:
            og_labels = pickle.load(f)
            labels = {v:k for k,v in og_labels.items()}


    if not screen:
        cap = cv2.VideoCapture(camera)
        if cap.isOpened():
            print("* Opened cam", camera)
        else:
            print("* Could not opened cam", camera)
            exit(1)
    else:
        sct = mss()


    last_update_time = time.time()
    wait_time = (1/fps)


    while True:

        if not is_connected:
            connect_server(server)

        if not screen:
            success, frame = cap.read()
            text="Cam: " + str(camera)
        else:
            frame = np.array(sct.grab(screen_box))
            text="Screen: " + str(screen_box)

        if find_faces:
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

            for (x, y, w, h) in faces:
                #print(x,y,w,h)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                id_, conf = recognizer.predict(roi_gray)
                print(conf, labels[id_])
                if conf >= 50 and conf <= 100:
                    #print(id_)
                    #print(labels[id_])
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    name = labels[id_]
                    color = (255, 0, 0) #BGR
                    stroke = 1
                    cv2.putText(frame, name, (x,y+h+20), font, 0.5, color, stroke, cv2.LINE_AA)

                color = (255, 0, 0)  #BGR
                stroke = 1
                end_cord_x = x + w
                end_cord_y = y + h
                cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke )

    
        cur_time = time.time()

        if cur_time - last_update_time > wait_time:
            send_data(frame, text)
            last_update_time =  cur_time
        else:
            time.sleep(0.01)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cam Streamer')
    parser.add_argument(
            '--camera', type=int, default='0',
            help='Camera index')

    parser.add_argument('--box', nargs='+', type=int,
            help='Screen box: top left width height')

    parser.add_argument(
            '--screen',  action="store_true",
            help='Capture screen instead of using camera')

    parser.add_argument(
            '--server',  type=str, default='localhost:8088',
            help='The IP address or hostname and port of the server (localhost:8088).')

    parser.add_argument(
            '--fps',  type=float, default=10.0,
            help='Frames per second')

    parser.add_argument(
            '--faces',  action="store_true",
            help='Detect faces')

    parser.add_argument("--log", action="store_true", help="increase output verbosity")

    
    args = parser.parse_args()
    


    if args.screen and args.box and len(args.box) == 4:
        print(args.screen)
        print(len(args.screen))
        
        screen_box['top'] = args.box[0]
        screen_box['left'] = args.box[1]
        screen_box['width'] = args.box[2]
        screen_box['height'] = args.box[3]


    print(screen_box)


    main(args.camera, args.server, args.fps, args.faces, args.screen)
