#!/bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

umask g+w

# Para produção é necessário usar o uWSGI!
# https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html
uwsgi \
    --socket 0.0.0.0:8000 \
    --wsgi-file /app/pzserver/wsgi.py \
    --module pzserver.wsgi:application \
    --buffer-size=32768 \
    --processes=1 \
    --threads=1 \
    --static-map /django_static=/app/django_static \
    --py-autoreload=${AUTORELOAD:-0}