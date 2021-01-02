
#FROM datamachines/cudnn_tensorflow_opencv:10.2_2.2.0_4.3.0-20200615 # mish error

#FROM datamachines/cudnn_tensorflow_opencv:10.2_2.3.1_4.5.0-20201204


FROM datamachines/cudnn_tensorflow_opencv:10.2_2.3.0_4.4.0-20200803

#RUN mkdir -p /wrk/darknet \
#    && cd /wrk \
#    && wget -q -c https://github.com/AlexeyAB/darknet/archive/darknet_yolo_v4_pre.tar.gz -O - | tar --strip-components=1 -xz -C /wrk/darknet \
#    && cd darknet \
#    && perl -i.bak -pe 's%^(GPU|CUDNN|OPENCV|OPENMP|LIBSO)=0%$1=1%g;s%(compute\_61\])%$1 -gencode arch=compute_35,code=[sm_35,compute_35]%' Makefile \
#    && make

RUN mkdir -p /wrk/darknet \
    && cd /wrk \
    && wget -q -c https://github.com/AlexeyAB/darknet/archive/darknet_yolo_v4_pre.tar.gz -O - | tar --strip-components=1 -xz -C /wrk/darknet \
    && cd darknet \
    && sed -i 's/GPU=0/GPU=1/' Makefile \
    && sed -i 's/CUDNN=0/CUDNN=1/' Makefile \
    && sed -i 's/OPENCV=0/OPENCV=1/' Makefile \
    && sed -i 's/OPENMP=0/OPENMP=1/' Makefile \
    && sed -i 's/CUDNN_HALF=0/CUDNN_HALF=1/' Makefile \
    && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
    && make


WORKDIR /wrk/darknet

ENV LIB_DARKNET=/wrk/darknet/libdarknet.so


