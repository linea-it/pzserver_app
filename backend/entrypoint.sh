#!/bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

# Para produção é necessário usar o uWSGI!
# uWSGI para servir o app e ter compatibilidade com Shibboleth
# https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html
# TODO: Em produção não é recomendado o auto reload. utilizar uma variavel de ambiente para ligar ou desligar esta opção.
uwsgi \
    --socket 0.0.0.0:8000 \
    --wsgi-file /app/pzserver/wsgi.py \
    --module pzserver.wsgi:application \
    --buffer-size=32768 \
    --processes=4 \
    --threads=2 \
    --static-map /django_static=/app/django_static \
    --py-autoreload=1 
    # --static-map /django_static/rest_framework=/app/static/rest_framework \

    

