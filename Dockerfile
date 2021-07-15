# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN ls -ls
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "api.py"]