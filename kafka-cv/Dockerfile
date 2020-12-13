FROM registry.access.redhat.com/ubi8/ubi
MAINTAINER Stefan Bergstein stefan.bergstein@gmail.com
RUN yum install -y python3; yum clean all
RUN python3 -m pip install --upgrade pip

COPY *.py /app/
COPY requirements.txt /app/

WORKDIR /app
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["consumer.py"]