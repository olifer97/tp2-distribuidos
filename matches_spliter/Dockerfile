FROM python:3.8
RUN pip3 install pika

COPY matches_spliter /
COPY common /
CMD [ "python", "./main.py" ]