FROM python:3.9.1-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /app/src/
COPY requirements.txt ./
RUN mkdir -p /app/src/static && pip install --no-cache-dir -r requirements.txt
COPY src/ .

EXPOSE 8000
