#!/usr/bin/env sh

export ENV="${ENV:=web}"  # web, ws, beat, task, dev or test.
export WORKERS="${WORKERS:=1}"
export WORKER_CONNECTIONS="${WORKER_CONNECTIONS:=100}"
export TASK_QUEUES="${TASK_QUEUES:=}"  # Example: q1, q2, q3.
export TASK_EXCLUDE_QUEUES="${TASK_EXCLUDE_QUEUES:=}"  # Example: q1, q2, q3.
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gcp.json"

echo $GCP_B64_CREDENTIALS | base64 -d >$GOOGLE_APPLICATION_CREDENTIALS

. /venv/bin/activate

echo $ENV | grep -q "web\|ws\|beat\|task\|dev" && \
    su -p app -c "python manage.py migrate" &

rm -r /etc/nginx
cp -r .docker/app/nginx /etc/nginx

[ -n "$TASK_QUEUES" ] && \
    TASK_ARGS="--queues ${TASK_QUEUES// /}"

[ -n "$TASK_EXCLUDE_QUEUES" ] && \
    TASK_ARGS="--exclude-queues ${TASK_EXCLUDE_QUEUES// /}"

echo $ENV | grep -q "web" && \
    cp .docker/app/nginx/web.conf /etc/nginx/app.conf

echo $ENV | grep -q "dev" && \
    cp .docker/app/nginx/dev.conf /etc/nginx/app.conf

echo $ENV | grep -q "ws" && \
    cp .docker/app/nginx/ws.conf /etc/nginx/app.conf

sed -e "s~WORKERS~$WORKERS~g" \
    -e "s~WORKER_CONNECTIONS~$(($WORKER_CONNECTIONS * 2))~g" \
    -i /etc/nginx/nginx.conf

echo $ENV | grep -q "web\|ws\|dev" && nginx

echo $ENV | grep -q "beat" && \
    exec celery --app conf beat --uid app --gid app --loglevel INFO

echo $ENV | grep -q "task" && \
    USE_GEVENT="True" exec celery --app conf worker \
        --without-gossip --without-mingle --without-heartbeat \
        --events --pool gevent --concurrency $WORKER_CONNECTIONS \
        --uid app --gid app --loglevel INFO $TASK_ARGS

echo $ENV | grep -q "web\|dev" && \
    su -p app -c "
        for x in \`seq 10\`
        do
            sleep 1s
            wget --spider -o /tmp/wget.log \
                http://127.0.0.1:2000/health-check && break
        done
    " &

echo $ENV | grep -q "web" && exec uwsgi --ini uwsgi.ini

echo $ENV | grep -q "dev" && \
    exec uwsgi --ini .docker/dev/uwsgi.ini --py-autoreload 1

echo $ENV | grep -q "ws" && \
    exec su -p app -c "
        exec uvicorn conf.channels_asgi:application \
            --interface asgi3 --loop uvloop --http httptools --ws websockets \
            --workers $WORKERS --limit-concurrency $WORKER_CONNECTIONS \
            --host 127.0.0.1 --port 2000 --log-level info \
            --lifespan off --no-server-header --ws-max-size 204800  # 200KB
    "

echo $ENV | grep -q "test" && \
    exec su -p app -c "
        python manage.py test --settings tests.settings --keepdb -v2 \
            tests.apps \
            tests.apis.gql \
            tests.apis.pi
    "

exit 0
