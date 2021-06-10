FROM python:3.8
RUN pip3 install pika

COPY joiner /
COPY common /
CMD [ "python", "./main.py" ]