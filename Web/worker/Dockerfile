FROM ubuntu:22.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

RUN pip3 install pika && \
    pip3 install xmltodict && \
    pip3 install SQLAlchemy && \
    pip3 install psycopg2-binary && \
    pip3 install flask

WORKDIR /app

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]