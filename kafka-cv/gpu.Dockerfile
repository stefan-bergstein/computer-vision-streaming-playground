
FROM quay.io/sbergste/darknet-opencv-gpu:latest

COPY *.py /wrk/darknet
COPY requirements-gpu.txt /wrk/darknet

WORKDIR /wrk/darknet

RUN python3 -m pip install -r requirements-gpu.txt \
    && curl -LO https://github.com/stefan-bergstein/computer-vision-streaming-playground/releases/download/v0.1-alpha/model.tar \
    && tar xvf model.tar --no-same-owner && rm -f model.tar

User 1001

ENTRYPOINT ["python3"]
CMD ["consumer.py"]

