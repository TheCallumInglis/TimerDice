FROM ubuntu:22.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /app

RUN pip3 install pika && \
    pip3 install flask

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]