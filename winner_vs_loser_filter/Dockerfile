FROM python:3.8
RUN pip3 install pika

COPY winner_vs_loser_filter /
COPY common /
CMD [ "python", "./main.py" ]