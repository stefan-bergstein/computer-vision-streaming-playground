import cv2

class objects():

    def __init__(self):
        self.thres = 0.65 # Threshold to detect object

        self.classNames= []
        classFile = 'objects/coco.names'
        with open(classFile,'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

        configPath = 'objects/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weightsPath = 'objects/frozen_inference_graph.pb'

        self.net = cv2.dnn_DetectionModel(weightsPath,configPath)
        self.net.setInputSize(320,320)
        self.net.setInputScale(1.0/ 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)


    def detect(self, frame):
        classIds, confs, bbox = self.net.detect(frame, confThreshold=self.thres)
        #print(classIds,bbox)

        if len(classIds) != 0:
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                cv2.rectangle(frame,box,color=(0,255,0),thickness=2)
                cv2.putText(frame,self.classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                cv2.putText(frame,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

        return frame