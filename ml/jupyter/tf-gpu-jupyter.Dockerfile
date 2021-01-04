FROM tensorflow/tensorflow:2.3.0-gpu

RUN apt-get update && apt-get install -y git

RUN mkdir /app && chmod 777 /app
ENV HOME=/app
WORKDIR /app

RUN python3 -m pip install jupyterlab

USER 1001

EXPOSE 8888

ENTRYPOINT ["jupyter-lab"]
CMD ["--ServerApp.open_browser=False", "--ServerApp.ip='*'",  "--ServerApp.allow_remote_access=True","--ServerApp.token=''", "--ServerApp.password='sha1:73f5d45705db:caf77270e9558cc4aee82d75782921cf6aba521b'"]

# password=secret