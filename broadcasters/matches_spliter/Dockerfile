FROM python:3.8
RUN pip3 install pika

COPY broadcasters/matches_spliter /
COPY common /
CMD [ "python", "./main.py" ]