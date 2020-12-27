FROM cuda:10.1-cudnn7-devel-ubi7
MAINTAINER Stefan Bergstein stefan.bergstein@gmail.com

RUN yum install -y git zip && yum clean all

RUN git clone https://github.com/AlexeyAB/darknet.git && cd darknet \
    && sed -i 's/GPU=0/GPU=1/' Makefile \
    && sed -i 's/CUDNN=0/CUDNN=1/' Makefile \
    && sed -i 's/CUDNN_HALF=0/CUDNN_HALF=1/' Makefile \
    && make
