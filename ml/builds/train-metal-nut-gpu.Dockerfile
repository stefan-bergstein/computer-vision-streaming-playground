FROM image-registry.openshift-image-registry.svc:5000/sbergste-opencv2/darknet-gpu
MAINTAINER Stefan Bergstein stefan.bergstein@gmail.com

RUN yum install -y zip && yum clean all

