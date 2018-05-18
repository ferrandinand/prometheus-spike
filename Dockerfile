FROM python:3.6

WORKDIR /app

RUN pip install prometheus_client
COPY . /app

EXPOSE 8000 8001

ENTRYPOINT python server.py
