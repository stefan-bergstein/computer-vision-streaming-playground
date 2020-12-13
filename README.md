# Computer-vision streaming playground

What is in the playground?


## As of 13.12.2020

### frontend - A simple SocketIO Flask app 
- Shows images in a very basic html page 
- Listens to web-sockets for new images
- Push images to the web client 

### kafka-cv - Reads messages from kafka and pushes images to the frontend
- Read messages from a kafka topic
- Optionally, mock logic for "good" images
- Push images to the frontend

### cam - read images from a camera, screen or files
- cam.py 
  - Read images from the local camera or a part of your screen
  - Optionally, try some face detection
  - Send image via web-socket to frontend
- camk.py
  - Read images from the local camera or from files
  - Write images to a kafka topic

## Try it locally ...

### Use case 1 - Stream web cam to web page
**Start the frontend backend:**
```
cd frontend
python app.py
```

**Open Browser**

http://localhost:8088/ 

**Stream your webcam**
```
cd cam
python cam.py 
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


**Start the kafka receiver:**
```
cd kafka-cv
python consumer.py
```

**Stream images**
```
cd cam
python camk.py --images --fps 2
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

### Get Get the correct route host
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


**Set env vars for Kafka SSL communication**
```
cd ../cam
. ../envs/ocp-env.sh
export SSL_CAFILE=../envs/ca.crt
```

**Stream your webcam via web-sockets**

Open Browser: http://<cv-streaming-route>/

```
python cam.py --server <cv-streaming-route>:80 --fps 1
```


**Stream your webcam via kafka**

Open Browser: http://<cv-streaming-route>/

```
python camk.py --fps 1
```


