FROM nvcr.io/nvidia/cuda:10.2-cudnn8-devel-centos8
MAINTAINER Stefan Bergstein stefan.bergstein@gmail.com

RUN yum install -y python3 git cmake; yum clean all
RUN python3 -m pip install --upgrade pip



RUN mkdir /tmp/ocv-build 
WORKDIR /tmp/ocv-build 

RUN git clone https://github.com/opencv/opencv
RUN git clone https://github.com/opencv/opencv_contrib

RUN mkdir /tmp/ocv-build/build && cd /tmp/ocv-build/build
RUN cmake -DOPENCV_EXTRA_MODULES_PATH=/tmp/ocv-build/opencv_contrib/modules  -DBUILD_SHARED_LIBS=OFF  -DBUILD_TESTS=OFF  -DBUILD_PERF_TESTS=OFF -DBUILD_EXAMPLES=OFF -DWITH_OPENEXR=OFF -DWITH_CUDA=ON -DWITH_CUBLAS=ON -DWITH_CUDNN=ON -DOPENCV_DNN_CUDA=ON /tmp/ocv-build
RUN make -j4 install


