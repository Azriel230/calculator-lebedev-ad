FROM python:3.13-alpine

WORKDIR /app

ENV DBPASSWORD=$DBPASSWORD
ENV DBUSER=$DBUSER
ENV DBNAME=$DBNAME
ENV DBHOST=$DBHOST
ENV DBPORT=$DBPORT
ENV SERVERHOST=$SERVERHOST
ENV SERVERPORT=$SERVERPORT

COPY ./src/ /app

RUN set -ex && \
    apk add --no-cache gcc musl-dev

RUN mkdir /build; gcc /app/main.c -o /build/app.exe

RUN python -m venv /app/venv; \
    . venv/bin/activate; \
    pip install --upgrade pip; \
    pip install structlog "fastapi[standard]" psycopg2-binary

RUN set -ex && \
    rm -f /usr/libexec/gcc/x86_64-alpine-linux-musl/6.4.0/cc1obj && \
    rm -f /usr/libexec/gcc/x86_64-alpine-linux-musl/6.4.0/lto1 && \
    rm -f /usr/libexec/gcc/x86_64-alpine-linux-musl/6.4.0/lto-wrapper && \
    rm -f /usr/bin/x86_64-alpine-linux-musl-gcj

RUN rm /app/gui.py

EXPOSE 8888

EXPOSE 8080

EXPOSE 65432

CMD . venv/bin/activate; cd /app/server/; uvicorn server:app --port 8080

