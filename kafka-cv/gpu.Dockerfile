FROM tensorflow/tensorflow:2.3.0-gpu

RUN mkdir /app
COPY ./ /app/

WORKDIR /app

RUN python3 -m pip install -r requirements-gpu.txt \
    && curl -LO https://github.com/stefan-bergstein/computer-vision-streaming-playground/releases/download/v0.1-alpha-tf/tf-model.tar \
    && tar xvf tf-model.tar --no-same-owner && rm -f tf-model.tar

User 1001

ENTRYPOINT ["python3"]
CMD ["consumer.py"]

