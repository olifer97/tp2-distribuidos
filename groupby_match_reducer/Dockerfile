FROM python:3.8
RUN pip3 install pika

COPY groupby_match_reducer /
CMD [ "python", "./main.py" ]