FROM python:3.8
RUN pip3 install pika

COPY calculators/top_civilizations /
COPY common /
CMD [ "python", "./main.py" ]