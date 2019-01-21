#!/usr/bin/env bash

docker build . -t sample-service
docker run -e MODE='' \
           --rm -p 8080:8080 sample-service:latest