FROM alpine:3.19.1 AS build

COPY . /app
WORKDIR /app

RUN apk update --no-cache \
    && apk add --no-cache build-base linux-headers \
        python3 nginx libpq \
        python3-dev jpeg-dev zlib-dev musl-dev libffi-dev \
        openssl-dev libpq-dev \
    && python -m venv /venv \
    && . /venv/bin/activate \
    && pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir \
        -r requirements/base.freeze.txt \
        -r requirements/db.freeze.txt \
        -r requirements/server.freeze.txt \
        -r requirements/ws.freeze.txt \
    && python manage.py collectstatic --no-input \
    && addgroup app \
    && adduser -s /bin/sh -D -G app app \
    && chown -R app:app /venv /app \
        /run/nginx /var/lib/nginx /var/log/nginx \
    && chmod 755 /root \
    && apk del build-base linux-headers \
        python3-dev jpeg-dev zlib-dev musl-dev libffi-dev \
        openssl-dev libpq-dev \
    && rm -rf /root/.cache /usr/local/share/.cache

FROM alpine:3.19.1 AS final

COPY --from=build / /
WORKDIR /app

EXPOSE 80

CMD ["sh", "init.sh"]
