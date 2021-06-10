FROM python:3.8
RUN pip3 install pika

COPY map_no_mirror_filter /
COPY common /
CMD [ "python", "./main.py" ]