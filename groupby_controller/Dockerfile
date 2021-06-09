FROM python:3.8
RUN pip3 install pika

COPY groupby_controller /
COPY common /
CMD [ "python", "./main.py" ]