FROM registry.access.redhat.com/ubi8/ubi
MAINTAINER Stefan Bergstein stefan.bergstein@gmail.com
RUN yum install -y python3; yum clean all
RUN python3 -m pip install --upgrade pip

COPY *.py /app/
COPY requirements.txt /app/

WORKDIR /app
RUN python3 -m pip install -r requirements.txt
RUN curl -LO https://github.com/stefan-bergstein/computer-vision-streaming-playground/releases/download/v0.1-alpha/model.tar
RUN tar xvf model.tar && rm -f model.tar

ENTRYPOINT ["python3"]
CMD ["consumer.py"]