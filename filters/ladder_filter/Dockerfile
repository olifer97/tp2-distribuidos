FROM python:3.8
RUN pip3 install pika

COPY filters/ladder_filter /
COPY common /
CMD [ "python", "./main.py" ]