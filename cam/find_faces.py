import os
import cv2
import pickle

class faces():

    def __init__(self):
        f = os.path.dirname(cv2.__file__) +  '/data/haarcascade_frontalface_alt2.xml'
        # print("* CascadeClassifier:", f)
        self.face_cascade = cv2.CascadeClassifier(f)

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read("./trainer.yml")

        self.labels = {"person_name": 1}
        with open("labels.pickle", 'rb') as f:
            og_labels = pickle.load(f)
            self.labels = {v:k for k,v in og_labels.items()}

    def find(self, frame):

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_list = self.face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

        for (x, y, w, h) in face_list:
            #print(x,y,w,h)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            id_, conf = self.recognizer.predict(roi_gray)

            # print(conf, labels[id_])
            if conf >= 50 and conf <= 100:
                font = cv2.FONT_HERSHEY_DUPLEX
                name = self.labels[id_]

                color = (255, 0, 0)  #BGR
                stroke = 1
                end_cord_x = x + w
                end_cord_y = y + h
                cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke )
                cv2.rectangle(frame, (x, end_cord_y + 20 ), (end_cord_x, end_cord_y), color, cv2.FILLED )
                cv2.putText(frame, name, (x + 6, end_cord_y + 16), font, 0.5, (255,255,255), stroke, cv2.LINE_AA)

        return frame