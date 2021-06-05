FROM python:3.8
RUN pip3 install pika

COPY players_clone_rating_filter /
CMD [ "python", "./main.py" ]