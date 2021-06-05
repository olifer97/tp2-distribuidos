FROM python:3.8
RUN pip3 install pika

COPY map_no_mirror_filter /
CMD [ "python", "./main.py" ]