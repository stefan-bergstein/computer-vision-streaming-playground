# Computer-vision streaming playground

What is in the playground?

### frontend - A simple SocketIO Flask app 
- Shows images in a very basic html page 
- Listens to web-sockets for new images
- Push images to the web client 

### kafka-cv - Reads messages from kafka and pushes images to the frontend
- Read messages from a kafka topic
- Optionally, mock logic for "good" images
- Push images to the frontend

### cam - read images from a camera, screen or files
- client.py 
  - Read images from the local camera, a part of your screen or from files
  - Optionally, try some face detection 
  - Send image via web-socket to frontend, or
  - Write images to a kafka topic

## Try it locally ...

### Use case 1 - Stream web cam to web page

Client sends web cam images via web sockets to the server.
Server sends images to the browser.

**Start the frontend backend:**
```
cd frontend
```
Install requirement in a venv:
```
python3 -m venv venv 
source venv/bin/activate
pip3 install -r requirements.txt
```

Start the frontend:
```
python3 app.py
```

**Open Browser**

http://localhost:8088/cam/ 

**Stream your webcam**
```
cd cam
```

Install requirement in a venv:
```
python3 -m venv venv 
source venv/bin/activate
pip3 install -r requirements.txt
```
```
python client.py --web
```


### Use case 2 - Stream image via kafka and classify images 

**Start a local Kafka server**

See [ Start the Kafka server](
https://kafka.apache.org/25/documentation/streams/quickstart#quickstart_streams_startserver)

**Start the frontend backend:**
```
cd frontend
python app.py
```

**Open Browser**

http://localhost:8088/ 


**Kafka receiver incl. visual inspection**
```
cd kafka-cv
python3 -m venv venv 
source venv/bin/activate
pip3 install -r requirements.txt
```

*Set env vars for ML based visual inspection*

Below are 'outdated'the settings for the darknet based ML. Let's skip and used the TF model.
```
export YOLO_CFG_FILE='../ml/yolo-cfg/yolov4-custom-metal-test.cfg'
export YOLO_WEIGHTS_FILE='../ml/data/weights/yolov4-custom-metal_final.weights'
export YOLO_CLASS_FILE='../ml/darknet/data/metal_yolo/classes.txt'
```

*Tensorflow settings:*

This assumes the TF model is saved in  `ml/data/tf-model/`. In case you don't have a TF model, you can download it here:

```
   cd ../ml/data/
   curl -LO https://github.com/stefan-bergstein/computer-vision-streaming-playground/releases/download/v0.1-alpha-tf/tf-model.tar
   tar xvf tf-model.tar --no-same-owner && rm -f tf-model.tar
```

Set the `TF_MODEL_PATH` env var:
```
export TF_MODEL_PATH=../ml/data/tf-model/
```

We need the `classes.txt` in the `kafka-cv` directory:
```
cd ../../kafka-cv
ln -s ../ml/darknet/data/metal_yolo/classes.txt
```

or create local file in `kafka-cv`:
```
cd ../../kafka-cv
cat << EOF > classes.txt
scratch
bent
EOF
```

*Start the kafka receiver:*
```
python3 consumer.py
```

**Stream images**

- Read images from `./data/`
- 2 frames per second
- Scale image by 0.5

```
cd cam
python client.py --images --fps 2 --scale 0.5
```

Note, in case you stream large images via Kafka, please ensure proper [Kafka configurations.](https://stackoverflow.com/questions/51767879/not-able-to-send-large-messages-to-kafka)



## Deploy the playground on OpenShift

**Prerequisites:**
- OpenShift ~4.5+
- This repo is cloned on your computer
- Red Hat Integration - AMQ Streams Operator is installed
   
### Build Container images
Build the frontend and kafka-cv container in your namespace:

```
cd manifests

oc apply -f frontend-is.yaml
oc apply -f frontend-bc.yaml

oc apply -f kafka-cv-is.yaml
oc apply -f kafka-cv-bc.yaml
```

Verify that the builds completed successfully.

### Configure Kafka

Prerequisite: Red Hat Integration - AMQ Streams Operator is installed in your namespace

Create Kafka instance:
```
oc apply -f kafka-cluster.yaml
```

Wait for kafka installation to be completed.

Either,
`watch oc get pods`
and look for `kafka-cluster-entity-operator-....`

or,

```
oc wait --for=condition=ready pod -l  strimzi.io/name=kafka-cluster-entity-operator
```
### Deploy the pod and create a service and route

Pod:
```
oc apply -f kafka-cv-conf.yaml
oc apply -f deployment.yaml 
```

Service and route
```
oc apply -f cv-streaming-service.yaml
oc apply -f cv-streaming-route.yaml
```
### Get cert.ca to access Kafka externally

```
cd ../envs
oc extract secret/kafka-cluster-cluster-ca-cert --keys=ca.crt --to=- > ca.crt 
```

### Get the correct route host
```
oc get routes kafka-cluster-kafka-bootstrap -o=jsonpath='{.status.ingress[0].host}{"\n"}'
```
Sample output:
```
kafka-cluster-kafka-bootstrap-sbergste-opencv2.apps.ocp4.stormshift.coe.muc.redhat.com
```
Update BOOTSTRAP_SERVER in ocp-env.sh using your favorite editor.

### Play with the use cases


**Install modules**
```
pip install -r requirements.txt
```

*Please let me know if any module is missing

**Stream your webcam via web-sockets**

Open Browser: `http://<cv-streaming-route>/`

Start the webcam streamer:
```
python client.py --web --server <cv-streaming-route>:80 --fps 1
```


**Stream your webcam via kafka**

Open Browser: `http://<cv-streaming-route>/`

Start the webcam streamer:

```
python client.py -l INFO  --fps 1  --scale 1 --bootstrap <kafka-bootstrap:443> --ssl --cafile ../envs/ca.crt
```

**Stream your screen, detect faces and send via kafka**

```
python client.py -l INFO  --fps 1  --scale 0.5 --screen --faces --bootstrap  <kafka-bootstrap:443> --ssl --cafile ../envs/ca.crt
```


**Stream metal nut images via kafka**

http://cv-streaming-sbergste-opencv2.apps.ocp4.stormshift.coe.muc.redhat.com/

```
python client.py -l INFO  --fps 0.5  --scale 0.5 --images --bootstrap <kafka-bootstrap:443> --ssl --cafile ../envs/ca.crt
```