FROM alpine:3.20
USER root
RUN apk update && apk add python3 && apk add --update py-pip && apk add firefox && apk add postgresql-dev && apk add gcc && apk add python3-dev && apk add musl-dev
RUN adduser -S --disabled-password -h /home/api -s /bin/sh api
USER api
COPY requirements.txt /home/api
RUN mkdir /home/api/api_code
RUN python3 -m venv /home/api/.venv
RUN /home/api/.venv/bin/pip install --no-cache-dir -r /home/api/requirements.txt
RUN rm /home/api/requirements.txt