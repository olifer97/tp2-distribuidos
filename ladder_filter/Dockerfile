FROM python:3.8
RUN pip3 install pika

COPY ladder_filter /
COPY common /
CMD [ "python", "./main.py" ]