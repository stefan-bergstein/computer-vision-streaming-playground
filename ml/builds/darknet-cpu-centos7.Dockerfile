FROM centos:centos7
RUN yum group install "Development Tools" -y
RUN yum install -y git zip && yum clean all

RUN git clone https://github.com/AlexeyAB/darknet.git && cd darknet \
    && sed -i 's/AVX=0/AVX=1/' Makefile \
    && sed -i 's/OPENMP=0/OPENMP=1/' Makefile \
    && make

USER 1001