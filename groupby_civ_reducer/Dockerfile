FROM python:3.8
RUN pip3 install pika

COPY groupby_civ_reducer /
COPY common /
CMD [ "python", "./main.py" ]