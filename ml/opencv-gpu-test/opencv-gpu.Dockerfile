FROM datamachines/cudnn_tensorflow_opencv:10.2_2.2.0_4.3.0-20200615

RUN mkdir -p /wrk/darknet \
    && cd /wrk \
    && wget -q -c https://github.com/AlexeyAB/darknet/archive/darknet_yolo_v4_pre.tar.gz -O - | tar --strip-components=1 -xz -C /wrk/darknet \
    && cd darknet \
    && perl -i.bak -pe 's%^(GPU|CUDNN|OPENCV|OPENMP|LIBSO)=0%$1=1%g;s%(compute\_61\])%$1 -gencode arch=compute_75,code=[sm_75,compute_75]%' Makefile \
    && make

WORKDIR /wrk/darknet

RUN pip3 install pyyolo==0.1.5
ENV LIB_DARKNET=/wrk/darknet/libdarknet.so


CMD /bin/bash

