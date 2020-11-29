# Computer-vision streaming playground

What is in the playground?


## As of 29.11.2020

### web-ui - A simple SocketIO Flask app 
- Shows images in a very basic html page 
- Listens to web-sockets for new images
- Push images to the web client 

### kafka-cv - Reads messages from kafka and pushes images to the web-ui
- Read messages from a kafka topic
- Optionally, mock logic for "good" images
- Push images to the web-ui

### cam - read images from a camera, screen or files
- cam.py 
  - Read images from the local camera or a part of your screen
  - Optionally, try some face detection
  - Send image via web-socket to web-ui
- camk.py
  - Read images from the local camera or from files
  - Write images to a kafka topic

## Try it ....

### Use case 1 - Stream web cam to web page
todo - describe

### Use case 2 - Stream image via kafka and classify images 
todo - describe


