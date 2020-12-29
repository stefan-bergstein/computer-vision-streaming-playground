

#
# Create images with bounding boxes and lables for all test and traning data
#
#


from darknetyolo import DarknetYolo

import cv2
import os
import time

from pathlib import Path

#
# Global vars
#



path_data = '../darknet/data/'
path_yolo = '../darknet/data/metal_yolo/'
path_pred = '../data/pred-test/'

yolo_config_file = '../yolo-cfg/yolov4-custom-metal-test.cfg'
weights_file = '../data/weights/yolov4-custom-metal_final.weights'
class_file = f"{path_yolo}classes.txt"


Path(os.path.dirname(path_pred)).mkdir(parents=True, exist_ok=True)

my_darknet = DarknetYolo(yolo_config_file=yolo_config_file, class_file=class_file, 
                    weights_file=weights_file)



#
# Loop through all files and predict bounding boxes
#

for file in os.listdir(path_yolo):
    if file.endswith("png") or file.endswith("jpg"):

        # Read image
        image_in = cv2.imread(f"{path_yolo}{file}")

        detected_classes, image_pred = my_darknet.predict(image_in)

        print(f"{file}:{detected_classes}")
        # Write image to file
        cv2.imwrite(f"{path_pred}{file}", image_pred)



