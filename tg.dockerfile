
FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY /tg_bot /tgbot

COPY requirements_tg.txt /tgbot
RUN apt-get update && \
    apt-get install -y build-essential libzbar-dev && \
    apt-get install zbar-tools
RUN pip install --no-cache-dir -r /tgbot/requirements_tg.txt
RUN apt-get install ffmpeg libsm6 libxext6  -y