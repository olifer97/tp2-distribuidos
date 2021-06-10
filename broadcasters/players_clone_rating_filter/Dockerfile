FROM python:3.8
RUN pip3 install pika

COPY broadcasters/players_clone_rating_filter /
COPY common /
CMD [ "python", "./main.py" ]