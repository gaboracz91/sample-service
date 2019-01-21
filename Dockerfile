FROM python:3-alpine

WORKDIR /app

RUN mkdir multiproc-tmp

RUN apk add --update postgresql-libs postgresql-dev python3-dev gcc musl-dev

RUN sed -i -e 's/v3\.4/edge/g' /etc/apk/repositories \
    && apk upgrade --update-cache --available \
    && apk add --no-cache librdkafka librdkafka-dev

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV prometheus_multiproc_dir=/app/multiproc-tmp

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/dumb-init", "/app/entrypoint.sh"]