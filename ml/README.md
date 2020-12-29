# Model training for the Metal Nut Data Set
## Metal Nut Data Set
- Credits to https://www.mvtec.com/company/research/datasets
- See also: https://www.mvtec.com/company/research/datasets/mvtec-ad

### ATTRIBUTION
Paul Bergmann, Michael Fauser, David Sattlegger, Carsten Steger. MVTec AD - A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection; in: IEEE Conference on Computer Vision and Pattern Recognition (CVPR), June 2019

### LICENSE
The data is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0). For using the data in a way that falls under the commercial use clause of the license, please contact us via the form below.

# Convert  Data Set to Darknet Yolo format

## Prerequisites

Metal Nut Data Set is downloaded on you computer in `computer-vision-streaming-playground/ml/data`. E.g.:

```
cd ml/data

curl -u guest:GU.205dldo ftp://ftp.softronics.ch/mvtec_anomaly_detection/metal_nut.tar.xz -o metal_nut.tar.xz

tar xf metal_nut.tar.xz && rm -f metal_nut.tar.xz

ls -1d metal_nut/*
metal_nut/ground_truth
metal_nut/license.txt
metal_nut/readme.txt
metal_nut/test
metal_nut/train
```


## Create Yolo files

TO-DO: Add description

Switch to `computer-vision-streaming-playground/ml/scripts` and run `generate_yolo_conf.py` 

```
python generate_yolo_conf.py
```

# Training on OpenShift
TO-DO: Add description

## Copy darknet conf


Switch to `computer-vision-streaming-playground/yolo-cfg` and copy files 

```
cd ../yolo-cfg
cp metal-data.data ../darknet/data/metal-data.data
cp yolov4-custom-metal-ocp.cfg ../darknet/data/yolov4-custom-metal.cfg

```

## zip images and annotation, push to git

```
cd ../darknet/
zip -r data.zip data
git add data.zip
git commit -m "new data.zip"
git push
```

## Run training on OpenShift

TO-DO: Add description

# Build Darknet image (GPU)

```
oc apply -f manifests/darknet-gpu-is.yaml
oc apply -f manifests/darknet-gpu-bc.yaml
```

# Run Training

```
oc apply -f manifests/darknet-gpu-pvc.yaml
oc apply -f manifests/darknet-metal-gpu-job.yaml
```

Note, trained weights are stored on a persistance volume `darknet-gpu-volume`, but you need to copy/save it to your computer manually.

# Training on Colab

## Copy darknet conf

Switch to `computer-vision-streaming-playground/yolo-cfg` and copy files 

```
cd ../yolo-cfg
cp metal-data-colab.data ../darknet/data/metal-data.data
cp yolov4-custom-metal.cfg ../darknet/data/yolov4-custom-metal.cfg

```

## zip images and annotation for easier upload

```
cd ../darknet/
zip -r data.zip data
```

## Run training on Colab

Upload `ml/notebooks/Metal_Nut_YOLOv4_Colab.ipynb` to your [Colab Account](https://colab.research.google.com/).
Run the notebook using a GPU.


# Check Model Mean Average Precision (mAP) manually

If you didn't run the training with the '-map- flag added then you can still find out the mAP of your model after training. Run the following command on any of the saved weights from the training to see the mAP value for that specific weight's file. 
Note, you have to install darknet on your computer first.

```
cd darknet
```

**1000.weights**:
```
darknet detector map data/metal_data_ocp.data data/yolov4-custom-metal.cfg ../data/weights/yolov4-custom-metal_1000.weights

class_id = 0, name = scratch, ap = 100.00%       (TP = 1, FP = 3) 
class_id = 1, name = bent, ap = 88.33%           (TP = 6, FP = 3) 

 for conf_thresh = 0.25, precision = 0.54, recall = 1.00, F1-score = 0.70 
 for conf_thresh = 0.25, TP = 7, FP = 6, FN = 0, average IoU = 36.56 % 

 IoU threshold = 50 %, used Area-Under-Curve for each unique Recall 
 mean average precision (mAP@0.50) = 0.941667, or 94.17 % 
```


**2000.weights**:
```
darknet detector map data/metal_data_ocp.data data/yolov4-custom-metal.cfg ../data/weights/yolov4-custom-metal_2000.weights

class_id = 0, name = scratch, ap = 100.00%       (TP = 1, FP = 3) 
class_id = 1, name = bent, ap = 100.00%          (TP = 6, FP = 0) 

 for conf_thresh = 0.25, precision = 0.70, recall = 1.00, F1-score = 0.82 
 for conf_thresh = 0.25, TP = 7, FP = 3, FN = 0, average IoU = 56.24 % 

 IoU threshold = 50 %, used Area-Under-Curve for each unique Recall 
 mean average precision (mAP@0.50) = 1.000000, or 100.00 % 
```

**final.weights**:
```
darknet detector map data/metal_data_ocp.data data/yolov4-custom-metal.cfg ../data/weights/yolov4-custom-metal_final.weights

class_id = 0, name = scratch, ap = 100.00%       (TP = 1, FP = 1) 
class_id = 1, name = bent, ap = 100.00%          (TP = 6, FP = 0) 

 for conf_thresh = 0.25, precision = 0.88, recall = 1.00, F1-score = 0.93 
 for conf_thresh = 0.25, TP = 7, FP = 1, FN = 0, average IoU = 71.37 % 

 IoU threshold = 50 %, used Area-Under-Curve for each unique Recall 
 mean average precision (mAP@0.50) = 1.000000, or 100.00 % 
 ```