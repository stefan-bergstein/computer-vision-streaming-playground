

#
# Create images with bounding boxes and lables for all test and traning data
#
#


import cv2
import os
import time

from pathlib import Path

import sys

# insert at position 1 in the path, as 0 is the path of this file.
sys.path.insert(1, '../../kafka-cv/')

from tensorflowyolo import TensorflowYolo


#
# Global vars
#

path_data = '../darknet/data/'
path_yolo = '../darknet/data/metal_yolo/'
path_pred = '../data/pred-tf/'

tfmodel_path = '../data/tf-model/'
class_file = f"{path_yolo}classes.txt"

Path(os.path.dirname(path_pred)).mkdir(parents=True, exist_ok=True)

my_tf = TensorflowYolo(tfmodel_path=tfmodel_path)


#
# Loop through all files and predict bounding boxes
#

for file in os.listdir(path_yolo):
    if file.endswith("png") or file.endswith("jpg"):

        # Read image
        image_in = cv2.imread(f"{path_yolo}{file}")

        detected_classes, image_pred = my_tf.predict(image_in)

        print(f"{file}:{detected_classes}")
        # Write image to file
        cv2.imwrite(f"{path_pred}{file}", image_pred)

