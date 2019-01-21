#!/usr/local/bin/dumb-init /bin/sh


if [[ "$MODE" = 'eu-production' ]]; then
    echo "Running in prod"
    # DB
    aws s3 cp db.password

    export DJANGO_SETTINGS_MODULE='project.settings.prod'

elif [[ "$MODE" = 'eu-staging' ]]; then
    echo "Running in staging"
    # DB
    aws s3 cp db.password

    export DJANGO_SETTINGS_MODULE='project.settings.staging'

else
    echo "Running in dev"
    export DJANGO_SETTINGS_MODULE='project.settings.dev'
fi

python manage.py migrate

python manage.py loaddata dev

echo Starting Gunicorn.
gunicorn project.wsgi -c gunicorn_conf.py -k gevent --name sample-service --bind :8080 --workers 3 --access-logfile "-" --error-logfile "-"
