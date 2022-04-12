#!/bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn pzserver.wsgi:application --bind 0.0.0.0:8000 --reload

# TODO: Para produção é necessário usar o uWSGI!
# uWSGI para servir o app e ter compatibilidade com Shibboleth
# https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html
# TODO: Em produção não é recomendado o auto reload. utilizar uma variavel de ambiente para ligar ou desligar esta opção.
# uwsgi \
#     --socket 0.0.0.0:8000 \
#     # --wsgi-file /app/pzserver/wsgi.py \    
#     # --static-map /django_static/admin=/app/static/admin \
#     # --static-map /django_static/rest_framework=/app/static/rest_framework \    
#     --module pzserver.wsgi:application \
#     --buffer-size=32768 \
#     --processes=4 \
#     --threads=2 \
#     --py-autoreload=1 

    

