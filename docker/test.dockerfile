FROM python:3.8-slim-buster

LABEL purpose="Integration tests for Ariadne GraphQL app"
LABEL maintainer="schweringmarc01@gmail.com"

EXPOSE 8000

COPY . /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    pip install -r tests/requirements.txt
