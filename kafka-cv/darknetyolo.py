import cv2
import numpy as np
import time

class DarknetYolo():


    def __init__(self, yolo_config_file="yolov4.cfg", class_file="classes.txt", 
                    weights_file="yolov4.weigths", random_colors=False,
                    probability_minimum=0.5, threshold = 0.5):

        self.random_colors = random_colors
        self.probability_minimum = probability_minimum
        self.threshold = threshold

        #
        # Load the YOLO network
        #

        # Read class lables 
        with open(class_file) as f:
            # Get labels reading every line
            self.labels = [line.strip() for line in f]

        # Read Yolo network
        self.network = cv2.dnn.readNetFromDarknet(yolo_config_file, weights_file)

        # Get list with names of all layers from the YOLO network
        layers_names_all = self.network.getLayerNames()


        # Get the YOLO output layer names
        self.layers_names_output = [layers_names_all[i[0] - 1] for i in self.network.getUnconnectedOutLayers()]

        # Generate colors for representing every detected object
        # with function randint(low, high=None, size=None, dtype='l')
        if random_colors:
            self.colors = np.random.randint(0, 255, size=(len(self.labels), 3), dtype='uint8')
        else:
            self.colors = array = np.array([[0,255,0] for _ in range(len(self.labels))])





    def predict(self, in_image):

        # Get dimension of the input image
        h, w = in_image.shape[:2]  # Slicing from tuple only first two elements

        # Create blob from the input image.
        # The 'cv2.dnn.blobFromImage' function returns 4-dimensional blob
        # from the image after mean subtraction, normalizing, and RB channels swapping.
        blob = cv2.dnn.blobFromImage(in_image, 1 / 255.0, (416, 416),
                                    swapRB=True, crop=False)


        # Implementing forward pass with the blob and only through the output layers
        # Calculating at the same time, needed time for forward pass
        self.network.setInput(blob)  # setting blob as input to the network
        start = time.time()
        output_from_network = self.network.forward(self.layers_names_output)
        end = time.time()

        # Showing spent time for forward pass
        print('network.forward: Object detection took {:.5f} seconds'.format(end - start))

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
                if confidence_current > self.probability_minimum:
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
                                self.probability_minimum, self.threshold)


        #
        # Draw bounding boxes and labels
        #

        # Counter for the detected objects
        counter = 1

        detected_classes = []
        # Checking if there is at least one detected object after non-maximum suppression
        if len(results) > 0:
            # Loop through indexes of results
            for i in results.flatten():
                # Showing labels of the detected objects
                #print('Object {0}: {1}'.format(counter, self.labels[int(class_numbers[i])]))

                # Incrementing counter
                counter += 1

                # Get current bounding box coordinates
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]

                # Set the  color for current bounding box and convert from numpy array to list
                colour_box_current = self.colors[class_numbers[i]].tolist()

                # Draw bounding box on the original image
                cv2.rectangle(in_image, (x_min, y_min),
                            (x_min + box_width, y_min + box_height),
                            colour_box_current, 2)

                # Set text with label and confidence for current bounding box
                text_box_current = '{}: {:.3f}'.format(self.labels[int(class_numbers[i])],
                                                    confidences[i])
                
                detected_classes.append(text_box_current)

                # Putting text with label and confidence on the original image
                cv2.putText(in_image, text_box_current, (x_min, y_min - 5),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, colour_box_current, 2)
      
        return detected_classes, in_image



