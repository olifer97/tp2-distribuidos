FROM python:3.8
RUN pip3 install pika

COPY filters/map_no_mirror_filter /
COPY common /
CMD [ "python", "./main.py" ]