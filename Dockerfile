FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt /app
RUN apk add --virtual=.build-deps musl-dev gcc libffi-dev libev-dev make && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY . /app

RUN ln -s /app/simpleupdate/generate_token.py /usr/local/bin/generate_token.py
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD gunicorn simpleupdate:app -k gevent --worker-connections=1000 -b 0.0.0.0:80
