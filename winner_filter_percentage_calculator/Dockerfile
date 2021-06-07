FROM python:3.8
RUN pip3 install pika

COPY winner_filter_percentage_calculator /
CMD [ "python", "./main.py" ]