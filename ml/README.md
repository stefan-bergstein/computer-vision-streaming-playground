# Convert mvtec.com Metal Nut Data Set to Darknet Yolo format

## Metal Nut Data Set
- Credits to https://www.mvtec.com/company/research/datasets
- See also: https://www.mvtec.com/company/research/datasets/mvtec-ad

### ATTRIBUTION
Paul Bergmann, Michael Fauser, David Sattlegger, Carsten Steger. MVTec AD - A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection; in: IEEE Conference on Computer Vision and Pattern Recognition (CVPR), June 2019

### LICENSE
The data is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0). For using the data in a way that falls under the commercial use clause of the license, please contact us via the form below.


# Convert data

Concepts:
- TODO: describe flow

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


Switch to `computer-vision-streaming-playground/ml/scripts` and run `generate_yolo_conf.py` 

```
python generate_yolo_conf.py
```


## zip images and annotation for easier upload

```
cd ../darknet/
zip -r data.zip data
```

