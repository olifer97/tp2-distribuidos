FROM python:3.8
RUN pip3 install pika

COPY filters/servers_avg_rating_duration /
COPY common /
CMD [ "python", "./main.py" ]