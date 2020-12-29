#
# Create images with bounding boxes and lables for all test and traning data
#
#

import cv2
import os
import time
import numpy as np
from pathlib import Path

#
# Global vars
#

path_data = '../darknet/data/'
path_yolo = '../darknet/data/metal_yolo/'
path_pred = '../data/pred/'
weights_file = '../data/weights/yolov4-custom-metal_best.weights'

random_colors = False

Path(os.path.dirname(path_pred)).mkdir(parents=True, exist_ok=True)


#
# Load the YOLO network
#

# Read class lables 
with open(f"{path_yolo}classes.txt") as f:
    # Getting labels reading every line
    labels = [line.strip() for line in f]

# Read Yolo network
network = cv2.dnn.readNetFromDarknet(f"{path_data}yolov4-custom-metal-test.cfg", weights_file)

# Get list with names of all layers from the YOLO network
layers_names_all = network.getLayerNames()


# Get the YOLO output layer names
layers_names_output = \
    [layers_names_all[i[0] - 1] for i in network.getUnconnectedOutLayers()]

# Set minimum probability to eliminate weak predictions
probability_minimum = 0.5

# Set threshold for filtering weak bounding boxes with non-maximum suppression
threshold = 0.3

# Generate colors for representing every detected object
# with function randint(low, high=None, size=None, dtype='l')
if random_colors:
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')
else:
    colors = array = np.array([[0,255,0] for _ in range(len(labels))])



for file in os.listdir(path_yolo):
    if file.endswith("png") or file.endswith("jpg"):

        # Read image
        image_BGR = cv2.imread(f"{path_yolo}{file}")

        # Get dimension of the input image
        h, w = image_BGR.shape[:2]  # Slicing from tuple only first two elements

        # Create blob from the input image.
        # The 'cv2.dnn.blobFromImage' function returns 4-dimensional blob
        # from the image after mean subtraction, normalizing, and RB channels swapping.
        blob = cv2.dnn.blobFromImage(image_BGR, 1 / 255.0, (416, 416),
                                    swapRB=True, crop=False)


        # Implementing forward pass with the blob and only through the output layers
        # Calculating at the same time, needed time for forward pass
        network.setInput(blob)  # setting blob as input to the network
        start = time.time()
        output_from_network = network.forward(layers_names_output)
        end = time.time()

        # Showing spent time for forward pass
        print('Object detection took {:.5f} seconds'.format(end - start))

        # Retrieve bounding boxes

        # lists for detected bounding boxes, obtained confidences and class numbers
        bounding_boxes = []
        confidences = []
        class_numbers = []

        # Loop through all output layers after feed forward pass
        for result in output_from_network:
            # Loop through all detections from current output layer
            for detected_objects in result:
                # Get all class probabilities for current detected object
                scores = detected_objects[5:]
                # Get index of the class with the maximum value of probability
                class_current = np.argmax(scores)
                # Getting value of probability for defined class
                confidence_current = scores[class_current]

                # Eliminating weak predictions with minimum probability
                if confidence_current > probability_minimum:
                    # Scaling bounding box coordinates to the initial image size
                    # YOLO data format keeps coordinates for center of bounding box and its current width and height
                    # That is why we can just multiply them elementwise to the width and height
                    # of the original image and in this way get coordinates for center
                    # of bounding box, its width and height for original image
                    box_current = detected_objects[0:4] * np.array([w, h, w, h])

                    # Now, from the YOLO data format, we can get top left corner coordinates
                    # that are x_min and y_min
                    x_center, y_center, box_width, box_height = box_current
                    x_min = int(x_center - (box_width / 2))
                    y_min = int(y_center - (box_height / 2))

                    # Adding results into prepared lists
                    bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                    confidences.append(float(confidence_current))
                    class_numbers.append(class_current)

        # Implementing non-maximum suppression of given bounding boxes
        # With this technique we exclude some of bounding boxes if their
        # corresponding confidences are low or there is another
        # bounding box for this region with higher confidence

        # It is needed to make sure that data type of the boxes is 'int'
        # and data type of the confidences is 'float'
        # https://github.com/opencv/opencv/issues/12789
        results = cv2.dnn.NMSBoxes(bounding_boxes, confidences,
                                probability_minimum, threshold)


        #
        # Draw bounding boxes and labels
        #

        # Counter for the detected objects
        counter = 1

        # Checking if there is at least one detected object after non-maximum suppression
        if len(results) > 0:
            # Loop through indexes of results
            for i in results.flatten():
                # Showing labels of the detected objects
                print('Object {0}: {1}'.format(counter, labels[int(class_numbers[i])]))

                # Incrementing counter
                counter += 1

                # Get current bounding box coordinates
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]

                # Set the  color for current bounding box and convert from numpy array to list
                colour_box_current = colors[class_numbers[i]].tolist()

                # Draw bounding box on the original image
                cv2.rectangle(image_BGR, (x_min, y_min),
                            (x_min + box_width, y_min + box_height),
                            colour_box_current, 2)

                # Set text with label and confidence for current bounding box
                text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])],
                                                    confidences[i])

                # Putting text with label and confidence on the original image
                cv2.putText(image_BGR, text_box_current, (x_min, y_min - 5),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, colour_box_current, 2)
                
                
        # Write image to file
        cv2.imwrite(f"{path_pred}{file}", image_BGR)
