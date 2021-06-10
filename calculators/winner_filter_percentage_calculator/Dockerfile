FROM python:3.8
RUN pip3 install pika

COPY calculators/winner_filter_percentage_calculator /
COPY common /
CMD [ "python", "./main.py" ]