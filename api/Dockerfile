FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1


WORKDIR /app
COPY ./app/requirements.txt /app/requirements.txt

RUN set -eux \
    && apk update \
    && apk add --no-cache build-base curl ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt \
    && apk del build-base \
    && rm -rf /root/.cache/pip

COPY ./app /